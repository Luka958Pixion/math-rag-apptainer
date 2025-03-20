#!/bin/bash
#PBS -P gpu
#PBS -N tgi
#PBS -o output.log
#PBS -e error.log
#PBS -q gpu
#PBS -l ngpus=1
#PBS -l ncpus=8

cd "${PBS_O_WORKDIR:-""}"

export PYTHONUNBUFFERED=1

apptainer run --nv --bind $PWD/data/meta-llama/Llama-3.2-3B:/model tgi.sif


echo "Waiting for the TGI server to become healthy..."

while true; do
    response=$(curl -s -o /dev/null -w "%{http_code}" http://0.0.0.0:8000/health)

    if [ "$response" -eq 200 ]; then
        echo "TGI server is healthy."
        break

    else
        echo "Health check returned status code $response. Retrying in 5 seconds..."
        sleep 5
    fi
done

apptainer run tgi_client.sif