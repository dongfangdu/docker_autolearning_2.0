#!/bin/sh


#setting asrp src location
local_src="/home/youranme/dcs_model_train_package/code/asrp_dcs_am/src/"

#AM pipeline local xml dir
local_xml_dir=${PWD}


echo "======================AM Training Resource checking begins========================="
python $local_src/asrp.py --inputxmlfilename $local_xml_dir/training_resource_checker.xml --printlogcode --debug
echo "=======================AM Training Resource checking ends=========================="
