import os
import numpy as np
import random
# from preprocess import *
import sys
import pyworld as pw
from concurrent.futures import ThreadPoolExecutor
import scipy
import librosa
from multiprocessing import Pool, cpu_count

def conversion(data_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # executor = ThreadPoolExecutor(max_workers=100)
    pool = Pool(50)
    cores = cpu_count()
    # print(cores)
    for file in os.listdir(data_dir):
        # convert(data_dir, output_dir, file)
        pool.apply_async(convert, (data_dir, output_dir, file))
    pool.close()
    pool.join()
    #     executor.map(convert, (data_dir, output_dir, file))
    # executor.shutdown(wait=True)

def wav_convert(i, j, f0_converted, sp, ap, fs, output_dir, file_ele):
    sp_like = np.zeros_like(sp)
    for idx in xrange(sp_like.shape[1]):
        if (idx / j) < sp_like.shape[1]:
            sp_like[:, idx] = sp[:, int(idx/j)]
        else:
            sp_like[:, idx] = sp[:, idx]
    y = pw.synthesize(f0_converted, sp_like, ap, fs)
    y = y.astype(np.int16)
    scipy.io.wavfile.write(os.path.join(output_dir, file_ele[:-4] + "_{}_{}.wav".format(i, j)), fs, y)
    # librosa.output.write_wav(os.path.join(output_dir, file_ele[:-4] + "_{}_{}.wav".format(i, j)), y, fs)

def convert(data_dir, output_dir, file):
    if file.endswith(".wav"):
        # print file
        fs, x = scipy.io.wavfile.read(os.path.join(data_dir, file))
        # wav = wav_padding(wav=wav, sr=sampling_rate, frame_period=frame_period, multiple=4)
        x = x.astype(np.float64)
        f0, t = pw.harvest(x, fs)
        sp = pw.cheaptrick(x, f0, t, fs)  # extract smoothed spectrogram
        ap = pw.d4c(x, f0, t, fs)  # extract aperiodicity
        i = 0
        for i in range(85, 320, 25):
            s = np.float64(i) / np.mean(f0)
            f0_converted = f0 * s
            if i < 200:
                j = round((random.sample(np.arange(0.7, 0.9, 0.05), 1))[0], 2)
                wav_convert(i, j, f0_converted, sp, ap, fs, output_dir, file)
            elif i >= 200 and i < 300:
                j = round((random.sample(np.arange(1.1, 1.3, 0.05), 1))[0], 2)
                wav_convert(i, j, f0_converted, sp, ap, fs, output_dir, file)
            else:
                j = round((random.sample(np.arange(1.3, 1.5, 0.05), 1))[0], 2)
                wav_convert(i, j, f0_converted, sp, ap, fs, output_dir, file)

if __name__ == '__main__':
    origin_data_path = sys.argv[1]
    save_data_path = sys.argv[2]
    conversion(data_dir=origin_data_path,output_dir=save_data_path)


