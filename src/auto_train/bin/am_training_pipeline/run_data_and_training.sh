#!/bin/sh
#whether to run data process and dnn training
#run_dp="true"
#run_dpf="true"
#run_train="true"
#run_test="true"
#fill_flag="true"

#setting asrp src location
#local_src="/home/admin/20181115_ctc/dcs_model_train_package_general_11122018/dcs_model_train_package/am/code/asrp_am/src"

#AM pipeline local xml dir
#local_xml_dir=${PWD}

#Test src localtion
#test_src="/home/admin/20181115_ctc/dcs_model_train_package_general_11122018/dcs_model_train_package/test/asr-tools-new/src"

# obtain args
run_dp=`python ../../src/read_global_RunShell.py --para run_dp`
echo " run_dp is:" $run_dp
run_dpf=`python ../../src/read_global_RunShell.py --para run_dpf`
echo " run_dpf is:" $run_dpf
run_train=`python ../../src/read_global_RunShell.py --para run_train`
echo " run_train is:" $run_train
run_test=`python ../../src/read_global_RunShell.py --para run_test`
echo " run_test is:" $run_test
fill_flag=`python ../../src/read_global_RunShell.py --para fill_flag`
echo " fill_flag is:" $fill_flag
local_src=`python ../../src/read_global_RunShell.py --para local_src`
echo " local_src is:" $local_src
local_xml_dir=`python ../../src/read_global_RunShell.py --para local_xml_dir`
echo " local_xml_dir is:" $local_xml_dir
test_src=`python ../../src/read_global_RunShell.py --para test_src`
echo " test_src is:" $test_src

python write_to_global.py
# manually fill path
condition1()
{
	echo "======================Data Parsing begins========================="
	if [ $run_dp == "true" ]
    	then
		python $local_src/asrp.py --inputxmlfilename $local_xml_dir/data_parse.xml --printlogcode
	fi

	echo "=======================Data Parsing ends=========================="

	echo "======================Data Process and Filter begins========================="
	if [ $run_dpf == "true" ]
    	then
		python $local_src/asrp.py --inputxmlfilename $local_xml_dir/data_process_filter.xml --printlogcode --debug
	fi

	echo "=======================Data  Process and Filter ends=========================="

	echo "======================DNN Training begins========================="
	if [ $run_train == "true" ]
    	then
		python $local_src/asrp.py --inputxmlfilename $local_xml_dir/dcs_am_pipeline.xml --printlogcode --debug
	fi
	echo "=======================DNN Training ends=========================="
}

# auto fill path
condition2()
{
	# obtain args
	run_dp=`python $folder_path/../../src/read_global_RunShell.py --para run_dp`
	#echo " run_dp is:" $run_dp
	run_dpf=`python $folder_path/../../src/read_global_RunShell.py --para run_dpf`
	#echo " run_dpf is:" $run_dpf
	run_train=`python $folder_path/../../src/read_global_RunShell.py --para run_train`
	#echo " run_train is:" $run_train
	run_test=`python $folder_path/../../src/read_global_RunShell.py --para run_test`
	#echo " run_test is:" $run_test
	local_src=`python $folder_path/../../src/read_global_RunShell.py --para local_src`
	#echo " local_src is:" $local_src
	local_xml_dir=`python $folder_path/../../src/read_global_RunShell.py --para local_xml_dir`
	#echo " local_xml_dir is:" $local_xml_dir
	test_src=`python $folder_path/../../src/read_global_RunShell.py --para test_src`
	#echo " test_src is:" $test_src

        `python $folder_path/../../tools/data_process/split_dataset.py --inputxmlfilename $local_xml_dir/global_config.xml`
	echo "======================Data Parsing begins========================="
        if [ $run_dp == "true" ]
        then
                python $local_src/asrp.py --inputxmlfilename $local_xml_dir/data_parse_bak.xml --printlogcode && python $folder_path/../../tools/data_process/split_dataset.py --inputxmlfilename $local_xml_dir/global_config.xml --inputtype True
        fi

        echo "=======================Data Parsing ends=========================="

        echo "======================Data Process and Filter begins========================="
        if [ $run_dpf == "true" ]
        then
                #python $local_src/asrp.py --inputxmlfilename $local_xml_dir/data_process_filter_bak.xml --printlogcode --debug
                python $folder_path/../../src/Dpf_server.py
        fi

        echo "=======================Data  Process and Filter ends=========================="

        echo "======================DNN Training begins========================="
        if [ $run_train == "true" ]
        then
                #python $local_src/asrp.py --inputxmlfilename $local_xml_dir/dcs_am_pipeline_bak.xml --printlogcode --debug
                python $folder_path/../../src/Train_server.py
		echo "yjyjs123"|sudo -S sh $folder_path/clean_feature_bak.sh
		`python $folder_path/write_to_sql.py`
        fi
        echo "=======================DNN Training ends=========================="

}

if [ $fill_flag == "true" ]; then
    python $folder_path/write_to_global.py && condition2
else
    echo "fill_flag  is  false!!"
fi
