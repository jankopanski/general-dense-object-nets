#!/bin/bash

set -euxo pipefail

apt-get update
apt-get install --no-install-recommends \
  terminator \
  tmux \
  vim \
  gedit \
  git \
  openssh-client \
  unzip \
  htop \
  libopenni-dev \
  apt-utils \
  usbutils \
  dialog \
  python-pip \
  python-dev \
  ffmpeg \
  nvidia-settings \
  cmake-curses-gui \
  libyaml-dev

pip install --upgrade pip==9.0.3
pip install -U setuptools

apt-get -y install ipython ipython-notebook
pip install \
  jupyter \
  opencv-python \
  plyfile \
  pandas \
  tensorflow \
  future \
  typing