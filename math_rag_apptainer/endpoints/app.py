import shutil
import subprocess

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from scalar_fastapi import get_scalar_api_reference

from math_rag_apptainer.requests import OverlayCreateRequest


app = FastAPI()

DEF_DIR = Path('defs')
SIF_DIR = Path('sifs')
IMG_DIR = Path('imgs')

DEF_DIR.mkdir(parents=True, exist_ok=True)
SIF_DIR.mkdir(parents=True, exist_ok=True)
IMG_DIR.mkdir(parents=True, exist_ok=True)


@app.post('/apptainer/build"')
async def build(file: UploadFile = File(...)) -> FileResponse:
    if not file.filename.endswith('.def'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Only .def files are accepted',
        )

    for path in DEF_DIR.glob('*'):
        path.unlink()

    for path in SIF_DIR.glob('*'):
        path.unlink()

    def_path = DEF_DIR / file.filename
    sif_filename = Path(file.filename).with_suffix('.sif').name
    sif_path = SIF_DIR / sif_filename

    with def_path.open('wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

    args = ['apptainer', 'build', str(sif_path), str(def_path)]

    try:
        subprocess.run(args, check=True, capture_output=True, text=True)

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500, detail=f'Apptainer build failed: {e.stderr}'
        )

    return FileResponse(
        sif_path, media_type='application/octet-stream', filename=sif_filename
    )


@app.post('/apptainer/overlay/create')
async def overlay_create(request: OverlayCreateRequest) -> FileResponse:
    for path in IMG_DIR.glob('*'):
        path.unlink()

    img_filename = request.filename + '.img'
    img_path = IMG_DIR / img_filename
    args = ['apptainer', 'overlay', 'create']

    if request.fakeroot:
        args.append('--fakeroot')

    args.extend(['--size', str(request.size), img_path])

    try:
        subprocess.run(args, check=True, capture_output=True, text=True)

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500, detail=f'Apptainer overlay create failed: {e.stderr}'
        )

    return FileResponse(
        img_path, media_type='application/octet-stream', filename=img_filename
    )


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
