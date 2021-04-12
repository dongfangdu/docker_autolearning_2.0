# -*- coding: utf8 -*-
import sys
import wave

import numpy as np
import os

#import configure as conf
from app.libs.enhance import configure as conf


def wave_info(data_path):
    f = wave.open(data_path)
    nframes = f.getnframes()
    f_str_data = f.readframes(nframes)
    f_wave_data = np.fromstring(f_str_data, dtype=np.int16)
    f.close()
    return nframes, f_wave_data


def wave_synthesis(wave_data, Output_wave):
    sf = wave.open(Output_wave, "wb")
    sf.setnchannels(nchannels)
    sf.setsampwidth(sampwidth)
    sf.setframerate(framerate)
    sf.writeframes(wave_data.tostring())
    sf.close()
    #print "noisy data have been synthetized"


def syn_data(noisydata, origin_data_path, save_data_path):
    noisy_nframes, noisy_wave_data = wave_info(noisydata)
    if not os.path.exists(save_data_path):
        os.makedirs(save_data_path)
    wav_list = os.listdir(origin_data_path)
    lenth = 0
    for wav_ele in wav_list:
        cleanwave = os.path.join(origin_data_path, wav_ele)
        noisywave = os.path.join(save_data_path, wav_ele)
        clean_nframes, wave_data = wave_info(cleanwave)
        fina_syndata = wave_data + noisy_wave_data[lenth: lenth + clean_nframes]
        wave_synthesis(fina_syndata, noisywave)
        lenth += clean_nframes


if __name__ == "__main__":
    origin_data_path = sys.argv[1]
    save_data_path = sys.argv[2]
    nchannels, sampwidth, framerate = 1, 2, 16000
    noisydata = conf.config.NOISE_DATA_PATH
    syn_data(noisydata, origin_data_path, save_data_path)
