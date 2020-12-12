FROM alpine

MAINTAINER k0perXD@ya.ru

COPY ./localtime /etc/localtime

RUN apk update 
RUN apk add socat py-pip git bash gcc musl-dev
RUN pip3 install flask requests pycryptodome

#RUN apt-get update 
#RUN apt-get -y install apache2 python3-pip git systemctl
#RUN pip3 install flask requests pycryptodome

#RUN systemctl enable apache2
#RUN cd /etc/apache2 ; mkdir ssl ; cd ssl ; openssl req -new -x509 -days 1461 -nodes -out cert.pem -keyout cert.key -subj "/C=RU/ST=SPb/L=SPb/O=Global Security/OU=IT Department/CN=test.dmosk.local/CN=test" 
#RUN a2enmod ssl
#RUN a2enmod rewrite
#RUN a2enmod proxy
#RUN a2enmod proxy_http
#RUN rm /etc/apache2/sites-available/*
#COPY ./000-default.conf /etc/apache2/sites-available/
#RUN systemctl restart apache2

EXPOSE 80
EXPOSE 433
EXPOSE 5000

RUN mkdir /app 
RUN git clone https://github.com/k0perX-X/GRUB.git /app/

RUN cp -r /app/output/ /app/output1/
COPY ./bashscript /
RUN chmod +x bashscript

ENTRYPOINT bash bashscript 