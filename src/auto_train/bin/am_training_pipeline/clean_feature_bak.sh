#!/bin/sh

folder_path=$(cd `dirname $0`; pwd)

echo "yjyjs123"|sudo -S mv ./feature_align_lattice_label_train/ $folder_path/../../corpus/data/feature_label_save/feature_align_lattice_label_train_`date '+%Y%m%d|%H:%M:%S'`
usage=`ls -l $folder_path/../../corpus/data/feature_label_save|wc -l`
if [ $usage -ge 6 ]
then
ls -ltr $folder_path/../../corpus/data/feature_label_save |grep feature|awk '{print $9}'|head -1 > $folder_path/../../corpus/data/feature_label_save/delet_list.txt
for i in `cat $folder_path/../../corpus/data/feature_label_save/delet_list.txt`
do
echo "yjyjs123"|sudo -S rm -rf $folder_path/../../corpus/data/feature_label_save/$i
done
echo "complete remove feature_label_bak file!"
date
fi

echo "yjyjs123"|sudo -S rm -rf $folder_path/asrprun
echo "complete remove the folder asrprun !"

usage=`ls -l $folder_path/../../corpus/data|wc -l`
if [ $usage -ge 7 ]
then
ls -ltr $folder_path/../../corpus/data|awk '{print $9}'|head -2 > $folder_path/../../corpus/data/delet_traindata_list.txt
for i in `cat $folder_path/../../corpus/data/delet_traindata_list.txt`
do
echo "yjyjs123"|sudo -S rm -rf $folder_path/../../corpus/data/$i
done
echo "complete remove train_data file!"
date
fi
