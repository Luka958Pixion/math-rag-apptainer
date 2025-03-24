import docker

from fastapi import FastAPI


app = FastAPI()
client = docker.from_env()
container = client.containers.get('apptainer')


@app.get('/build/tgi')
async def build_tgi():
    exec_result = container.exec_run('apptainer build tgi.sif tgi.def')

    return exec_result.output.decode()


@app.get('/build/tei')
async def build_tei():
    raise NotImplementedError()
