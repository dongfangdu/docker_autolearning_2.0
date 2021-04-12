# -*- coding; utf8 -*-

# This file used to conduct Auto-arange parameters in XML files in Parse, DPF and Training
# ======================================
import logging
import os
import re
import sys
import xml.etree.ElementTree as ET
import xml.etree.cElementTree

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


# ====================
# Auxiliary Func
# ====================
def add_folder(path, name):
    folder_list = [file for file in os.listdir(path) if os.path.isdir(arange_slash(path, file))]
    out_num = 0
    for folder in folder_list:
        for ele in os.listdir(arange_slash(path, folder)):
            if re.search(name + '_*', ele):
                if int(ele.split('_')[-1]) >= out_num:
                    out_num = int(ele.split('_')[-1]) + 1
    return '%.3d' % out_num


def arange_slash(*args):
    return ('/'.join([arg for arg in args])).replace('//', '/')


def check_slash(path):
    return '/'.join(path.split('\\'))


# ====================
# Define Class
# ====================
class Auto_Path():
    def __init__(self, inputargs, save_wav_path, save_txt_path):
        self.inputargs = inputargs
        self.parse_xml = folder_path + '/../../bin/am_training_pipeline/data_parse.xml'
        self.dpf_xml = folder_path + '/../../bin/am_training_pipeline/data_process_filter.xml'
        self.train_xml = folder_path + '/../../bin/am_training_pipeline/dcs_am_pipeline.xml'
        self.test_xml = folder_path + '/../../bin/am_training_pipeline/SimpleRecognitionToolForDcsWithCust.xml'
        self.CeTrain_txt = folder_path + "/../../bin/am_training_pipeline/mw_config_CeTrain.txt"
        self.SmbrTrain_txt = folder_path + "/../../bin/am_training_pipeline/mw_config_SmbrTrain.txt"
        self.save_wav_path = save_wav_path
        self.save_txt_path = save_txt_path

    def read_global_xml(self, inputargs):
        my_logger.info(u'Read Globalxml Begin')
        '''
        This func used to read global xml and return corresponding configs used in XML later
        '''
        tree = xml.etree.cElementTree.ElementTree()
        tree.parse(inputargs.inputxmlfilename)
        root = tree.getroot()
        iter_xml = root.find('corpus').attrib
        #  --------------------------------------------------------
        # self.corpus_path, self.corpus_name = check_slash(iter_xml['corpus']), iter_xml['name']
        self.corpus_path = check_slash(iter_xml['corpus']) if iter_xml['name'] else '/'.join(
            check_slash(iter_xml['corpus']).split('/')[:-1])
        self.corpus_name = iter_xml['name'] if iter_xml['name'] else check_slash(iter_xml['corpus']).split('/')[-1]
        #  --------------------------------------------------------
        self.resource_path = check_slash(iter_xml['resource_package'])
        self.tagged_type = iter_xml['Tagged_type']
        self.trans_name, self.wave_name = iter_xml['trans_name'], iter_xml['wave_name']
        self.train_radio = iter_xml['trainpercentage']
        self.test_radio = '%.1f' % (1 - eval(self.train_radio))
        self.parse_type = iter_xml['type']
        self.license, self.initmodel, self.initfeature = iter_xml['licenseServerList'], \
                                                         iter_xml['initModel'], \
                                                         iter_xml['initFeature']
        self.samplerate = iter_xml['samplerate']
        self.generate_path = os.path.dirname(inputargs.inputxmlfilename)

        self.model_type = iter_xml['Model_Type']
        self.customizationID = root.find('test').attrib['customizationId']

        self.fix_test = root.find('test').attrib['fix_test']
        self.fix_trans = root.find('test').attrib['fix_trans']
        self.fix_wave = root.find('test').attrib['fix_wave']

        self.dpf_train_flag = False if eval(self.train_radio) == 0 else True
        self.dpf_test_flag = False if eval(self.test_radio) == 0 else True

        iter_xml_detail = root.find('TrainDetail').attrib
        self.Ce_Epoch, self.Smbr_Epoch = iter_xml_detail['Ce_Epoch'], iter_xml_detail['Smbr_Epoch']
        self.dp_numinark, self.dp_partsize = iter_xml_detail['dp_numinark'], iter_xml_detail['dp_partsize']
        self.dpf_MinSentenceLengthInMillsecond = iter_xml_detail['dpf_MinSentenceLengthInMillsecond']
        self.dpf_MaxSentenceLengthInMillsecond = iter_xml_detail['dpf_MaxSentenceLengthInMillsecond']
        self.dpf_PeakPointRatio = iter_xml_detail['dpf_PeakPointRatio']
        # self.dpf_werThresholdDrop = iter_xml_detail['dpf_werThresholdDrop']
        self.Ce_maxValHour, self.Smbr_maxValHour = iter_xml_detail['Ce_maxValHour'], iter_xml_detail['Smbr_maxValHour']

        self.fsmn_CE_Batch = iter_xml_detail['fsmn_CE_Batch']
        self.Skip_CE_Length = iter_xml_detail['Skip_CE_Length']
        self.fsmn_ctc_CE_Batch = iter_xml_detail['fsmn_ctc_CE_Batch']
        self.fsmn_ctc_smbr_Batch = iter_xml_detail['fsmn_ctc_smbr_Batch']

        self.local_src = root.find('RunShell').attrib['local_src']
        my_logger.info(u'Read Globalxml Successfully')

    def edit_parse_xml(self):
        my_logger.info(u'Edit parse_bakxml Begin')
        tree_xml = ET.parse(self.parse_xml)
        root_xml = tree_xml.getroot()
        iter_xml = root_xml.find('corpus').attrib
        iter_xml['type'] = self.tagged_type
        # iter_xml['name'] = self.corpus_name if self.corpus_name else 'data'
        iter_xml['name'] = self.corpus_name
        iter_xml['osstranscriptionpath'] = self.save_txt_path
        iter_xml['osswavpath'] = self.save_wav_path

        print(self.corpus_path)
        print(self.corpus_name)
        iter_xml['ossuploadrootpath'] = arange_slash(self.corpus_path, self.corpus_name, 'dataparsed',
                                                     'dataparsed_' + add_folder(arange_slash(self.corpus_path,
                                                                                             self.corpus_name),
                                                                                'dataparsed'))
        iter_xml['trainpercentage'] = self.train_radio
        iter_xml['devtestpercentage'] = self.test_radio

        self.ossuploadrootpath = iter_xml['ossuploadrootpath']

        iter_xml['numinark'] = self.dp_numinark
        iter_xml['partsize'] = self.dp_partsize

        tree_xml.write(arange_slash(self.generate_path, 'data_parse_bak.xml'))
        my_logger.info(u'Edit parse_bakxml Successfully')

    def edit_dfp_xml(self):
        my_logger.info(u'Edit dfp_bakxml Begin')
        tree_xml = ET.parse(self.dpf_xml)
        root_xml = tree_xml.getroot()
        root_xml.attrib['resourceRootPath'] = self.resource_path
        root_xml.attrib['outputDir'] = arange_slash(self.corpus_path, self.corpus_name, 'filtered',
                                                    'filtered_' + add_folder(arange_slash(self.corpus_path,
                                                                                          self.corpus_name),
                                                                             'filtered'))
        if eval(self.train_radio) == 0:
            root_xml.remove(root_xml.getchildren()[0])
        elif eval(self.test_radio) == 0:
            root_xml.remove(root_xml.getchildren()[1])
        self.dpf_name = ['']
        for child in root_xml.getchildren():
            root_iter = child.find('Corpus').attrib
            try:
                detail_iter = child.find('BasicFilter').attrib
            except:
                detail_iter = None
            wer_iter = child.find('LatticeWerFilter').attrib
            if self.dpf_train_flag:
                self.dpf_name.append(root_iter['corpusname'])
            sub_dpf_corpusname = 'train' if 'train' in root_iter['corpusname'] else 'devtest'
            root_iter['waveList'] = arange_slash(self.ossuploadrootpath,
                                                 sub_dpf_corpusname,
                                                 self.corpus_name,
                                                 'wavelist.txt')
            root_iter['transcriptionList'] = arange_slash(self.ossuploadrootpath,
                                                          sub_dpf_corpusname,
                                                          self.corpus_name,
                                                          'transcriptionlist.txt')

            if detail_iter:
                detail_iter['MinSentenceLengthInMillsecond'] = self.dpf_MinSentenceLengthInMillsecond
                detail_iter['MaxSentenceLengthInMillsecond'] = self.dpf_MaxSentenceLengthInMillsecond
                # detail_iter['PeakPointRatio'] = self.dpf_PeakPointRatio

            # wer_iter['werThresholdDrop'] = self.dpf_werThresholdDrop

        tree_xml.write(arange_slash(self.generate_path, 'data_process_filter_bak.xml'))

        try:
            self.dpf_name = self.dpf_name[1]
        except:
            self.dpf_name = ''
        my_logger.info(u'Edit dfp_bakxml Successfully')

    def edit_train_xml(self):
        my_logger.info(u'Edit train_bakxml Begin')
        tree_xml = ET.parse(self.train_xml)
        root_xml = tree_xml.getroot()
        root_xml.attrib['outputDir'] = arange_slash(self.corpus_path, self.corpus_name, 'trained',
                                                    'trained_' + add_folder(
                                                        arange_slash(self.corpus_path, self.corpus_name),
                                                        'trained'))
        root_xml.attrib['resourceRootPath'] = self.resource_path
        root_xml.attrib['licenseServerList'] = self.license

        root_xml.find('CorpusList').attrib['samplerate'] = self.samplerate
        root_iter = root_xml.find('CorpusList').find('Corpus').attrib

        # root_iter['SmbrTrainFeatureLabelPath'] = arange_slash(self.generate_path,
        # 'feature_align_lattice_label_'+self.dpf_name)
        root_iter['SmbrTrainFeatureLabelPath'] = (os.getcwd() + '/feature_align_lattice_label_' + self.dpf_name)

        root_xml.find('SmbrTrain').attrib['initModel'] = self.initmodel
        root_xml.find('SmbrTrain').attrib['featureTrans'] = self.initfeature

        try:
            root_iter_Smbr = root_xml.find('SmbrTrain').attrib
            root_iter_Smbr['epochNum'] = self.Smbr_Epoch
        except:
            pass

        tree_xml.write(arange_slash(self.generate_path, 'dcs_am_pipeline_bak.xml'))
        my_logger.info(u'Edit train_bakxml Successfully')

    def edit_test_xml(self):
        tree_xml = ET.parse(self.test_xml)
        root_xml = tree_xml.getroot()
        iter_xml = root_xml.find('DataList').find('Data').attrib
        iter_xml['customizationId'] = self.customizationID

        if (self.fix_test == "T" or self.fix_test == "True" or self.fix_test == "true"):
            iter_xml['name'] = 'Standard_Test'
            iter_xml['transcriptionListFile'] = self.fix_trans
            iter_xml['waveListFile'] = self.fix_wave
        else:
            iter_xml['name'] = 'Test_' + self.corpus_name
            iter_xml['transcriptionListFile'] = arange_slash(self.ossuploadrootpath,
                                                             'devtest',
                                                             self.corpus_name,
                                                             'transcriptionlist.txt')
            iter_xml['waveListFile'] = arange_slash(self.ossuploadrootpath,
                                                    'devtest',
                                                    self.corpus_name,
                                                    'wavelist.txt')
        tree_xml.write(arange_slash(self.generate_path, 'SimpleRecognitionToolForDcsWithCust_bak.xml'))

    def CE_Train_txt(self):
        util_path = os.path.join(self.local_src, "AMDataProcessingTools/am_train_local/train_confs")
        os.system("sed -i 's#minibatchSize=[0-9]*#minibatchSize=%s#' %s" % (
        self.fsmn_CE_Batch, os.path.join(util_path, "fsmn", self.CeTrain_txt)))
        os.system(
            "sed -i -e 's#minibatchSize=[0-9]*#minibatchSize=%s#' -e 's#batchSize=[0-9]*#batchSize=%s#' -e 's#maxLen=[0-9]*#maxLen=%s#'  %s" % (
            self.fsmn_ctc_CE_Batch, self.fsmn_ctc_CE_Batch, self.Skip_CE_Length,
            os.path.join(util_path, "fsmn-ctc", self.CeTrain_txt)))
        os.system("sed -i 's#minibatchSize=[0-9]*#minibatchSize=%s#' %s" % (
        self.fsmn_ctc_smbr_Batch, os.path.join(util_path, "fsmn-ctc", self.SmbrTrain_txt)))

    def main(self):
        self.read_global_xml(self.inputargs)
        self.edit_parse_xml()
        self.CE_Train_txt()
        if self.dpf_train_flag:
            self.edit_dfp_xml()
            self.edit_train_xml()

        if self.dpf_test_flag:
            self.edit_test_xml()

        else:
            print('No Training Data Appointed, Ineffective for Train XML')
