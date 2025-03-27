import logging
import shutil
import subprocess

from pathlib import Path
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from scalar_fastapi import get_scalar_api_reference

from math_rag_apptainer.enums import BuildStatus
from math_rag_apptainer.requests import (
    BuildClearRequest,
    BuildResultRequest,
    OverlayCreateRequest,
)
from math_rag_apptainer.trackers import BuildStatusTracker


app = FastAPI()

DEF_DIR = Path('files/defs')
SIF_DIR = Path('files/sifs')
IMG_DIR = Path('files/imgs')

DEF_DIR.mkdir(parents=True, exist_ok=True)
SIF_DIR.mkdir(parents=True, exist_ok=True)
IMG_DIR.mkdir(parents=True, exist_ok=True)

build_status_tracker = BuildStatusTracker()


def build_background_task(task_id: str, def_path: Path, sif_path: Path) -> None:
    build_status_tracker.set_status(task_id, BuildStatus.RUNNING)
    args = ['apptainer', 'build', str(sif_path), str(def_path)]

    try:
        subprocess.run(args, check=True, capture_output=True, text=True)
        build_status_tracker.set_status(task_id, BuildStatus.DONE)

    except subprocess.CalledProcessError as e:
        logging.error(f'Apptainer build {task_id} failed: {e.stderr}')
        build_status_tracker.set_status(task_id, BuildStatus.FAILED)


def overlay_create_background_task(
    task_id: str, fakeroot: bool, size: int, img_path: Path
) -> None:
    args = ['apptainer', 'overlay', 'create']

    if fakeroot:
        args.append('--fakeroot')

    args.extend(['--size', str(size), img_path])

    try:
        subprocess.run(args, check=True, capture_output=True, text=True)

    except subprocess.CalledProcessError as e:
        logging.error(f'Apptainer overlay create {task_id} failed: {e.stderr}')


@app.post('/apptainer/build"')
async def build(
    background_tasks: BackgroundTasks, def_file: UploadFile = File(...)
) -> dict[str, str]:
    if not def_file.filename.endswith('.def'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Only .def files are accepted',
        )

    task_id = str(uuid4())
    build_status_tracker.set_status(task_id, BuildStatus.PENDING)
    def_path = DEF_DIR / f'{task_id}.def'
    sif_path = SIF_DIR / f'{task_id}.sif'

    with def_path.open('wb') as buffer:
        shutil.copyfileobj(def_file.file, buffer)

    background_tasks.add_task(build_background_task, task_id, def_path, sif_path)

    return {'task_id': task_id}


@app.post('/apptainer/build/result')
async def build_result(request: BuildResultRequest) -> FileResponse:
    task_id = request.task_id
    sif_path = SIF_DIR / f'{task_id}.sif'
    build_status = build_status_tracker.get_status(task_id)

    if build_status == BuildStatus.FAILED:
        raise HTTPException(status_code=500, detail='Build failed')

    elif (
        build_status in (BuildStatus.PENDING, BuildStatus.RUNNING)
        or not sif_path.exists()
    ):
        raise HTTPException(status_code=404, detail='Result is not available yet')

    return FileResponse(
        sif_path,
        media_type='application/octet-stream',
        filename=f'{task_id}.sif',
    )


@app.post('/apptainer/build/clear')
async def build_clear(request: BuildClearRequest) -> None:
    task_id = request.task_id
    def_path = DEF_DIR / f'{task_id}.def'
    sif_path = SIF_DIR / f'{task_id}.sif'

    for path in (def_path, sif_path):
        if path.exists():
            path.unlink()

    build_status_tracker.remove_status(task_id)


@app.post('/apptainer/overlay/create')
async def overlay_create(
    background_tasks: BackgroundTasks, request: OverlayCreateRequest
) -> dict[str, str]:
    for path in IMG_DIR.glob('*'):
        path.unlink()

    task_id = str(uuid4())
    img_path = IMG_DIR / f'{task_id}.img'

    background_tasks.add_task(
        overlay_create_background_task,
        task_id,
        request.fakeroot,
        request.size,
        img_path,
    )

    return {'task_id': task_id}


@app.post('/apptainer/overlay/create/result')
async def overlay_create_result(request: BuildResultRequest) -> FileResponse:
    img_path = IMG_DIR / f'{request.task_id}.img'

    if not img_path.exists():
        raise HTTPException(status_code=404, detail='Result is not available yet')

    return FileResponse(
        img_path,
        media_type='application/octet-stream',
        filename=f'{request.task_id}.img',
    )


@app.post('/apptainer/overlay/create/clear')
async def overlay_create_clear(request: BuildClearRequest) -> None:
    img_path = IMG_DIR / f'{request.task_id}.img'

    if img_path.exists():
        img_path.unlink()


@app.get('/apptainer/version')
async def version() -> str:
    args = ['apptainer', 'version']

    try:
        result = subprocess.run(args, check=True, capture_output=True, text=True)

        return result.stdout

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500, detail=f'Apptainer version failed: {e.stderr}'
        )


@app.get('/health')
async def health_check() -> dict[str, str]:
    return {'status': 'ok'}


@app.get('/scalar', include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )
