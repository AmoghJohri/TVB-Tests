FROM alpine:3.9
ADD pipeline.py /
ADD full_testing.py /
ADD full_testing_legacy.py / 
ADD main.c / 
ADD tvbii_multicore.c /
ADD C_Input /
ADD Final_Output /
ADD Final_Output_Legacy /
RUN apk add --no-cache python3 && \
	apk add build-base && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache

RUN apk add --no-cache zlib libjpeg-turbo-dev libpng-dev gsl gsl-dev freetype-dev lcms2-dev libwebp-dev harfbuzz-dev fribidi-dev tcl-dev tk-dev && \
	apk add --no-cache libpng freetype libstdc++ openblas libxml2 libxslt && \
	apk add --no-cache --virtual .build-deps \
	    g++ gfortran file binutils \
	    openblas-dev \
	    python3-dev \
	    gcc \
	    build-base \
	    musl-dev \
	    libxml2-dev \
	    libxslt-dev \
		libressl-dev \ 
		pkgconfig && \
	ln -s /usr/include/locale.h /usr/include/xlocale.h \
	&& pip3 install wheel \
	&& pip3 install matplotlib \
	&& pip3 install mpld3 \
	&& pip3 install joblib \
	&& pip3 install numpy \
	&& pip3 install scipy==1.3.3 \
	&& pip3 install pandas \
	&& pip3 install rsHRF==1.2.2 \
    && pip3 install nitime==0.8.1 \
	&& rm -r /root/.cache \
	&& find /usr/lib/python3.*/ -name 'tests' -exec rm -r '{}' + \
	&& find /usr/lib/python3.*/site-packages/ -name '*.so' -print -exec sh -c 'file "{}" | grep -q "not stripped" && strip -s "{}"' \; \
	&& rm /usr/include/xlocale.h \
	&& apk del .build-deps

CMD [ "python", "./full_testing.py" ]
