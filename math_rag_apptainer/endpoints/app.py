import shutil
import subprocess

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import (
    FileResponse,
    PlainTextResponse,
    Response,
)
from scalar_fastapi import get_scalar_api_reference


app = FastAPI()

UPLOAD_DIR = Path('uploads')
PROCESSED_DIR = Path('processed')

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


@app.post('/apptainer/build"')
async def build(file: UploadFile = File(...)) -> FileResponse:
    def_path = UPLOAD_DIR / file.filename
    sif_filename = f'{file.filename.rsplit('.', 1)[0]}.sif'
    sif_path = PROCESSED_DIR / sif_filename

    with def_path.open('wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        subprocess.run(
            ['apptainer', 'build', str(sif_path), str(def_path)],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500, detail=f'Apptainer build failed: {e.stderr}'
        )

    return FileResponse(
        sif_path, media_type='application/octet-stream', filename=sif_filename
    )


@app.get('/apptainer/overlay/create')
async def build_tei() -> None:
    raise NotImplementedError()


@app.get('/apptainer/version')
async def version() -> str:
    try:
        result = subprocess.run(
            ['apptainer', 'version'], check=True, capture_output=True, text=True
        )

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
