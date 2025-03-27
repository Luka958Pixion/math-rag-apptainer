from fastapi import APIRouter
from scalar_fastapi import get_scalar_api_reference

from math_rag_apptainer.configs import OPENAPI_URL, TITLE


router = APIRouter()


@router.get('/scalar', include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=OPENAPI_URL,
        title=TITLE,
    )
