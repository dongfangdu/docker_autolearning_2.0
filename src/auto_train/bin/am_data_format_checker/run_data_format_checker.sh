#!/bin/sh

#NOTE, the following is for using under linux.

#setting data format checker src location
local_src="/your_path/format_checker/src/"

#local xml dir, assuming you cd-ed to local_xml_dir
local_xml_dir=${PWD}

python $local_src/asrp.py --inputxmlfilename $local_xml_dir/data_format_checker.xml --printlogcode --debug


#If you want to use under window, go to cmd and cd to local_xml_dir, and run the following
# python your_asrp.py_path --inputxmlfilename data_format_checker.xml --printlogcode --debug

