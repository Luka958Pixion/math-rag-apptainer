# start interactive job on gpu node
qsub -I -q login-gpu

# create build directory
cd /scratch/apptainer && mkdir ${USER} && cd ${USER} && mkdir tmp

# update TMPDIR env variables
export APPTAINER_TMPDIR=/scratch/apptainer/${USER}/tmp && unset TMPDIR

# build apptainer sandbox
image="docker://ubuntu:20.04" && image_name="ubuntu_20.04" && sandbox_name="${image_name}_sandbox"

apptainer build --sandbox "$sandbox_name" "$image"
apptainer shell --writable --fakeroot "$sandbox_name"
# Apptainer> ...
exit

# convert apptainer sandbox to image
apptainer build "$image_name".sif "$sandbox_name"

# move image to home directory
mv "$image_name".sif ~ && cd ~

# delete build directory
rm -rf /scratch/apptainer/${USER}