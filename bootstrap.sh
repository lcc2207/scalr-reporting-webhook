#!/bin/bash

yum update -y
yum install epel-release -y
yum install python-pip git unzip -y

pip install docker-compose

curl -fsSL https://get.docker.com/ | sh
service docker start || systemctl start docker

git clone https://github.com/scalr-tutorials/scalr-reporting-webhook /opt/reporting-webhook

chmod 755 /opt/reporting-webhook/relaunch.sh
/opt/reporting-webhook/relaunch.sh
