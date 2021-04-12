# -*- coding: utf-8 -*-
# ===============================================================
# This file used to split origin dataset to Train and Test
# 1. Appoint dataset type which split by speaker
# 2. Read split radio in XML config
# 3. Split
# 4. Arange Folder
# ================================================================
import os
import sys

if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding('utf-8')
import argparse
from pydub import AudioSegment
import xml.etree.ElementTree as ET
import xml.etree.cElementTree
import auto_find_path
import traceback
import shutil
import random

import logging
import codecs

folder_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
log_path = folder_path + '/../../bin/am_training_pipeline/log_autotrain/train.log'

LOG_FORMAT = '[%(asctime)s] [%(levelname)s - %(lineno)d] -- [%(message)s]'
my_logger = logging.getLogger(__name__)
my_logger.setLevel(level=logging.DEBUG)
fh = logging.FileHandler(log_path, encoding='utf8')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt=LOG_FORMAT)
fh.setFormatter(formatter)
my_logger.addHandler(fh)

GLOBAL_RATE = -1


# =============================
# Auxiliary Function
# =============================
# def check_folder(path, name):
#     folder_list = [file for file in os.listdir(path) if os.path.isdir(arange_slash(path, file))]
#     out_num = 0
#     flag = True
#     for folder in folder_list:
#         for ele in os.listdir(arange_slash(path, folder))
#             if re.search(name+'_*', folder):
#                 if eval(ele.split('_')[-1]) >= out_num:
#                     flag = False
#     return flag

def check_slash(str):
    return '/'.join(str.split('\\'))


def arange_slash(*args):
    return ('/'.join([arg for arg in args])).replace('//', '/')


# =============================
# Body Function
# =============================
def obtain_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputxmlfilename', action='store', required=True, help='input global xml')
    parser.add_argument('--inputtype', action='store', default='False',
                        help='control whether mv dataset')  # {True: mv, False: no mv}
    inputargs = parser.parse_args()
    return inputargs


def try_mkdir(inputargs):
    '''
    This func used to parse XML file and appoint folder for saving dataset
    '''
    tree = xml.etree.cElementTree.ElementTree()
    tree.parse(inputargs.inputxmlfilename)
    root = tree.getroot()
    iter_xml = root.find('corpus').attrib

    corpus_path = iter_xml['corpus']
    corpus_name = iter_xml['name']
    corpus_type = iter_xml['type']
    tagged_type = iter_xml['Tagged_type']
    corpus_trans = iter_xml['trans_name']
    corpus_wave = iter_xml['wave_name']

    corpus_trans_path = arange_slash(corpus_path, corpus_name, corpus_trans, corpus_type)
    corpus_wave_path = arange_slash(corpus_path, corpus_name, corpus_wave)
    save_root_path = arange_slash(corpus_path, corpus_name, 'dataparsed')
    save_wav_path, save_txt_path = arange_slash(save_root_path, 'wav'), arange_slash(save_root_path, 'txt')

    try:
        os.mkdir(save_root_path)
    except:
        pass
    try:
        os.mkdir(save_wav_path)
    except:
        pass
    try:
        os.mkdir(save_txt_path)
    except:
        pass

    try:
        os.mkdir(arange_slash(corpus_path, corpus_name, 'filtered'))
    except:
        pass
    try:
        os.mkdir(arange_slash(corpus_path, corpus_name, 'trained'))
    except:
        pass

    return save_root_path, save_wav_path, save_txt_path, corpus_trans_path, corpus_wave_path, tagged_type


def split_func(corpus_trans_path, corpus_wave_path, save_wav_path, save_txt_path):
    print('---------- Split Dataset Begin -----------')
    my_logger.info(u'------Split Dataset Begin-------')
    try:
        Split_Data(txt_path=corpus_trans_path, wav_path=corpus_wave_path, save_wav_path=save_wav_path,
                   save_txt_path=save_txt_path).main()
        print('---------- Split Dataset Successfully ----------')
        my_logger.info(u'-------Split Dataset Successfully-------')
    except:
        print('----------- Split Dataset Failed -------------')
        my_logger.error(u'Split Dataset Failed!!!')
        traceback.print_exc()


def auto_path(inputargs, save_wav_path, save_txt_path):
    print('----------Auto Path Begin--------------')
    my_logger.info(u'-------Auto Path Begin-------')
    try:
        Auto_Path_Element = auto_find_path.Auto_Path(inputargs, save_wav_path, save_txt_path).main()
        print('----------Auto Path Successfully-----------')
        my_logger.info(u'-------Auto Path Successfully-------')
    except:
        print('---------Auto Path Failed ------------')
        my_logger.info(u'Auto Path Failed!!!')
        traceback.print_exc()


class Split_Data():
    def __init__(self, txt_path, wav_path, save_wav_path, save_txt_path):
        '''
        :param txt_path: corpus + name + trans_name + type
        :param wav_path: corpus + name + wave_name
        '''
        self.txt_path = txt_path
        self.wav_path = wav_path
        self.save_wav_path = save_wav_path
        self.save_txt_path = save_txt_path

    def data_dict(self, txt_path, wav_path):
        '''
        This func used to generate dict that connect certain txt and wav
        :return: {txt_file_path: wav_file_path}
        '''
        txt_list = sorted([arange_slash(txt_path, file) for file in os.listdir(txt_path)])
        wav_list = [arange_slash(wav_path, x.split('/')[-1][:-3] + 'wav') for x in txt_list]
        # wav_list = sorted([arange_slash(wav_path, file) for file in os.listdir(wav_path)])
        return dict(zip(txt_list, wav_list))

    def split_by_txt(self, txt, wav, save_txt_path, save_wav_path):
        '''
        :param txt: single txt file
        '''
        # wav_element = AudioSegment.from_file(wav, format = 'wav')
        try:
            wav_element = AudioSegment.from_file(wav, format='wav')
        except:
            wav_element = AudioSegment.from_file(wav, format='s16le')
        with codecs.open(txt, encoding='utf-8') as f:
            lines = f.readlines()
            head_line = lines.pop(0)
            count = len(str(len(lines)))
            i = 1
            while (lines):
                line = lines.pop(0)
                if line == '\r\n' or line == '\n':
                    continue
                if line.split('\t')[2] == '有效':
                    save_single_txt_path = arange_slash(save_txt_path,
                                                        os.path.basename(txt)[:-4] + '_' + '%.{}d'.format(
                                                            count) % i + '.txt')
                    save_single_wav_path = arange_slash(save_wav_path,
                                                        os.path.basename(wav)[:-4] + '_' + '%.{}d'.format(
                                                            count) % i + '.wav')

                    # --------save wav -------------
                    duration_begin = eval(line.split('\t')[-1].split('][')[0][1:])
                    duration_end = eval(line.split('\t')[-1].split('][')[1][:-3])

                    sub_wav_element = wav_element[1000 * duration_begin: 1000 * duration_end]
                    sub_wav_element.export(save_single_wav_path, format='wav')

                    if (os.path.getsize(save_single_wav_path) == 44) or (
                            ('tagged' not in wav) and ('zhe' not in wav) and (random.uniform(0, 1) < GLOBAL_RATE)):
                        os.system('rm %s' % (save_single_wav_path))
                    else:

                        # --------save txt ------------
                        with codecs.open(save_single_txt_path, 'w', encoding='utf-8') as nf:
                            nf.write(head_line)
                            write_content = ['0001'] \
                                            + line.split('\t')[1:-1] \
                                            + ['[0.000][{:.3f}]\r\n'.format(duration_end - duration_begin)]

                            nf.write('\t'.join(write_content))

                    i += 1

    def main(self):
        data_dict = self.data_dict(self.txt_path, self.wav_path)
        for key, value in data_dict.items():
            self.split_by_txt(key, value, self.save_txt_path, self.save_wav_path)


if __name__ == '__main__':
    inputargs = obtain_args()
    save_root_path, save_wav_path, save_txt_path, corpus_trans_path, corpus_wave_path, tagged_type = try_mkdir(
        inputargs)
    if inputargs.inputtype == 'False':
        if tagged_type == "STANDARD_LONG":
            split_func(corpus_trans_path, corpus_wave_path, save_wav_path, save_txt_path)
            auto_path(inputargs, save_wav_path, save_txt_path)
        else:
            auto_path(inputargs, corpus_wave_path, corpus_trans_path)
    else:
        generate_path = os.path.dirname(inputargs.inputxmlfilename)
        try:
            in_path = ET.parse(arange_slash(generate_path, 'data_parse_bak.xml')).getroot().find('corpus')
            in_path = in_path.attrib['ossuploadrootpath']
        except:
            raise Exception('XML file name not is data_parse_bak.xml, Please check out')
        [shutil.move(file, in_path) for file in [save_wav_path, save_txt_path]]
        # command_1 = 'mv %s %s'%(save_wav_path, in_path)
        # command_2 = 'mv %s %s'%(save_txt_path, in_path)
        # os.system(command_1)
        # os.system(command_2)
