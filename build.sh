# start interactive job on gpu node
qsub -I -q login-gpu

# create build directory
cd /scratch/apptainer
mkdir ${USER}
cd ${USER}
mkdir tmp

# update TMPDIR env variables
export APPTAINER_TMPDIR=/scratch/apptainer/${USER}/tmp
unset TMPDIR

# build apptainer sandbox
apptainer build --sandbox ubuntu_20.04_sandbox docker://ubuntu:20.04
apptainer shell --writable --fakeroot ubuntu_20.04_sandbox
# Apptainer> ...
exit

# convert apptainer sandbox to image
apptainer build ubuntu_20.04.sif ubuntu_20.04_sandbox

# move image to home directory
mv ubuntu_20.04.sif ~
cd ~

# delete build directory
rm -rf /scratch/apptainer/${USER}