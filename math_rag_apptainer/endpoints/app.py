from docker import from_env
from docker.models.containers import Container
from fastapi import FastAPI, HTTPException
from fastapi.responses import (
    JSONResponse,
    PlainTextResponse,
    Response,
    StreamingResponse,
)

from math_rag_apptainer.utils import stream_sif_file


app = FastAPI()
client = from_env()
container: Container = client.containers.get('apptainer')


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
async def health_check() -> JSONResponse:
    try:
        container.reload()

        if container.status == 'running':
            return JSONResponse(content={'status': 'ok'})

        return JSONResponse(
            content={'status': 'container not running'}, status_code=503
        )

    except Exception as e:
        return JSONResponse(
            content={'status': 'error', 'detail': str(e)}, status_code=500
        )
