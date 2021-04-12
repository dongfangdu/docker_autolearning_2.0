# This Scripth used to conduct 
# - Replace Engine
# - Test New Engine
# of Auto-Test
#
# Making sure of Stopping Server or the Running Server version is corresponds to the one config file appointed
#
# Need Update
# 1. Test Time Record Funciton
# 2. Add check function of whether stop current server
# 3. Add restore function for every step after Restart_Engine encount ERROR
# ===================================================

bin_path=$(cd $(dirname $0); pwd)
cd ${bin_path}
Restart_Engine=`python ./read_global_config.py -f Restart_Engine -s restart`
Engine=`python ./read_global_config.py -f Engine -s engine`
System_Log_Dir=`python ./read_global_config.py -f SystemLog -s saveSelfLogDir`
#System_Log_Dir=$(dirname $bin_path)/${System_Log_Dir#*/}
User_Passwd=`python ./read_global_config.py -f EngineServer -s passwd`
source ./abt_engine.sh

Clear_Log_Data $System_Log_Dir $Engine 
if [[ ${Restart_Engine} == 'True' ]];then
	Stop_Server $System_Log_Dir $Engine
	if [[ ${Engine:0:3} == "2.0" ]];then
		Clean_Init_Image $System_Log_Dir ${Engine:4} $User_Passwd
	fi

	Restart_Server $System_Log_Dir $Engine 

	#if [[ ${Engine:0:3} == "2.0" ]];then
	#	Replace_Log $System_Log_Dir ./log.conf
	#	Restart_Docker $System_Log_Dir 
	#fi
fi
