#!/bin/env bash
function doStop() {

  docker stop autolearning_2.0
  docker system prune
}

doStop
