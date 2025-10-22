#!/bin/sh
set -e
export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get -y upgrade

apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libpango1.0-dev \
    libcairo2-dev \
    curl \
    netcat-traditional \
    inetutils-traceroute \
    iputils-ping \
    ca-certificates

apt-get clean
rm -rf /var/lib/apt/lists/*