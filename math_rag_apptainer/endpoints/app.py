from docker import from_env
from docker.models.containers import Container
from fastapi import FastAPI, HTTPException
from fastapi.responses import (
    PlainTextResponse,
    Response,
    StreamingResponse,
)
from scalar_fastapi import get_scalar_api_reference

from math_rag_apptainer.utils import stream_sif_file


app = FastAPI()
client = from_env()
container: Container = client.containers.get('math_rag_apptainer_dev_container')


@app.get('/build/tgi')
async def build_tgi() -> Response:
    sif_filename = 'tgi.sif'
    container_sif_path = f'/huggingface/{sif_filename}'
    container_def_path = '/huggingface/tgi.def'

    result = container.exec_run(
        f'apptainer build {container_sif_path} {container_def_path}'
    )
    output = result.output

    if isinstance(output, bytes):
        output = output.decode()

    if result.exit_code != 0:
        raise HTTPException(status_code=500, detail=output)

    archive_stream, _ = container.get_archive(container_sif_path)
    content = stream_sif_file(archive_stream)

    return StreamingResponse(
        content,
        media_type='application/octet-stream',
        headers={'Content-Disposition': f'attachment; filename={sif_filename}'},
    )


@app.get('/build/tei')
async def build_tei() -> None:
    raise NotImplementedError()


@app.get('/version')
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
