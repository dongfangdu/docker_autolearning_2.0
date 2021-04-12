#!/usr/bin/env bash
#export PATH=$PATH:/opt/jdk1.8.0_101/bin:/root/bin:/root/.local/bin:/opt/jdk1.8.0_101/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/home/user/chenms/srilm/bin:/home/user/chenms/srilm/bin/i686-m64:/root/bin
#export PATH=$PATH:/home/user/linjr/venv/auto_train/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin
#echo $PATH >> /home/user/linjr/train_path.txt
#nohup /home/user/linjr/venv/auto_train/bin/python /home/user/linjr/auto_train/src/run_auto_train.py >> /home/user/linjr/auto_train/auto_train.log &
#source /home/user/linjr/venv/auto_train/bin/activate && python /home/user/linjr/auto_train/src/run_auto_train.py
#source /home/user/linjr/venv/auto_train/bin/activate
while [ True ]; do
    python /home/user/linjr/auto_test/src/auto_test.py
    python /home/user/linjr/auto_train/src/run_auto_train.py
done
