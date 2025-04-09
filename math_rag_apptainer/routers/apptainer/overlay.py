import subprocess

from logging import getLogger
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from math_rag_apptainer.enums import OverlayCreateStatus
from math_rag_apptainer.requests import (
    OverlayCreateRequest,
    OverlayCreateResultRequest,
    OverlayCreateStatusRequest,
)
from math_rag_apptainer.trackers import OverlayCreateStatusTracker


logger = getLogger(__name__)

router = APIRouter()
status_tracker = OverlayCreateStatusTracker()

IMG_DIR = Path('files/imgs')

IMG_DIR.mkdir(parents=True, exist_ok=True)


def overlay_create_background_task(
    task_id: str, fakeroot: bool, size: int, img_path: Path
) -> None:
    status_tracker.set_status(task_id, OverlayCreateStatus.RUNNING)
    args = ['apptainer', 'overlay', 'create']

    if fakeroot:
        args.append('--fakeroot')

    args.extend(['--size', str(size), img_path])

    try:
        # capture_output=False to see stdout and stderr in console
        subprocess.run(args, check=True, capture_output=False, text=True)
        status_tracker.set_status(task_id, OverlayCreateStatus.DONE)

    except subprocess.CalledProcessError as e:
        logger.error(f'Apptainer overlay create {task_id} failed: {e.stderr}')
        status_tracker.set_status(task_id, OverlayCreateStatus.FAILED)


def overlay_create_cleanup_task(task_id: str) -> None:
    img_path = IMG_DIR / f'{task_id}.img'

    if img_path.exists():
        img_path.unlink()

    status_tracker.remove_status(task_id)
    logger.info(f'Cleaned up overlay create files for task {task_id}')


@router.post('/apptainer/overlay/create/init')
async def overlay_create_init(
    background_tasks: BackgroundTasks, request: OverlayCreateRequest
) -> dict[str, str]:
    task_id = str(uuid4())
    status_tracker.set_status(task_id, OverlayCreateStatus.PENDING)
    img_path = IMG_DIR / f'{task_id}.img'

    background_tasks.add_task(
        overlay_create_background_task,
        task_id,
        request.fakeroot,
        request.size,
        img_path,
    )

    return {'task_id': task_id}


@router.post('/apptainer/overlay/create/status')
async def overlay_create_status(request: OverlayCreateStatusRequest) -> dict[str, str]:
    task_id = request.task_id
    status = status_tracker.get_status(task_id)

    if status is None:
        raise HTTPException(status_code=404, detail=f'Task {task_id} not found')

    return {'status': status.value}


@router.post('/apptainer/overlay/create/result')
async def overlay_create_result(request: OverlayCreateResultRequest) -> FileResponse:
    task_id = request.task_id
    img_path = IMG_DIR / f'{task_id}.img'
    status = status_tracker.get_status(task_id)

    if status is None:
        raise HTTPException(status_code=404, detail=f'Task {task_id} not found')

    if status != OverlayCreateStatus.DONE or not img_path.exists():
        raise HTTPException(
            status_code=400, detail=f'Result not available, build status: {status}'
        )

    background_task = BackgroundTask(overlay_create_cleanup_task, task_id)

    return FileResponse(
        img_path,
        media_type='application/octet-stream',
        filename=f'{task_id}.img',
        background=background_task,
    )
