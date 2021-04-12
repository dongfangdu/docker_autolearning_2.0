#!/bin/env bash
docker rmi -f $(docker images | grep autolearning | tr -s ' ' | cut -d ' ' -f 3)
