# start interactive job on gpu node
qsub -I -q login-gpu -l select=1:ncpus=8:mem=32gb -l walltime=00:30:00

# create build directory
cd /scratch/apptainer && \
mkdir ${USER} && \
cd ${USER} && \
mkdir tmp

# update TMPDIR env variables
export APPTAINER_TMPDIR=/scratch/apptainer/${USER}/tmp && \
unset TMPDIR

# build apptainer sandbox
image="docker://ghcr.io/huggingface/text-generation-inference:latest" && \
image_name="tgi" && \
sandbox_name="${image_name}_sandbox" && \
volume="$PWD/data"

export MODEL="meta-llama/Llama-3.2-1B"

mkdir -p "$volume"

apptainer build --sandbox "$sandbox_name" "$image"
apptainer exec --writable --fakeroot "$sandbox_name" mkdir -p /data
apptainer shell --writable --fakeroot --nv --bind $volume:/data --env MODEL=$MODEL "$sandbox_name"
# Apptainer> ...
apt-get update
apt-get install -y python3-pip

pip --version
pip install huggingface_hub hf_transfer

huggingface-cli login
huggingface-cli download "$MODEL" --local-dir "/data/$MODEL" --local-dir-use-symlinks False

exit

# convert apptainer sandbox to image
apptainer build "$image_name".sif "$sandbox_name"

# move image and copy model to home directory
home_dir="new" && \
mv "$image_name".sif ~/${home_dir} && \
cp -r "$volume/$MODEL" ~/${home_dir} && \
cd ~/${home_dir}

# delete build directory
rm -rf /scratch/apptainer/${USER}