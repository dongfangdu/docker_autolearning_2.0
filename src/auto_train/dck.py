import os
os.system("docker run -it --runtime=nvidia --net=host --name autolearning -v /home/user/linjr/:/home/user/linjr/  nvidia/cuda:8.0-runtime-centos7 bash ")
