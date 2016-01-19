#!/bin/sh
#
# Using a build script, because the Docker plugin does not work!
# Alway pull-in the latest parent so we are up to date with latest patch releases
#
# Usage: ./build.sh [push]
#
# The [push] option should only be used for Jenkins builds and not local builds.
#
DOCKER_IMAGE_NAME=docker-registry.finalist.nl:5000/surfnet/ooapi-poc
DOCKER_IMAGE_VERSION=1.0

display_usage() {
	echo "Builds the Docker image $DOCKER_IMAGE_NAME:$DOCKER_IMAGE_VERSION" 
	echo "\nUsage:\n$0 admin-password external-url \n" 
	echo "admin-password: The password to set for the admin user"
	} 

if [  $# -le 0 ]; then 
	display_usage
	exit 1
fi 

docker rmi --force=true $DOCKER_IMAGE_NAME:$DOCKER_IMAGE_VERSION
docker build --pull=true --force-rm=true --rm=true --build-arg ADMIN_PASSWORD=$1 -t $DOCKER_IMAGE_NAME:$DOCKER_IMAGE_VERSION $(dirname $0)

if [ "$1" = "push" ]; then
	docker push $DOCKER_IMAGE_NAME:$DOCKER_IMAGE_VERSION
fi


                                                                                                                
