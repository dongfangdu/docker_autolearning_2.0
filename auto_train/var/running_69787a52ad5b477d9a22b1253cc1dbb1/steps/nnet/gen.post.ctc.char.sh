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

# End configuration options.

[ $# -gt 0 ] && echo "$0 $@"  # Print the command line for logging

[ -f path.sh ] && . ./path.sh # source the path.
. parse_options.sh || exit 1;

if [ $# != 3 ]; then
   echo "usage: $0 <data-dir> <lang-dir> <align-dir>"
   echo "e.g.:  $0 data/train data/lang exp/tri1_ali"
   echo "main options (for others, see top of script file)"
   echo "  --config <config-file>                           # config containing options"
   echo "  --nj <nj>                                        # number of parallel jobs"
   echo "  --cmd (utils/run.pl|utils/queue.pl <queue opts>) # how to run jobs."
   exit 1;
fi

data=$1
lang=$2
dir=$3

mkdir -p $dir/log
echo $nj > $dir/num_jobs
sdata=$data/split$nj
[[ -d $sdata && $data/feats.scp -ot $sdata ]] || split_data.sh $data $nj || exit 1;

tokens=$lang/tokens.txt
lex=$lang/lexicon.lex
lexIdMap=$lang/lexicon_id.lex

# Check that files exist
for f in $sdata/1/feats.scp $sdata/1/text; do
  [ ! -f $f ] && echo "$0: missing file $f" && exit 1;
done

[[ ! -f $tokens && ! -f $lex ]] && [ ! -f $lexIdMap ] && echo "$0: must either have $tokens and $lex, or $lexIdMap." && exit 1;


echo "$0: aligning data '$data', putting alignments in '$dir'"


if [ $stage -le 0 ]; then
  for i in `seq 1 $nj`;do
    echo $sdata/${i}/text | python  $dir/trans2id.py  $tokens $lex $lexIdMap>$dir/new.${i}.trans
  done
  #$cmd JOB=1:$nj $dir/log/trans2id.JOB.log \
  #  echo $sdata/JOB/text | python  $dir/trans2id.py  $tokens $lex >$dir/new.JOB.trans
fi 

if [ $stage -le 1 ]; then
  $cmd JOB=1:$nj $dir/log/ali2post.JOB.log \
    ali-to-post ark:$dir/new.JOB.trans ark,scp:$dir/newpost.JOB.ark,$dir/newpost.JOB.scp
fi
