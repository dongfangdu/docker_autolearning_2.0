#!/bin/env bash
BINHOME="$( cd "$( dirname "$0"  )" && pwd  )"
BASEHOME="$( cd "$( dirname "$BINHOME"  )" && pwd  )"


function doLoad() {
	for imgName in `find $BASEHOME/images -type f -name "autolearning*tar"`
	do
		echo "load $imgName"
		docker load --input $imgName
	done
	
}


doLoad
