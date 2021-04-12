#!/bin/bash
ENH_DATA_PATH="$1"
cd $ENH_DATA_PATH
for sound in `ls *.wav`;do
        sox $sound -b 16 -r 16000 16-$sound; mv 16-$sound $sound
done
