import subprocess

from fastapi import APIRouter, HTTPException


router = APIRouter()


@router.get('/apptainer/version')
async def version() -> str:
    args = ['apptainer', 'version']

    try:
        result = subprocess.run(args, check=True, capture_output=True, text=True)
        version = result.stdout.strip()

        return version

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500, detail=f'Apptainer version failed: {e.stderr}'
        )
