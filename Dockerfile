FROM debian:jessie-slim
MAINTAINER Scalr <@scalr.com>

RUN apt-get update && \
    apt-get install -y --no-install-recommends python python-dev python-pip uwsgi uwsgi-plugin-python && \
    groupadd uwsgi && \
    useradd -g uwsgi uwsgi

COPY ./requirements.txt /opt/reporting-webhook/

RUN pip install -r /opt/reporting-webhook/requirements.txt

COPY . /opt/reporting-webhook

EXPOSE 5018

CMD ["/usr/bin/uwsgi", "--ini", "/opt/reporting-webhook/uwsgi.ini"] 
