import logging

import uvicorn

from decouple import config

from math_rag_apptainer.endpoints import app


PORT = config('PORT', cast=int)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
    )

    uvicorn.run(app, host='0.0.0.0', port=PORT)
