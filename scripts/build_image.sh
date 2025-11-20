#!/bin/bash

USERNAME="hsiangjenli"
IMAGE_NAME="$USERNAME/mcp-pofile"
date_tag=$(date +%Y-%m-%d)

docker build --no-cache -t $IMAGE_NAME:$date_tag --push .
docker tag $IMAGE_NAME:$date_tag $IMAGE_NAME:latest
docker push $IMAGE_NAME:latest
