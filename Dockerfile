FROM debian:11

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update

RUN apt-get -y install gnupg wget apt-transport-https systemd

RUN wget -q -O- https://downloads.opennebula.io/repo/repo2.key | apt-key add -

RUN echo "deb https://downloads.opennebula.io/repo/6.6.0/Debian/11 stable opennebula" > /etc/apt/sources.list.d/opennebula.list

RUN apt-get update

RUN apt-get -y install opennebula-tools

WORKDIR /root
