# -*- coding: utf8 -*-
import logging
import sys

import os
import traceback

from app.libs.enhance import configure as conf
from app.libs.enhance.libs.enums import EnhanceTypeEnum
from app.libs.enhance.libs.path_utils import get_enhance_tools_dir
from app.libs.enhance.libs.utils import get_uuid, get_json
from multiprocessing import Pool, cpu_count

def convert_to_stand(self, file_path):
    # ffmpeg_path = conf.config.FFMPEG_PATH
    # os.system("echo y|%s -i '%s' -f wav -ar 16000 -acodec pcm_s16le '%s' >/home/user/linjr/aaa.log" %(ffmpeg_path, file_path, file_path))
    os.system("echo y|ffmpeg -i '%s' -f wav -ar 16000 -acodec pcm_s16le '%s' >/home/user/linjr/aaa.log" %(file_path, file_path))

class DataEnhancement:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level=logging.INFO)
        self.log_path = conf.config.LOG_PATH
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)
        handler = logging.FileHandler(os.path.join(self.log_path, "log.txt"))
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        self.logger.addHandler(handler)
        self.logger.addHandler(console)

    def adjust_volume(self, ori_data_path):
        self.logger.info(u"训练数据预处理：自适应音量调节")
        volup_uuid = get_uuid()
        self.logger.info(u"音量调节全局ID：{}".format(volup_uuid))
        status_code = 2000000
        try:
            save_data_path = os.path.join(conf.config.INCREASE_VOL_PATH, volup_uuid, "data/wav")
            # save_data_path = os.path.join("/home/user/linjr/enh_tmp_data/Test_data/increase_vol", volup_uuid, "data/wav")
            # "/home/user/linjr/enh_tmp_data/Test_data/increase_vol"
            #audio_volup = "python {} {} {}".format("adj_vol.py", ori_data_path, save_data_path)
            #os.system(audio_volup)
            cmd = '{executable} {script} {ori_data_path} {save_data_path}'.format(
                executable=sys.executable,
                script=os.path.join(get_enhance_tools_dir(), 'adj_vol.py'),
                ori_data_path=ori_data_path,
                save_data_path=save_data_path
            )
            return_code = os.system(cmd)
            if return_code != 0:
                raise
            self.logger.info(u"音量调节完成")
        except Exception as e:
            self.logger.error(traceback.print_exc())
            self.logger.error(u"音量调节失败: {}".format(e.message))
            status_code = 5000300
            save_data_path = None
            return status_code, ori_data_path, save_data_path
        return status_code, ori_data_path, save_data_path

    def reduce_noise(self, ori_data_path):
        self.logger.info(u"训练数据预处理：音频去噪")
        denoise_uuid = get_uuid()
        self.logger.info(u"音频去噪全局ID：{}".format(denoise_uuid))
        status_code = 2000000

        # 去噪
        try:
            save_data_path = os.path.join(conf.config.DENOISE_PATH, denoise_uuid, "data/wav")
            # audio_denoise = "python {} {} {}".format("denoise.py", ori_data_path, save_data_path)
            # os.system(audio_denoise)
            cmd = '{executable} {script} {ori_data_path} {save_data_path}'.format(
                executable=sys.executable,
                script=os.path.join(get_enhance_tools_dir(), 'denoise.py'),
                ori_data_path=ori_data_path,
                save_data_path=save_data_path
            )
            return_code = os.system(cmd)
            if return_code != 0:
                raise
            self.logger.info(u"音频去噪初步完成，等待bit转换")

        except Exception as e:
            self.logger.error(u"音频去噪失败: {}".format(e.message))
            status_code = 5000100
            save_data_path = None
            return status_code, ori_data_path, save_data_path

        # bit转换
        try:
            # bit_trans = "sh {} {}".format("bit_trans.sh", save_data_path)
            # os.system(bit_trans)
            cmd = '{executable} {script} {save_data_path}'.format(
                executable='sh',
                script=os.path.join(get_enhance_tools_dir(), 'bit_trans.sh'),
                # ori_data_path=ori_data_path,
                save_data_path=save_data_path
            )
            return_code = os.system(cmd)
            if return_code != 0:
                raise
            self.logger.info(u"完成bit转换，音频去噪全部完成")
        except Exception as e:
            self.logger.error(u"bit转换失败: {}".format(e.message))
            status_code = 5000101
            save_data_path = None
            return status_code, ori_data_path, save_data_path

        return status_code, ori_data_path, save_data_path

    def add_noise(self, ori_data_path):
        self.logger.info(u"训练数据预处理：音频加噪")
        addnoise_uuid = get_uuid()
        self.logger.info(u"音频加噪全局ID：{}".format(addnoise_uuid))
        status_code = 2000000

        # 加噪
        try:
            save_data_path = os.path.join(conf.config.ADD_NOISE_PATH, addnoise_uuid, "data/wav")
            # audio_addnoise = "python {} {} {}".format("add_noise.py", ori_data_path, save_data_path)
            # os.system(audio_addnoise)
            cmd = '{executable} {script} {ori_data_path} {save_data_path}'.format(
                executable=sys.executable,
                # executable='python',
                script=os.path.join(get_enhance_tools_dir(), 'add_noise.py'),
                ori_data_path=ori_data_path,
                save_data_path=save_data_path
            )
            return_code = os.system(cmd)
            if return_code != 0:
                raise
            self.logger.info(u"音频加噪完成")
        except Exception as e:
            self.logger.error(u"音频加躁失败: {}".format(e.message))
            status_code = 5000200
            save_data_path = None
            return status_code, ori_data_path, save_data_path

        return status_code, ori_data_path, save_data_path

    def voice_convert(self, ori_data_path):
        self.logger.info(u"训练数据预处理：声音转换")
        addnoise_uuid = get_uuid()
        self.logger.info(u"音频加噪全局ID：{}".format(addnoise_uuid))
        status_code = 2000000

        # 转音
        try:
            save_data_path = os.path.join(conf.config.VOICE_CONVERSION_PATH, addnoise_uuid, "data/wav")
            # audio_addnoise = "python {} {} {}".format("add_noise.py", ori_data_path, save_data_path)
            # os.system(audio_addnoise)
            cmd = '{executable} {script} {ori_data_path} {save_data_path}'.format(
                executable=sys.executable,
                # executable='python',
                script=os.path.join(get_enhance_tools_dir(), 'convert_random.py'),
                ori_data_path=ori_data_path,
                save_data_path=save_data_path
            )
            return_code = os.system(cmd)
            if return_code != 0:
                raise
            self.logger.info(u"声音转换完成")
        except Exception as e:
            self.logger.error(u"声音转换失败: {}".format(e.message))
            status_code = 5000400
            save_data_path = None
            return status_code, ori_data_path, save_data_path
        return status_code, ori_data_path, save_data_path
        # try:
        #     self.logger.info(u"音频格式转换开始")
        #     save_data_path = os.path.join(conf.config.VOICE_CONVERSION_PATH, addnoise_uuid, "data/wav")
        #     # pool = Pool(50)
        #     # cores = cpu_count()
        #     for file in os.listdir(save_data_path):
        #         file_path = os.path.join(save_data_path, file)
        #         os.system("echo y|ffmpeg -i '%s' -f wav -ar 16000 -acodec pcm_s16le '%s' >/dev/null 2>&1" %(file_path, file_path))
        #         # self.logger.info(file_path)
        #     #     pool.apply_async(convert_to_stand, file_path)
        #     # pool.close()
        #     # pool.join()
        #     self.logger.info(u"音频格式转换完成")
        # except Exception as e:
        #     self.logger.error(u"音频格式转换失败: {}".format(e.message))
        #     status_code = 5000500
        #     save_data_path = None
        #     return status_code, ori_data_path, save_data_path


    def enhance_data(self, mode, ori_data_path):
        self.logger.info(u"训练数据预处理开始 ***")
        if mode not in [e.value for e in EnhanceTypeEnum]:
            self.logger.error(u"输入的增强模式不存在，请选择正确的数据增强模式：{}".format(
                '; '.join(['{} for {}'.format(e.value, e.name) for e in EnhanceTypeEnum])
            ))
            res_json = get_json(4000001)
            return res_json

        if not os.path.exists(ori_data_path):
            self.logger.info(u"输入路径不存在，请输入正确的文件夾路径")
            res_json = get_json(4000002)
            return res_json

        if not os.path.isdir(ori_data_path):
            self.logger.info(u"输入路径不是文件夹，请输入正确的文件夾路径")
            res_json = get_json(4000003)
            return res_json

        res = (500000, None, None)
        try:
            if mode == EnhanceTypeEnum.REDUCE_NOISE.value:
                res_adj_vol = self.adjust_volume(ori_data_path)
                res = self.reduce_noise(res_adj_vol[2])
            elif mode == EnhanceTypeEnum.ADD_NOISE.value:
                res_adj_vol = self.adjust_volume(ori_data_path)
                res = self.add_noise(res_adj_vol[2])
            elif mode == EnhanceTypeEnum.ADJUST_VOLUME.value:
                res = self.adjust_volume(ori_data_path)
            elif mode == EnhanceTypeEnum.VOICE_CONVERSION.value:
                res_adj_vol = self.adjust_volume(ori_data_path)
                res = self.voice_convert(res_adj_vol[2])
            else:
                pass

        except Exception as e:
            self.logger.error(u"音频增强失败: {}".format(e.message))

        res_json = get_json(res[0], res[1], res[2])
        return res_json
