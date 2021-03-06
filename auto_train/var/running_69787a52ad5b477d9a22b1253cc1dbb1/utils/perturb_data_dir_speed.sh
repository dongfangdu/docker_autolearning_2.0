#!/bin/bash 

# Copyright 2013  Johns Hopkins University (author: Daniel Povey)
#           2014  Tom Ko
# Apache 2.0

# This script operates on a directory, such as in data/train/,
# that contains some subset of the following files:
#  wav.scp
#  spk2utt
#  utt2spk
#  text
#
# It generates the files which are used for perturbing the speed of the original data.

. utils/parse_options.sh

if [ $# != 3 ]; then
  echo "Usage: perturb_data_dir_speed.sh <warping-factor> <srcdir> <destdir>"
  echo "e.g.:"
  echo " $0 0.9 data/train_si284 data/train_si284p"
  exit 1
fi

export LC_ALL=C

factor=$1
srcdir=$2
destdir=$3
label="sp"
spk_prefix=$label$factor"-"
utt_prefix=$label$factor"-"

#check is sox on the path
which sox &>/dev/null
! [ $? -eq 0 ] && echo "sox: command not found" && exit 1;

if [ ! -f $srcdir/utt2spk ]; then
  echo "$0: no such file $srcdir/utt2spk" 
  exit 1;
fi

set -e;
set -o pipefail

mkdir -p $destdir

cat $srcdir/utt2spk | awk -v p=$utt_prefix '{printf("%s %s%s\n", $1, p, $1);}' > $destdir/utt_map
cat $srcdir/spk2utt | awk -v p=$spk_prefix '{printf("%s %s%s\n", $1, p, $1);}' > $destdir/spk_map

cat $srcdir/utt2spk | utils/apply_map.pl -f 1 $destdir/utt_map  | \
  utils/apply_map.pl -f 2 $destdir/spk_map >$destdir/utt2spk

utils/utt2spk_to_spk2utt.pl <$destdir/utt2spk >$destdir/spk2utt

if [ -f $srcdir/segments ]; then
  # also apply the spk_prefix to the recording-ids.
  cat $srcdir/wav.scp | awk -v p=$spk_prefix '{printf("%s %s%s\n", $1, p, $1);}' > $destdir/reco_map

  utils/apply_map.pl -f 1 $destdir/utt_map <$srcdir/segments | \
    utils/apply_map.pl -f 2 $destdir/reco_map | \
      awk -v factor=$factor \
        '{printf("%s %s %.2f %.2f\n", $1, $2, $3/factor, $4/factor);}' >$destdir/segments

  utils/apply_map.pl -f 1 $destdir/reco_map <$srcdir/wav.scp | sed 's/| *$/ |/' | \
    awk -v factor=$factor \
        '{wid=$1; $1=""; if ($NF=="|") {print wid $_ " sox -t wav - -t wav - speed " factor " |"} 
          else {print wid " sox -t wav" $_ " -t wav - speed " factor " |"}}' > $destdir/wav.scp
  if [ -f $srcdir/reco2file_and_channel ]; then
    utils/apply_map.pl -f 1 $destdir/reco_map <$srcdir/reco2file_and_channel >$destdir/reco2file_and_channel
  fi
  
  rm $destdir/reco_map 2>/dev/null
else # no segments->wav indexed by utterance.
  if [ -f $srcdir/wav.scp ]; then
    utils/apply_map.pl -f 1 $destdir/utt_map <$srcdir/wav.scp | sed 's/| *$/ |/' | \
     awk -v factor=$factor \
       '{wid=$1; $1=""; if ($NF=="|") {print wid $_ " sox -t wav - -t wav - speed " factor " |"} 
         else {print wid " sox -t wav" $_ " -t wav - speed " factor " |"}}' > $destdir/wav.scp
  fi
fi

if [ -f $srcdir/text ]; then
  utils/apply_map.pl -f 1 $destdir/utt_map <$srcdir/text >$destdir/text
fi
if [ -f $srcdir/spk2gender ]; then
  utils/apply_map.pl -f 1 $destdir/spk_map <$srcdir/spk2gender >$destdir/spk2gender
fi


rm $destdir/spk_map $destdir/utt_map 2>/dev/null
echo "$0: generated speed-perturbed version of data in $srcdir, in $destdir"
utils/validate_data_dir.sh --no-feats $destdir
