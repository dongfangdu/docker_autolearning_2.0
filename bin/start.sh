#!/bin/env bash
BIN_HOME="$( cd "$( dirname "$0"  )" && pwd  )"
BASE_HOME="$( cd "$( dirname "$BIN_HOME"  )" && pwd  )"

function readINI()
{
 FILENAME=$1; SECTION=$2; KEY=$3
 RESULT=`awk -F '=' '/\['$SECTION'\]/{a=1}a==1&&$1~/'$KEY'/{print $2;exit}' $FILENAME`
 echo $RESULT
}

#ENGINE_PATH="/home/admin/v2.6.3_16K"
ENGINE_PATH=$(readINI $BASE_HOME/auto_test/cfg/config.ini Engine engine)
ENGINE_PATH=${ENGINE_PATH:4}
echo $ENGINE_PATH


function doFirst() {

  nvidia-docker run --name autolearning_2.0 \
    -v $BASE_HOME/dcs_model_train_package_general_06052019_2.6.3_16k:/home/user/linjr/dcs_model_train_package_general_06052019_2.6.3_16k \
    -v $BASE_HOME/enh_tmp_data:/home/user/linjr/enh_tmp_data \
    -v $BASE_HOME/tmp_model:/home/user/linjr/tmp_model \
    -v $BASE_HOME/tools:/home/user/linjr/tools \
    -v $BASE_HOME/train_tmp_data:/home/user/linjr/train_tmp_data \
    -v $BASE_HOME/auto_test/cfg:/home/user/linjr/auto_test/cfg \
    -v $BASE_HOME/auto_test/doc:/home/user/linjr/auto_test/doc \
    -v $BASE_HOME/auto_test/log:/home/user/linjr/auto_test/log \
    -v $BASE_HOME/auto_test/output:/home/user/linjr/auto_test/output \
    -v $BASE_HOME/auto_train/cfg:/home/user/linjr/auto_train/cfg \
    -v $BASE_HOME/auto_train/logs:/home/user/linjr/auto_train/logs \
    -v $BASE_HOME/auto_train/var:/home/user/linjr/auto_train/var \
    -v $BASE_HOME/auto_train/corpus/model:/home/user/linjr/auto_train/corpus/model \
    -v $BASE_HOME/auto_train/xml/data_parse_temp.xml:/home/user/linjr/auto_train/bin/am_training_pipeline/data_parse_temp.xml \
    -v $BASE_HOME/auto_train/xml/data_process_filter_temp.xml:/home/user/linjr/auto_train/bin/am_training_pipeline/data_process_filter_temp.xml \
    -v $BASE_HOME/auto_train/xml/dcs_am_pipeline_temp.xml:/home/user/linjr/auto_train/bin/am_training_pipeline/dcs_am_pipeline_temp.xml \
    -v $BASE_HOME/online_label_api_dev/cfg/db_base.ini:/home/user/linjr/online_label_api_dev/cfg/db_base.ini \
    -v $BASE_HOME/online_label_api_dev/cfg/configure.py:/home/user/linjr/online_label_api_dev/src/app/configure.py \
    -v $BASE_HOME/online_label_api_dev/logs:/home/user/linjr/online_label_api_dev/logs \
    -v $ENGINE_PATH:$ENGINE_PATH \
    -v /usr/bin/docker:/usr/bin/docker \
    -v /var/run/docker.sock:/var/run/docker.sock \
	-d -it autolearning:2.0 bash\
    #sh /home/user/linjr/auto_train/bin/run_test.sh
    #python /home/user/linjr/auto_train/src/run_auto_train.py

}

doFirst
