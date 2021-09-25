#!/bin/bash
# Part of COMP90024 Project Team members are
# Ziyuan Xiao (940448)
# Pengyu Mu(890756)
# Dechao Sun (980546)
# Seehoi Chow(980301)
# Yuexin Li (959634)

app="webserver"

docker build -t ${app} .
docker run -p 5000:5000 ${app}
