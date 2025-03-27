import logging

import uvicorn

from decouple import config
from fastapi import FastAPI

from math_rag_apptainer.configs import OPENAPI_URL, TITLE
from math_rag_apptainer.routers import health_router, scalar_router
from math_rag_apptainer.routers.apptainer import (
    apptainer_build_router,
    apptainer_overlay_router,
    apptainer_version_router,
)


PORT = config('PORT', cast=int)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
    )

    app = FastAPI(openapi_url=OPENAPI_URL, title=TITLE)
    app.include_router(health_router)
    app.include_router(scalar_router)
    app.include_router(apptainer_build_router)
    app.include_router(apptainer_overlay_router)
    app.include_router(apptainer_version_router)

    uvicorn.run(app, host='0.0.0.0', port=PORT)
