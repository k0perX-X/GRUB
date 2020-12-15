FROM ubuntu

MAINTAINER k0perXD@ya.ru

COPY Docker/Ubuntu/localtime /etc/localtime

RUN apt-get update 
RUN apt-get -y install apache2 python3-pip git systemctl
RUN pip3 install flask requests pycryptodome

RUN systemctl enable apache2
RUN cd /etc/apache2 ; mkdir ssl ; cd ssl ; openssl req -new -x509 -days 1461 -nodes -out cert.pem -keyout cert.key -subj "/C=RU/ST=SPb/L=SPb/O=Global Security/OU=IT Department/CN=test.dmosk.local/CN=test" 
RUN a2enmod ssl
RUN a2enmod rewrite
RUN a2enmod proxy
RUN a2enmod proxy_http
RUN rm /etc/apache2/sites-available/*
COPY Docker/Ubuntu/000-default.conf /etc/apache2/sites-available/
RUN systemctl restart apache2

EXPOSE 80
EXPOSE 443

RUN mkdir /app
COPY . /app/

RUN cp -r /app/output/ /app/output1/
COPY Docker/Ubuntu/bashscript /
RUN chmod +x bashscript

ENTRYPOINT bash bashscript