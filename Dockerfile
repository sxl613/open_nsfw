FROM ubuntu:16.04
LABEL maintainer caffe-maint@googlegroups.com

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        git \
        wget \
        libatlas-base-dev \
        libboost-all-dev \
        libgflags-dev \
        libgoogle-glog-dev \
        libhdf5-serial-dev \
        libleveldb-dev \
        liblmdb-dev \
        libopencv-dev \
        libprotobuf-dev \
        libsnappy-dev \
        libmagic-dev \
        protobuf-compiler \
        python-opencv \ 
        libopencv-dev \ 
        libav-tools  \ 
        libjpeg-dev \ 
        libpng-dev \ 
        libtiff-dev \ 
        libjasper-dev \ 
        libgtk2.0-dev \ 
        python3 \ 
        python3-dev \
        python3-pip \
        locales \ 
        python-setuptools && \
    rm -rf /var/lib/apt/lists/*

ENV CAFFE_ROOT=/opt/caffe
WORKDIR $CAFFE_ROOT

# Set the locale
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG C.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL C.UTF-8  

# FIXME: use ARG instead of ENV once DockerHub supports this
# https://github.com/docker/hub-feedback/issues/460
ENV CLONE_TAG=1.0
RUN pip3 install --upgrade pip

RUN git clone -b ${CLONE_TAG} --depth 1 https://github.com/sxl613/caffe.git . && \
    cd python && for req in $(cat requirements.txt) pydot; do python3 -m pip install $req; done && cd .. && \
    mkdir build && cd build && \
    cmake -D python_version=3 -D CPU_ONLY=1 .. && \
    make -j4

# RUN cd ~/ &&\
#     git clone https://github.com/Itseez/opencv.git &&\
#     git clone https://github.com/Itseez/opencv_contrib.git &&\
#     cd opencv && mkdir build && cd build && cmake  -DWITH_QT=ON -DWITH_OPENGL=ON -DFORCE_VTK=ON -DWITH_TBB=ON -DWITH_GDAL=ON -DWITH_XINE=ON -DBUILD_EXAMPLES=ON .. && \
#     make -j4 && make install && ldconfig

RUN python3 -m pip install flask \
                libmagic   \
                numpy  \
                python-magic  \
                opencv-python \
                scikit-image \
                scipy \
                numpy

ENV FLASK_APP api.py 
ENV FLASK_ENV development
ENV RELOADER_TYPE stat
ENV PYCAFFE_ROOT $CAFFE_ROOT/python
ENV PYTHONPATH $PYCAFFE_ROOT:$PYTHONPATH
ENV PATH $CAFFE_ROOT/build/tools:$PYCAFFE_ROOT:$PATH
RUN echo "$CAFFE_ROOT/build/lib" >> /etc/ld.so.conf.d/caffe.conf && ldconfig

WORKDIR /workspace
#COPY . /workspace/


EXPOSE 5000
#ENTRYPOINT [ "python" ]
#CMD ["app.py"]