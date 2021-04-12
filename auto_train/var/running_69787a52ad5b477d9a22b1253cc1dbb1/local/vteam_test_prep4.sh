#!/bin/bash

# Hub-5 Eval 2000 data preparation 
# Author:  Arnab Ghoshal (Jan 2013)

# To be run from one directory above this script.

# The input is two directory names (possibly the same) containing the 
# 2000 Hub5 english evaluation test set and transcripts, which are
# respectively: LDC2002S09  LDC2002T43
# e.g. see
# http://www.ldc.upenn.edu/Catalog/catalogEntry.jsp?catalogId=LDC2002S09
# http://www.ldc.upenn.edu/Catalog/CatalogEntry.jsp?catalogId=LDC2002T43
#
# Example usage:
# local/eval2000_data_prep_edin.sh /exports/work/inf_hcrc_cstr_general/corpora/hub5/2000 /exports/work/inf_hcrc_cstr_general/corpora/hub5/2000/transcr
# The first directory ($sdir) contains the speech data, and the directory
# $sdir/english/ must exist.
# The second directory ($tdir) contains the transcripts, and the directory
# $tdir/reference must exist; in particular we need the file
# $tdir/reference/hub5e00.english.000405.stm

if [ $# -ne 5 ]; then
  echo "Usage: "`basename $0`" /path/to/vteam_data /path/to/trans.txt pcm_or_wav samplerate corpusname"
  echo "See comments in the script for more details"
  exit 1
fi

sdir=$1
tdir=$2
ext=$3
srate=$4

. path.sh 
parent_name=test
iitest=$5

#itest="${parent_name}_${iitest}"
itest="${parent_name}/${iitest}"
dir=data/local/$itest
if [ -d $dir ];then
 rm -rf $dir
 mkdir -p $dir
else
 mkdir -p $dir
fi

echo "prep vteam test(${itest}) data start."

if [ -f "${sdir}/wavelist.txt" ];then
cat ${sdir}/wavelist.txt |sort - >$dir/w0.scp
n=`wc -l $dir/w0.scp`
echo "find $n wav."
else
echo "no such file ${sdir}/wavelist.txt"
exit
fi
sort $tdir >$dir/text0

python local/pylib/check_text_and_scp.py --in-scp=$dir/w0.scp --out-scp=$dir/w.scp --in-text=$dir/text0 --out-text=$dir/text
cp $dir/w.scp $dir/pcm.scp
#python local/pylib/check_exists.py
addwaveheader=$Kaldibin/add-wave-header 
if [ $ext = "pcm" -o $ext = "all" ];then
  #addwaveheader=$KALDI_ROOT/src/featbin/add-wave-header
  [ ! -x $addwaveheader ] \
    && echo "Could not execute the AddWaveHeader program at $addwaveheader" && exit 1;
fi


if [ $ext = "pcm" ]; then
echo "pcm format."
awk -v addwaveheader=$addwaveheader -v samplerate=$srate '{
   printf($1" "addwaveheader" --skip-bytes=0 --sample-rate="samplerate" "$2" |\n"); 
}' < $dir/pcm.scp |sort - >$dir/wav.scp || exit 1;
elif [ $ext = "wav" ]; then
echo wav format
awk -v addwaveheader=$addwaveheader -v samplerate=$srate '{
  printf($1" "addwaveheader" --skip-bytes=44 --sample-rate="samplerate" "$2" |\n"); 
}' < $dir/w.scp |sort - >$dir/wav.scp || exit 1;
else
echo "all format"
awk -v addwaveheader=$addwaveheader -v samplerate=$srate '{
  printf($1" "addwaveheader" --skip-bytes=0 --sample-rate="samplerate" "$2" |\n"); 
}' < $dir/pcm.scp |sort - >$dir/pcm2.scp || exit 1;
awk -v addwaveheader=$addwaveheader -v samplerate=$srate '{
  printf($1" "addwaveheader" --skip-bytes=44 --sample-rate="samplerate" "$2" |\n"); 
}' < $dir/w.scp |sort - >$dir/wav2.scp || exit 1;
cat $dir/pcm2.scp $dir/wav2.scp | sort - > $dir/wav.scp
fi

n=`wc -l $dir/wav.scp`
echo "find $n wav after check."
#sort $tdir >$dir/text

# create an utt2spk file that assumes each conversation side is
# a separate speaker.
awk '{print $1,$1;}' $dir/wav.scp > $dir/utt2spk  
sort -k 2 $dir/utt2spk | utils/utt2spk_to_spk2utt.pl  >$dir/spk2utt || exit 1;

# cp $dir/segments $dir/segments.tmp
# awk '{x=$3-0.05; if (x<0.0) x=0.0; y=$4+0.05; print $1, $2, x, y; }' \
#   $dir/segments.tmp > $dir/segments

dest=data/$itest
echo "cp resource to $dest"
mkdir -p $dest
for x in wav.scp text utt2spk spk2utt; do
  cp $dir/$x $dest/$x
done

echo "prep vteam test(${itest}) done."
