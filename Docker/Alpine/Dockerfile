FROM alpine

MAINTAINER k0perXD@ya.ru

COPY localtime /etc/localtime

RUN apk update 
RUN apk add py-pip git bash gcc musl-dev openssl nginx openrc
RUN pip3 install flask requests pycryptodome

EXPOSE 80
EXPOSE 433
EXPOSE 5000

ARG INCUBATOR_VER=unknown
RUN echo INCUBATOR_VER
RUN mkdir /app
RUN git clone https://github.com/k0perX-X/GRUB.git /app/

RUN cp -r /app/output/ /app/output1/
COPY bashscript /
RUN chmod +x bashscript

# ENTRYPOINT bash bashscript