#!/bin/bash

cv_size=$1
src_dir=$2
dst_dir=$3
task_name=$4
proc_num=$5

if [ $# != 5 ]; then
  echo "usage:$0 data_size_cv src_dir(include featNnet1.txt framesPerArk.txt) dst_dir Warmup/CeTrain/SmbrTrain process_num"
  exit 1;
fi

echo "Begin making train & cv data for $task_name!"

for f in featNnet1.txt framesPerArk.txt;do
  if [ ! -s $src_dir/$f ];then
    echo "Please check $src_dir/$f !"
    exit 2;
  fi
done

mkdir -p $dst_dir

arkFrames=$src_dir/framesPerArk.txt
cv_arkNum=0
cv_frames=$(echo $cv_size | awk '{printf "%d", $1*360000}')
cv_cur_frames=0
for i in $(cat $arkFrames);do
  let cv_cur_frames=${cv_cur_frames}+$i
  let cv_arkNum=${cv_arkNum}+1
  if [[ ${cv_cur_frames} -ge ${cv_frames} ]];then
    break;
  fi
done || exit 1;

if [[ ${cv_arkNum} -eq $(wc -l $arkFrames | awk '{print $1}') ]];then
  echo "The validation ark number is the same as total ark number, please reduce the validation data set."
  exit 2;
fi

ncopy=1
if [ $cv_arkNum -lt $proc_num ];then
  ncopy=$(echo $proc_num | awk -v n=$cv_arkNum '{print ($0-1)/n+1}')
fi

dataList=$src_dir/featNnet1.txt
rm -f $dst_dir/valArkList_${task_name}.txt 
for i in `seq 1 $ncopy`;do
  head -n ${cv_arkNum}  $dataList >> $dst_dir/valArkList_${task_name}.txt
done || exit;
tail -n +$((${cv_arkNum}+1)) $dataList > $dst_dir/arkList_${task_name}.txt || exit;

echo "Succeed making train & cv data for $task_name!"

