#基本镜像
FROM nvidia/cuda:10.0-runtime-centos7
LABEL maintainer="Lin JianRui <linjr@yunjiacloud.com>"

# 时区
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' >/etc/timezone

#工作目录
WORKDIR /home/admin

#拷贝代码
COPY src/auto_test/ /home/user/linjr/auto_test/
COPY src/auto_train/ /home/user/linjr/auto_train/
COPY src/online_label_api_dev/ /home/user/linjr/online_label_api_dev/

#安装支持
COPY *.repo requirements.txt ./
COPY packages ./packages
RUN mkdir -p /etc/yum.repos.bak && mv /etc/yum.repos.d/*.repo /etc/yum.repos.bak && \
    mv *.repo /etc/yum.repos.d/ && \
    yum -y clean all && yum makecache && \
    yum install -y gcc gcc-c++ python-pip python-devel perl pciutils sox libsndfile libcurl-devel && \
    yum -y clean all && \
    pip install --no-index --find-links=./packages/  --no-cache-dir -r ./requirements.txt && \
    rm -rf ./packages

# 安装ffmpeg
COPY libs ./libs
RUN yum install -y automake autoconf libtool make tar
RUN cd libs && tar -xvf yasm-1.3.0.tar.gz && cd yasm-1.3.0 && ./configure && make && make install && cd /home/admin && \
    cd libs && tar -xvf ffmpeg-3.4.tar.gz && cd ffmpeg-3.4 && ./configure --disable-doc && make && make install && cd /home/admin && \
    rm ./libs -rf && \
    yum remove -y automake autoconf libtool make && yum -y clean all
