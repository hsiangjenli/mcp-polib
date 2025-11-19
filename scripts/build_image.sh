#!/bin/bash

date_tag=$(date +%Y-%m-%d)

docker build --no-cache -t python-mcp-template:$date_tag .
docker tag python-mcp-template:$date_tag python-mcp-template:latest
