#!/bin/bash

# Ensure sudo is available
apt install -y sudo

# Update package lists
sudo apt update

# Install required packages
sudo apt install -y ffmpeg
sudo apt install -y libglib2.0-0 libsm6 libxrender1 libxext6
sudo apt install -y libgl1
sudo apt-get install -y graphviz


# Install Node.js and Mermaid CLI
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
sudo apt-get install -y nodejs
sudo npm install -g @mermaid-js/mermaid-cli

# Start your FastAPI app
uvicorn api:app --host 0.0.0.0 --port 8000