# -*- coding:utf-8 -*-

class Config:
    def __init__(self):
        pass

    ENH_MODEL_PATH = "/home/user/linjr/enh_tmp_data/speech_enhancement/segan_mix_7"
    NOISE_DATA_PATH = "/home/user/linjr/enh_tmp_data/speech_enhancement/noise/mix_noise.wav"
    LOG_PATH = "/home/user/linjr/enh_tmp_data/speech_enhancement/log"

    # ORIGIN_DATA_PATH = "/home/user/wangyd/train_tmp_data"
    DENOISE_PATH = "/home/user/linjr/enh_tmp_data/Test_data/denoise"
    ADD_NOISE_PATH = "/home/user/linjr/enh_tmp_data/Test_data/add_noise"
    INCREASE_VOL_PATH = "/home/user/linjr/enh_tmp_data/Test_data/increase_vol"
    VOICE_CONVERSION_PATH = "/home/user/linjr/enh_tmp_data/Test_data/voice_convert"

    FFMPEG_PATH = "/home/user/linjr/online_label_api_dev/bin/ffmpeg"

config = Config
