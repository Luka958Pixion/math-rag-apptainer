import uvicorn

from math_rag_apptainer.endpoints import app


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000)
