import shutil

from pathlib import Path

from docker import from_env
from docker.models.containers import Container
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import (
    FileResponse,
    PlainTextResponse,
    Response,
)
from scalar_fastapi import get_scalar_api_reference


app = FastAPI()
client = from_env()
container: Container = client.containers.get('math_rag_apptainer_dev_container')

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

    with def_path.open('rb') as def_file:
        container.put_archive('/tmp', def_file.read())

    exit_code, output = container.exec_run(
        f'apptainer build /tmp/{sif_filename} /tmp/{file.filename}'
    )

    if exit_code != 0:
        raise HTTPException(
            status_code=500, detail=f'Apptainer build failed: {output.decode()}'
        )

    bits, stat = container.get_archive(f'/tmp/{sif_filename}')

    with sif_path.open('wb') as sif_file:
        for chunk in bits:
            sif_file.write(chunk)

    return FileResponse(
        sif_path, media_type='application/octet-stream', filename=sif_filename
    )


@app.get('/apptainer/overlay/create')
async def build_tei() -> None:
    raise NotImplementedError()


@app.get('/apptainer/version')
async def get_version() -> Response:
    result = container.exec_run('apptainer version')
    output = result.output

    if isinstance(output, bytes):
        output = output.decode()

    if result.exit_code != 0:
        raise HTTPException(status_code=500, detail=output)

    return PlainTextResponse(content=output)


@app.get('/health')
async def health_check() -> dict[str, str]:
    return {'status': 'ok'}


@app.get('/scalar', include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )
