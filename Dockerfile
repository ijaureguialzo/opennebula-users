ARG DEBIAN_VERSION=11

FROM debian:${DEBIAN_VERSION}

ARG DEBIAN_VERSION=11
ARG OPENNEBULA_VERSION=6.6.0

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update

RUN apt-get -y install gnupg wget apt-transport-https systemd

RUN mkdir -p /etc/apt/keyrings

RUN wget -q -O- https://downloads.opennebula.io/repo/repo2.key | gpg --dearmor --yes --output /etc/apt/keyrings/opennebula.gpg

RUN echo "deb [signed-by=/etc/apt/keyrings/opennebula.gpg] https://downloads.opennebula.io/repo/${OPENNEBULA_VERSION}/Debian/${DEBIAN_VERSION} stable opennebula" > /etc/apt/sources.list.d/opennebula.list

RUN apt-get update

RUN apt-get -y install opennebula-tools

RUN apt-get -y install python3-click

ENV PS1='\u@\h:\w\$\040'

WORKDIR /root
