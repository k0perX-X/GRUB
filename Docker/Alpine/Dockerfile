FROM alpine

MAINTAINER k0perXD@ya.ru

COPY Docker/Alpine/localtime /etc/localtime

RUN apk update 
RUN apk add py-pip git bash gcc musl-dev openssl nginx
RUN pip3 install flask requests pycryptodome

RUN adduser -D -g 'www' www
RUN rm /etc/nginx/nginx.conf
COPY Docker/Alpine/nginx.conf /etc/nginx/
RUN cd /etc/nginx ; mkdir ssl ; cd ssl ; openssl req -new -x509 -days 1461 -nodes -out cert.pem -keyout cert.key -subj "/C=RU/ST=SPb/L=SPb/O=Global Security/OU=IT Department/CN=test.dmosk.local/CN=test"
RUN nginx -t
RUN chown -R www:www /var/lib/nginx
RUN chown -R www:www /etc/nginx

EXPOSE 80
EXPOSE 443

RUN mkdir /app
COPY . /app/

RUN cp -r /app/output/ /app/output1/
COPY Docker/Alpine/bashscript /
RUN chmod +x bashscript

ENTRYPOINT bash bashscript