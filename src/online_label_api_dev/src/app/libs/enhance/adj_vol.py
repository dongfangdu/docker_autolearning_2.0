# coding=utf-8
from pydub import AudioSegment
import os
import sys

def adj_vol(data):
    if data.rms*5 <= 200:
        pass
    else:
        while 200 <= data.rms*5 < 5000:
            data += 0.2
        while data.rms*5 > 30000:
            data -= 0.2
    return data

def main(datas):
    Outsound = AudioSegment.empty()
    nframes = len(datas) / 2000
    if len(datas) > 2000:
        if len(datas) % 2000 == 0:
            tailsound = AudioSegment.empty()
        else:
            tailsound = datas[2000 * nframes:]
        #print tailsound.rms*5
        tailsound = adj_vol(tailsound)
        #print tailsound.rms*5
        for i in xrange(nframes):
            midsound = datas[i*2000:((i+1)*2000)]
            midsound = adj_vol(midsound)
            Outsound += midsound
        Outsound += tailsound
    else:
        Outsound = adj_vol(datas)
    return Outsound

if __name__ == "__main__":
    #print "123"
    origin_data_path = sys.argv[1]
    save_data_path = sys.argv[2]
    wav_list = os.listdir(origin_data_path)
    if not os.path.exists(save_data_path):
        os.makedirs(save_data_path)
    #print "1234"
    for wav_ele in wav_list:
        if wav_ele.endswith(".wav"):
            #print wav_ele
            wave = os.path.join(origin_data_path, wav_ele)
            sound = AudioSegment.from_file(wave)
            Outsound = main(sound)
            Outsound.export(os.path.join(save_data_path, wav_ele), format="wav")
