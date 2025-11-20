#!/bin/bash

date_tag=$(date +%Y-%m-%d)

docker build --no-cache -t mcp-pofile:$date_tag --output type=docker .
docker tag mcp-pofile:$date_tag mcp-pofile:latest
