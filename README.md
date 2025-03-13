1. `docker build -t ubuntu-apptainer .`
2. `docker run -it --privileged --name apptainer-container -v ~/.ssh:/root/.ssh ubuntu-apptainer /bin/bash`
3. `apptainer build data_stack.sif data_stack.def`
4. `scp data_stack.sif lpanic@login-gpu.hpc.srce.hr:.`