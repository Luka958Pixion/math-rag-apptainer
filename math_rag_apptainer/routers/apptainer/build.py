import logging
import shutil
import subprocess

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from math_rag_apptainer.enums import BuildStatus
from math_rag_apptainer.requests import BuildResultRequest, BuildStatusRequest
from math_rag_apptainer.trackers import BuildStatusTracker


router = APIRouter()
status_tracker = BuildStatusTracker()


DEF_DIR = Path('files/defs')
SIF_DIR = Path('files/sifs')

DEF_DIR.mkdir(parents=True, exist_ok=True)
SIF_DIR.mkdir(parents=True, exist_ok=True)


def build_background_task(task_id: str, def_path: Path, sif_path: Path) -> None:
    status_tracker.set_status(task_id, BuildStatus.RUNNING)
    args = ['apptainer', 'build', str(sif_path), str(def_path)]

    try:
        subprocess.run(args, check=True, capture_output=True, text=True)
        status_tracker.set_status(task_id, BuildStatus.DONE)

    except subprocess.CalledProcessError as e:
        logging.error(f'Apptainer build {task_id} failed: {e.stderr}')
        status_tracker.set_status(task_id, BuildStatus.FAILED)

        if def_path.exists():
            def_path.unlink()
            logging.info(f'Deleted .def file for task {task_id} after build failure')


def build_cleanup_task(task_id: str) -> None:
    def_path = DEF_DIR / f'{task_id}.def'
    sif_path = SIF_DIR / f'{task_id}.sif'

    for path in (def_path, sif_path):
        if path.exists():
            path.unlink()

    status_tracker.remove_status(task_id)
    logging.info(f'Cleaned up build files for task {task_id}')


@router.post('/apptainer/build')
async def build(
    background_tasks: BackgroundTasks, def_file: UploadFile = File(...)
) -> dict[str, str]:
    if not def_file.filename.endswith('.def'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Only .def files are accepted',
        )

    task_id = str(uuid4())
    status_tracker.set_status(task_id, BuildStatus.PENDING)
    def_path = DEF_DIR / f'{task_id}.def'
    sif_path = SIF_DIR / f'{task_id}.sif'

    with def_path.open('wb') as buffer:
        shutil.copyfileobj(def_file.file, buffer)

    background_tasks.add_task(build_background_task, task_id, def_path, sif_path)

    return {'task_id': task_id}


@router.post('/apptainer/build/status')
async def build_status(request: BuildStatusRequest) -> dict[str, str]:
    task_id = request.task_id
    status = status_tracker.get_status(task_id)

    if status is None:
        raise HTTPException(status_code=404, detail=f'Task {task_id} not found')

    return {'task_id': task_id, 'status': status.value}


@router.post('/apptainer/build/result')
async def build_result(request: BuildResultRequest) -> FileResponse:
    task_id = request.task_id
    sif_path = SIF_DIR / f'{task_id}.sif'
    status = status_tracker.get_status(task_id)

    if status is None:
        raise HTTPException(status_code=404, detail=f'Task {task_id} not found')

    if status != BuildStatus.DONE or not sif_path.exists():
        raise HTTPException(
            status_code=400, detail=f'Result not available, build status: {status}'
        )

    background_task = BackgroundTask(build_cleanup_task, task_id)

    return FileResponse(
        sif_path,
        media_type='application/octet-stream',
        filename=f'{task_id}.sif',
        background=background_task,
    )
