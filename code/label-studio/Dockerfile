FROM heartexlabs/label-studio

RUN echo "Removing old build from LSB"

ARG dist=label_studio/frontend/dist/lsf

RUN rm -rf $dist/{js,css}/*

RUN echo "Copying build directory from LSF to LSB"

ARG build=label-studio-frontend/build/static

COPY $build/js $dist/js
COPY $build/css $dist/css