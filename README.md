# ubuntu-apptainer

## Docker
1. `docker build --platform=linux/amd64 -t ubuntu-apptainer .`
2. `docker run -it --privileged --platform=linux/amd64 --name apptainer-container -v ~/.ssh:/root/.ssh ubuntu-apptainer /bin/bash`
3. `apptainer build data_stack.sif data_stack.def`
4. `scp data_stack.sif lpanic@login-gpu.hpc.srce.hr:.`

## Host
1. `ssh lpanic@login-gpu.hpc.srce.hr`
2. `./data_stack.sif python3 --version`