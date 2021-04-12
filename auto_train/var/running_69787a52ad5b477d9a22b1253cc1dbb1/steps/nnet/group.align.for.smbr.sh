[ $# -gt 0 ] && echo "$0 $@"  # Print the command line for logging

[ -f path.sh ] && . ./path.sh # source the path.
. parse_options.sh || exit 1;

if [ $# != 4 ]; then
   echo "usage: $0 <data-dir> <in-align-dir> <out-align_dir> <split-num>"
   echo "e.g.:  $0 data/train exp_old/tri1_ali exp/tri1_ali 50"
   exit 1;
fi

data=$1
in_dir=$2
out_dir=$3
newNj=$4

  
split_data.sh $data $newNj
newSdata=$data/split$newNj
flist_dir=$out_dir/finalList
mkdir -p $flist_dir
mkdir -p $out_dir/log
#cat $in_dir/ali.*.scp > $out_dir/all.ali.scp
#cat $in_dir/lat.*.scp > $out_dir/all.lat.scp
rm -f $flist_dir/featNnet1.txt $flist_dir/framesPerArk.txt $out_dir/log/copy.log
for i in `seq 1 $newNj`;do
select_from_uttlist.pl $newSdata/$i/feats.scp $out_dir/all.ali.scp $flist_dir/newali.$i.scp
select_from_uttlist.pl $newSdata/$i/feats.scp $out_dir/all.lat.scp $flist_dir/newlat.$i.scp
copy-feats scp,p:$newSdata/$i/feats.scp ark:$flist_dir/fbank.$i.ark >> $out_dir/log/copy.log 2>&1
copy-int-vector scp,p:$flist_dir/newali.$i.scp ark:$flist_dir/newali.$i.ark >> $out_dir/log/copy.log 2>&1
lattice-copy scp,p:$flist_dir/newlat.$i.scp ark:$flist_dir/newlat.$i.ark >> $out_dir/log/copy.log 2>&1
echo $flist_dir/fbank.$i.ark $flist_dir/newlat.$i.ark $flist_dir/newali.$i.ark >> $flist_dir/featNnet1.txt
feat-to-len scp,p:$newSdata/$i/feats.scp >> $flist_dir/framesPerArk.txt
done

