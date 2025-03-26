#!/bin/bash
#PBS -P gpu
#PBS -N nim
#PBS -o output.log
#PBS -e error.log
#PBS -q gpu
#PBS -l ngpus=1
#PBS -l ncpus=8

cd "${PBS_O_WORKDIR:-""}"

export http_proxy="http://10.150.1.1:3128" # squid proxy
export https_proxy="http://10.150.1.1:3128"
export NO_PROXY="0.0.0.0"   # no proxy for local connections

export PYTHONUNBUFFERED=1
export LOCAL_NIM_CACHE=./nim/.cache/nim
export NIM_CACHE_PATH=/mnt/nim-cache
export NGC_API_KEY="..."

mkdir -p "$LOCAL_NIM_CACHE"


apptainer run \
    --nv \
    --fakeroot \
    --overlay llama-3.2-3b-instruct-overlay.img  \
    --env NGC_API_KEY=$NGC_API_KEY \
    llama-3.2-3b-instruct.sif &


echo "Waiting for the NIM server to become healthy..."

while true; do
    response=$(curl -X GET 'http://0.0.0.0:8000/v1/health/ready' -H 'accept: application/json')
    http_code=$(curl -s -o /dev/null -w "%{http_code}" -X GET 'http://0.0.0.0:8000/v1/health/ready')

    if [ "$http_code" -eq 200 ]; then
        echo "NIM server is healthy."
        break
    else
        echo "Health check returned $http_code. Retrying in 5s..."
        sleep 5
    fi
done

curl -X 'POST' \
'http://0.0.0.0:8000/v1/chat/completions' \
-H 'accept: application/json' \
-H 'Content-Type: application/json' \
-d '{
    "model": "meta/llama-3.2-3b-instruct",
    "messages": [{"role":"user", "content":"Write a limerick about the wonders of GPU computing."}],
    "max_tokens": 64
}'