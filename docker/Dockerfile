FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04 
WORKDIR /root/pickpod
COPY . /root/pickpod

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# change mirrors
RUN sed -i "s@http://archive.ubuntu.com/ubuntu/@https://mirrors.tuna.tsinghua.edu.cn/ubuntu/@g" /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y cmake libsndfile1 ffmpeg python3-pip

# change the pip mirror
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip3 install --no-cache-dir .
RUN pip3 install -r ./app/requirements.txt

# start the service
ENTRYPOINT [ "streamlit", "run", "./app/Home.py"]
CMD ["--server.port", "8051"]

