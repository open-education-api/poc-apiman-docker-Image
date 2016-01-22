#!/bin/sh
#
# Alway pull-in the latest parent so we are up to date with latest patch releases
#
# Usage: ./build.sh
#
DOCKER_IMAGE_NAME=surfnet/ooapi-apiman
DOCKER_IMAGE_VERSION=latest

docker rmi --force=true $DOCKER_IMAGE_NAME:$DOCKER_IMAGE_VERSION
docker build --pull=true --force-rm=true --rm=true -t $DOCKER_IMAGE_NAME:$DOCKER_IMAGE_VERSION $(dirname $0)
