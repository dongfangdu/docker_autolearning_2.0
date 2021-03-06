#!/bin/bash
# Copyright 2012-2013 Brno University of Technology (Author: Karel Vesely)
# Apache 2.0

# Aligns 'data' to sequences of transition-ids using Neural Network based acoustic model.
# Optionally produces alignment in lattice format, this is handy to get word alignment.

# Begin configuration section.
nj=4
cmd=run.pl
max_jobs_run=""
cmd=$cmd" "$max_jobs_run
stage=0
# Begin configuration.
scale_opts="--transition-scale=1.0 --acoustic-scale=0.1 --self-loop-scale=0.1"
beam=10
retry_beam=40
nnet_forward_opts="--no-softmax=true --prior-scale=1.0"
align_to_lats=false # optionally produce alignment in lattice format
lats_decode_opts="--acoustic-scale=1.4 --beam=17 --lattice-beam=10"
lats_graph_scales="--transition-scale=1.0 --self-loop-scale=0.1"
net_forward_ctc_blank_scale="--ctc-blank-scale=1.3"
boost_opt="1.0"
optional_silence="1"

use_gpu="no" # yes|no|optionaly # TODO: support gpu
# End configuration options.

[ $# -gt 0 ] && echo "$0 $@"  # Print the command line for logging

[ -f path.sh ] && . ./path.sh # source the path.
. parse_options.sh || exit 1;

if [ $# != 4 ]; then
   echo "usage: $0 <data-dir> <lang-dir> <src-dir> <align-dir>"
   echo "e.g.:  $0 data/train data/lang exp/tri1 exp/tri1_ali"
   echo "main options (for others, see top of script file)"
   echo "  --config <config-file>                           # config containing options"
   echo "  --nj <nj>                                        # number of parallel jobs"
   echo "  --cmd (utils/run.pl|utils/queue.pl <queue opts>) # how to run jobs."
   exit 1;
fi

data=$1
lang=$2
srcdir=$3
dir=$4


gpu_nj=
##########When use GPU, force setting nj to 2############
if [ $use_gpu == "yes" ];then
  gpu_nj=2
  split_data.sh $data $gpu_nj || exit 1;
fi
########################################################

mkdir -p $dir/log
echo $nj > $dir/num_jobs
sdata=$data/split$nj
[[ -d $sdata && $data/feats.scp -ot $sdata ]] || split_data.sh $data $nj || exit 1;

cp $srcdir/{tree,final.mdl} $dir || exit 1;

# Select default locations to model files
nnet=$srcdir/adv.model.ce.mdl
class_frame_counts=$srcdir/ali_train_pdf.counts
feature_transform=$srcdir/final.fe.feature_transform
model=$dir/final.mdl

# Check that files exist
for f in $sdata/1/feats.scp $sdata/1/text $lang/L.fst $lang/T.fst $nnet $model $feature_transform $class_frame_counts; do
  [ ! -f $f ] && echo "$0: missing file $f" && exit 1;
done


# PREPARE FEATURE EXTRACTION PIPELINE
# import config,
cmvn_opts=
delta_opts=
D=$srcdir
[ -e $D/norm_vars ] && cmvn_opts="--norm-means=true --norm-vars=$(cat $D/norm_vars)" # Bwd-compatibility,
[ -e $D/cmvn_opts ] && cmvn_opts=$(cat $D/cmvn_opts)
[ -e `pwd`/delta_order ] && delta_opts="--delta-order=$(cat `pwd`/delta_order)" # Bwd-compatibility,
[ -e $D/delta_opts ] && delta_opts=$(cat $D/delta_opts)
#
# Create the feature stream,
feats="ark:copy-feats scp:$sdata/JOB/feats.scp ark:- |"
# apply-cmvn (optional),
[ ! -z "$cmvn_opts" -a ! -f $sdata/1/cmvn.scp ] && echo "$0: Missing $sdata/1/cmvn.scp" && exit 1
[ ! -z "$cmvn_opts" ] && feats="$feats apply-cmvn $cmvn_opts --utt2spk=ark:$sdata/JOB/utt2spk scp:$sdata/JOB/cmvn.scp ark:- ark:- |"
# add-deltas (optional),
[ ! -z "$delta_opts" ] && feats="$feats add-deltas $delta_opts ark:- ark:- |"
# nnet-forward,
#feats="$feats nnet-forward $nnet_forward_opts --feature-transform=$feature_transform --class-frame-counts=$class_frame_counts --use-gpu=$use_gpu $nnet ark:- ark:- |"
#

echo "$0: aligning data '$data' using nnet/model '$srcdir', putting alignments in '$dir'"

# Map oovs in reference transcription,
oov=`cat $lang/oov.int` || exit 1;
tra="ark:utils/sym2int.pl --map-oov $oov -f 2- $lang/words.txt $sdata/JOB/text|";
#mdl="nnet2-boost-silence --boost=$boost_opt $optional_silence $nnet - |"
feats="$feats nnet-forward $net_forward_ctc_blank_scale --no-softmax=true --prior-scale=1.0 --feature-transform=$feature_transform --class-frame-counts=$class_frame_counts --use-gpu=$use_gpu $nnet ark:- ark:- |"
# We could just use align-mapped in the next line, but it's less efficient as it compiles the
# training graphs one by one.
if [ $stage -le 0 ]; then
  train_graphs="ark:compile-train-graphs-ctc $dir/tree $dir/final.mdl $lang/L.fst $lang/T.fst '$tra' ark:- |"
  if [ $use_gpu == "no" ];then
    rm -f $dir/ali.*.scp $dir/ali.*.ark
    $cmd JOB=1:$nj $dir/log/align.JOB.log \
      compile-train-graphs-ctc $dir/tree $dir/final.mdl $lang/L.fst $lang/T.fst "$tra" ark:- \| \
      align-compiled $scale_opts --beam=$beam --retry-beam=$retry_beam $model ark:- \
        "$feats" "ark,scp,f:$dir/ali.JOB.ark,$dir/ali.JOB.scp" || exit 1;
  fi
fi

# Optionally align to lattice format (handy to get word alignment)
if [ $stage -le 1 ]; then
  echo "$0: aligning also to lattices"
  rm -f $dir/lat.*.ark $dir/lat.*.scp
  $cmd JOB=1:$nj $dir/log/lat.JOB.log \
    latgen-faster $lats_decode_opts --max-mem=20000000 --max-active=5000 --word-symbol-table=$lang/words.txt $dir/final.mdl \
      $lang/HCLG.fst "$feats" ark,scp,f:$dir/lat.JOB.ark,$dir/lat.JOB.scp || exit 1;
fi

#if [ $stage -le 2 ]; then
#  newNj=50
#  split_data.sh $data $newNj
#  newSdata=$data/split$newNj
#  flist_dir=$dir/finalList
#  mkdir -p $flist_dir
#  cat $dir/ali.*.scp > $dir/all.ali.scp
#  cat $dir/lat.*.scp > $dir/all.lat.scp
#  rm -f $flist_dir/featNnet1.txt $flist_dir/framesPerArk.txt $dir/log/copy.log
#  for i in `seq 1 $newNj`;do
#    select_from_uttlist.pl $newSdata/$i/feats.scp $dir/all.ali.scp $flist_dir/newali.$i.scp
#    select_from_uttlist.pl $newSdata/$i/feats.scp $dir/all.lat.scp $flist_dir/newlat.$i.scp
#    copy-feats scp,p:$newSdata/$i/feats.scp ark:$flist_dir/fbank.$i.ark >> $dir/log/copy.log 2>&1
#    copy-int-vector scp,p:$flist_dir/newali.$i.scp ark:$flist_dir/newali.$i.ark >> $dir/log/copy.log 2>&1
#    lattice-copy scp,p:$flist_dir/newlat.$i.scp ark:$flist_dir/newlat.$i.ark >> $dir/log/copy.log 2>&1
#    echo $flist_dir/fbank.$i.ark $flist_dir/newlat.$i.ark $flist_dir/newali.$i.ark >> $flist_dir/featNnet1.txt
#    feat-to-len scp,p:$newSdata/$i/feats.scp >> $flist_dir/framesPerArk.txt
#  done
#fi

echo "succeed generating lattice"
