# Base Image
FROM ubuntu:22.04

MAINTAINER dev@bats.li

# Installing requirements
RUN apt-get update

# nano for editing the script file for cloudflare api connection
RUN apt-get install -y vim

# curl to download the script
RUN apt-get install -y curl

# cron to schedule the script
RUN apt-get install -y cron

RUN apt-get install -y python3.11

RUN apt-get install -y python3-docker

RUN apt-get install -y python3-elasticsearch

# Create directory for script
RUN mkdir -p /app; 

# Create directory for cron script
RUN mkdir -p /app/data

RUN curl https://raw.githubusercontent.com/batscs/docker-elk-monitor/main/app/app.py -o /app/app.py
RUN curl https://raw.githubusercontent.com/batscs/docker-elk-monitor/main/app/elastic_api.py -o /app/elastic_api.py
RUN curl https://raw.githubusercontent.com/batscs/docker-elk-monitor/main/app/init.sh -o /app/init.sh

RUN chmod +x /app/init.sh

# Crontab in foreground to keep Docker Container running when detatched
CMD /app/init.sh
