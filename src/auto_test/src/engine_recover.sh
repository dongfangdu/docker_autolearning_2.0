#!/bin/bash
echo "please ensure the followed files what you just used such as vad_1600.cfg,processor.json and server.json were backed up "
echo "please ensure the default/models dir was recovered"
service_path="/home/admin/v2.6_16K/service"
log_file=$(cd $(dirname $0); pwd)/engine_recover.log
root_psword="yjyjs123"
cd $service_path
function recover_file() {
	echo "start recover files and files" >> $log_file
	cp resource/asr/vad_16000.cfg resource/realtime/vad
	cp resource/asr/*.json  resource/asr/default/conf
	cp -r resource/asr/models resource/asr/default
}

function restart() {
	echo "`date +%d:%H:%M` Restart Engine" >> $log_file
	echo $root_psword|sudo -S sh ./bin/stop.sh;sleep 2m;echo $root_psword|sudo -S sh ./bin/start.sh;sleep 10s
	until `ss -anl | grep 8680 > /dev/null`;do
		echo "Engine restarting..." >> $log_file
		sleep 1m
	done
	echo "`date +%d:%H:%M` Engine Started Successfully" >> $log_file
}
read -p "you have baked up the files above:(y/n)" answer
if [ $answer="y" ];then
	recover_file
	restart
	fi
