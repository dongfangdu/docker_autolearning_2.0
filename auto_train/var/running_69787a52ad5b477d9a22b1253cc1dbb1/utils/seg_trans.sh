#!/bin/bash

if [ $# != 4 ]; then
    echo "usage: seg_trans.sh /path/dict /path/trans /path/wavelist /path/dst_dir/"
    exit 1
fi
. path.sh

dict=$1
trans=$2
wavelist=$3
dst_dir=$4

tmp_dir=$dst_dir/seg_trans_tmp
mkdir -p $tmp_dir

cat $trans | sed 's/\t/ /g' | sed 's/ /\t/' | awk '{if(NF>1){print}}' > $tmp_dir/trans.deal.txt

#word segmentaion
cat $tmp_dir/trans.deal.txt | awk -F '\t' '{print $2}' | \
sed 's: (noise) ::g' | sed 's:(noise)::g' | sed 's: (overlap) ::g' | sed 's: (\/overlap) ::g' | \
sed 's:(overlap)::g' | sed 's:(\/overlap)::g' | sed 's: (sil) ::g' | sed 's:(sil)::g' | \
tr [A-Z] [a-z] | sed 's:,::g' | sed 's:?::g' | sed 's:!::g' | \
awk '{str="";for(i=1;i<=NF;i++){if($i~/[a-zA-Z]/){str=str" "$i" "}else{str=str$i}};print str}' | \
sed 's/^ //;s/  / /g' | \
segword2 $dict $tmp_dir/trans.deal.content.txt

awk -F '\t' '{print $1}' $tmp_dir/trans.deal.txt > $tmp_dir/trans.deal.id.txt

paste $tmp_dir/trans.deal.id.txt $tmp_dir/trans.deal.content.txt > $tmp_dir/trans.tempSegment.txt

#remove oov
awk 'NR==FNR{a[$1]=$1}NR!=FNR{for(i=2;i<=NF;i++){if ($i in a == 0){print $1;break}}}' $dict $tmp_dir/trans.tempSegment.txt \
| awk 'NR==FNR{a[$1]=$1;b[$1]=$0}NR!=FNR{if($1 in a == 0){ c[$1]=$0}}END{if(length(c)<=0){for(i in b){print b[i]}}else{for(i in c){print c[i]}}}' - $tmp_dir/trans.tempSegment.txt | sed 's/  / /g' >  $tmp_dir/trans.noOOVSegment.txt

#trans && wave filtering
select_from_uttlist.pl $wavelist $tmp_dir/trans.noOOVSegment.txt $dst_dir/trans.segment.txt
select_from_uttlist.pl $dst_dir/trans.segment.txt $wavelist $dst_dir/wave.filtered.txt

if [ $(wc -l ${dst_dir}/trans.segment.txt | awk '{print $1}') -eq 0 ]
  then
    echo "segmenting transription failed!"
    exit 2
fi
rm -rf $tmp_dir

