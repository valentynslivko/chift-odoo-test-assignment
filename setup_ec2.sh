#!/bin/bash

# exit on error
set -e

# update package index
sudo apt-get update -y

# install dependencies
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# add docker's official gpg key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# set up the repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# install docker engine
sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# start and enable docker
sudo systemctl start docker
sudo systemctl enable docker

# add current user to docker groups
sudo usermod -aG docker $USER

# print version
docker --version
docker compose version

echo "EC2 setup complete. Restart the instance for group changes to take effect."
