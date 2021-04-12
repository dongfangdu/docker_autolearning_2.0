function Logger(){
# ==================
# $1: Logger type
# $3: Log message
# $3: Log Path
# ==================
    echo "[`date +%Y-%m-%d\ %H:%M:%S`    ] [Autotest_logger:$1]--[abt_engine]:$2" >> $3/Autotest.log
}

function Clean_Init_Image(){
# ==================
# $1: saving log path
# $2: Engine Path
# $3: sudo password
# ==================
#Logger "Clean and Init Image..." $1
    ls $2/service > /dev/null 2>&1
    if [ $? -ne 0 ];then
        Logger "ERROR   " "Clean and Init Image Failed!!" $1
    else
        (cd $2/service; sh ./bin/clean.sh;sleep 2m;
        sh ./bin/init.sh;sleep 1m)
        Logger "INFO    " "clean and init image successful!" $1
    fi
}

function Clear_Log_Data(){
# ===================
# $1: saving log path
# $2: Engine Path
# $3: sudo passwd
# ===================
#Logger "Clear Log and Data..." $1
    if [[ ${2:0:3} == "1.0" ]];then
        (cd ${2:4}/logs || Logger "ERROR   " "clear log and data failed!!" $1;
        rm -rf alisr.log.* speech-alisr-trace.log.*;
        cat /dev/null > alisr.log;
        cat /dev/null > speech-alisr-trace.log;
        rm -rf ../data/*)
    else
        (cd ${2:4}/service/logs/nls-cloud-asr || cd ${2:4}/service/logs/nls-cloud-gateway || Logger "ERROR   " "clear log and data failed!!" $1)
        (cd ${2:4}/service/logs/nls-cloud-asr;
        rm -rf alisr.log.* access.log.* speech-alisr-trace.log.* custom-application.log.* custom-error.log.* application.log.*;
        cat /dev/null > alisr.log;
        cat /dev/null > access.log)
        (cd ${2:4}/service/logs/nls-cloud-gateway;
        rm -rf access.log.* conn-open.log.* task.log.* task-asr.log.* task-ast.log.* error.log.* metrics.log.* sla.log.*;
        cat /dev/null > access.log;
        cat /dev/null > conn-open.log;
        cat /dev/null > task-asr.log;
        cat /dev/null > task-ast.log;
        cat /dev/null > task.log)
    fi
    Logger "INFO    " "clear log and data successful!" $1
} 

function Restart_Server(){
# ===================
# $1: saving log path
# $2: Engine Path
# $3: sudo passwd
# TIME-OUT: 3600s
# ===================
    Logger "DEBUG   " "restart ASR server..." $1
    if [[ ${2:0:3} == "1.0" ]];then
        (cd ${2:4}; sh ./bin/alisr-ctrl.sh restart;sleep 10s)
    else
        (cd ${2:4}/service; sh ./bin/stop.sh;sleep 10s;
        sh ./bin/start.sh)
    fi
    sleep 600s	
    #curr_time=$(date +%s)
    #until `ss -anl | grep 8680 > /dev/null`;do
    #    Logger "DEBUG   " "ASR server restarting..." $1
    #    sleep 1m
    #    end_time=$(date +%s)
    #    if [[ $((end_time-curr_time)) -gt 6000 ]];then
    #        Logger "ERROR   " "restart ASR server failed!!" $1
    #        break
    #    fi
    #done
    #Logger "INFO    " "restart ASR server successful!" $1
}

function Replace_Log(){
# =====================
# $1: saving log path
# $2: sudo passwd
# $3: log.conf path of 2.x Engine need
# =====================
#Logger "Replace Docker Log..." $1
    docker cp $3 nls-cloud-asr:/home/admin/resource/asr/default/conf/log.conf > /dev/null 2>&1
    if [[ $? -ne 0 ]];then
        Logger "ERROR   " "replace docker log failed!!" $1
    else
        Logger "INFO    " "replace docker log successful" $1
    fi
}

function Restart_Docker(){
# =====================
# $1: saving log path
# $2: sudo passwd
# =====================
    Logger "DEBUG   " "restart docker engine..." $1
    docker exec -i -u admin nls-cloud-asr /bin/bash -c "source /home/admin/nls/scripts/env && sv restart speech-alisr" || Logger "ERROR   " "restart docker engine failed!!" $1
    sleep 600s
	
    #curr_time_d=$(date +%s)
    #until `ss -anl | grep 8680 > /dev/null`;do
    #    Logger "DEBUG   " "docker ASR server restarting..." $1
    #    sleep 1m
    #    end_time_d=$(date +%s)
    #    if [[ $((end_time_d-curr_time_d)) -gt 6000 ]];then
    #        Logger "ERROR   /sud" "docker ASR server restart failed!!" $1
    #        break
    #    fi
    #done
    #Logger "INFO    " "docker ASR server restart successful!" $1
}

function Stop_Server(){
# =================
# $1: saving log path
# $2: Engine Path
# $3: sudo passwd
# ==================
    Logger "DEBUG   " "stop ASR server..." $1
    if [[ ${2:0:3} == "1.0" ]];then
        (cd ${2:4} && sh ./bin/alisr-ctrl.sh stop) > /dev/null 2>&1
        if [ $? -ne 0 ];then
            Logger "ERROR   " "stop ASR server 1.0 failed!!" $1
        fi
    else
        (cd ${2:4}/service && sh ./bin/stop.sh) > /dev/null 2>&1
        if [ $? -ne 0 ];then
            Logger "ERROR   " "stop ASR server 2.0 failed!!" $1
        fi
        Logger "INFO    " "stop ASR server successful!" $1
    fi
}

		
