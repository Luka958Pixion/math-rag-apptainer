from fastapi import FastAPI, Form, HTTPException


app = FastAPI()


@app.get('/build/tgi')
async def build_tgi():
    raise NotImplementedError()


@app.get('/build/tei')
async def build_tei():
    raise NotImplementedError()
