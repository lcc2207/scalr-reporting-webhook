#!/bin/bash

yum update -y
yum install epel-release -y

yum install python-pip -y

pip install docker-compose

curl -fsSL https://get.docker.com/ | sh
service docker start || systemctl start docker


