#!/bin/bash

# Switchboard-1 training data preparation customized for Edinburgh
# Author:  Arnab Ghoshal (Jan 2013)

# To be run from one directory above this script.

## The input is some directory containing the switchboard-1 release 2
## corpus (LDC97S62).  Note: we don't make many assumptions about how
## you unpacked this.  We are just doing a "find" command to locate
## the .pcm files.

## The second input is optional, which should point to a directory containing
## Switchboard transcriptions/documentations (specifically, the conv.tab file).
## If specified, the script will try to use the actual speaker PINs provided
## with the corpus instead of the conversation side ID (Kaldi default). We
## will be using "find" to locate this file so we don't make any assumptions
## on the directory structure. (Peng Qi, Aug 2014)

. path.sh

#check existing directories
if [ $# != 5 ]; then
  echo "Usage: vteam_data_prep.sh /path/to/wavelist /path/to/trans.txt pcm_or_wav samplerate train/test"
  exit 1;
fi

src_wave=$1
src_trans=$2
ext=$3
samplerate=$4
parent_name=$5

#itest="${parent_name}_${iitest}"
itest="${parent_name}"
#itest=`basename $1`
dir=data/$itest
mkdir -p $dir

echo prep vteam $parent_name data start.

addwaveheader=add-wave-header
if [ $ext = "pcm" -o $ext = "all" ];then
#addwaveheader=$KALDI_ROOT/src/featbin/add-wave-header
[ ! -x $addwaveheader ] \
  && echo "Could not execute the AddWaveHeader program at $addwaveheader" && exit 1;
fi

# Trans directory check
if [ ! -f $src_trans ]; then
  (
    echo "no such file: $src_trans"
    exit
  )
fi

if [ ! -f $src_wave ];then
  echo "no such file $src_wave"
  exit
fi

export LC_ALL=C;

cp $src_trans  $dir/text

if [ $ext = 'wav' ];then
awk -v addwaveheader=$addwaveheader -v srate=$samplerate '{
  printf($1" "addwaveheader" --skip-bytes=44 --sample-rate="srate" "$2" |\n");
}' < $src_wave  >$dir/wav.scp || exit 1;
elif [ $ext = 'ark' ]; then
awk -v addwaveheader=$addwaveheader -v srate=$samplerate '{
  printf($1" "$2"\n");
}' < $src_wave  >$dir/wav.scp || exit 1;
else
awk -v addwaveheader=$addwaveheader -v srate=$samplerate '{
  printf($1" "addwaveheader" --skip-bytes=0 --sample-rate="srate" "$2" |\n");
}' < $src_wave >$dir/wav.scp || exit 1;
fi

awk '{print $1" "$1;}' $dir/wav.scp > $dir/utt2spk \
  || exit 1;
sort -k 2 $dir/utt2spk | utils/utt2spk_to_spk2utt.pl > $dir/spk2utt || exit 1;

for f in spk2utt utt2spk wav.scp text; do
  if [ ! -s $dir/$f ]; then
    echo "failed to generate $f"
  fi
done
echo vteam $parentname data preparation succeeded.

