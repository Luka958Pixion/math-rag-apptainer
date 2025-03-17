# ubuntu-apptainer

## Docker
1. `docker build --no-cache --platform=linux/amd64 -t ubuntu-apptainer .`
2. `docker run -it --privileged --platform=linux/amd64 --name apptainer-container -v ~/.ssh:/root/.ssh ubuntu-apptainer /bin/bash` (`docker exec -it apptainer-container /bin/bash`)
3. `apptainer build --docker-login data_stack.sif data_stack.def`
4. `scp data_stack.sif lpanic@login-gpu.hpc.srce.hr:.`

## Host
1. `ssh lpanic@login-gpu.hpc.srce.hr`
2. `./data_stack.sif python3 --version`




wget --content-disposition https://ngc.nvidia.com/downloads/ngccli_cat_linux.zip
unzip ngccli_cat_linux.zip
./ngc-cli/ngc --version
./ngc-cli/ngc registry resource download-version "nvidia/ngc-apps/ngc_cli:3.63.0"
