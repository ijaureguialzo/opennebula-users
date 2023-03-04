ARG DEBIAN_VERSION

FROM debian:${DEBIAN_VERSION}

ARG DEBIAN_VERSION
ARG OPENNEBULA_VERSION

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update

RUN apt-get -y install gnupg wget apt-transport-https systemd

RUN wget -q -O- https://downloads.opennebula.io/repo/repo2.key | apt-key add -

RUN echo "deb https://downloads.opennebula.io/repo/${OPENNEBULA_VERSION}/Debian/${DEBIAN_VERSION} stable opennebula" > /etc/apt/sources.list.d/opennebula.list

RUN apt-get update

RUN apt-get -y install opennebula-tools

RUN apt-get -y install python3-pip

RUN pip3 install click

WORKDIR /root
