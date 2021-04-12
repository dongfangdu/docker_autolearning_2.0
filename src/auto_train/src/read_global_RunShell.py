# -*- coding; utf8 -*-

# This file used to read parameters of
# run_data_and_training.sh
# This procedure applied to arrange the parameters to global_config.xml
# =========================================================
import argparse
import os
import sys
import xml.etree.ElementTree as ET
import xml.etree.cElementTree


# ============================
class Read_Global_RunShell():
    def __init__(self):
        self.choices = ['local_src', 'local_xml_dir', 'test_src', 'run_dp', 'run_dpf', 'run_train', 'run_test',
                        'fill_flag']
        self.corpus_choices = ['corpus', 'name', 'speech_alisr', 'initModel']
        self.test_choices = ['fix_trans', 'fix_wave']

    def obtain_args(self):
        parser = argparse.ArgumentParser()
        # default_xml_path = os.path.join(os.path.dirname(os.getcwd()), 'am_training_pipeline', 'global_config.xml')
        default_xml_path = os.path.join(os.path.split(os.path.realpath(sys.argv[0]))[0],
                                        '../bin/am_training_pipeline/global_config.xml')
        parser.add_argument('--inputxmlfilename', action='store', default=default_xml_path, help='input global xml')
        parser.add_argument('-p', '--para', action='store', choices=self.choices)
        self.inputargs = parser.parse_args()

    def read_global_xml(self):
        tree = xml.etree.cElementTree.ElementTree()
        tree.parse(self.inputargs.inputxmlfilename)
        root = tree.getroot()
        self.iter_xml = root.find('RunShell').attrib
        self.corpus_iter_xml = root.find('corpus').attrib
        self.test_iter_xml = root.find('test').attrib

    def obtain_paras(self):
        for ele in self.choices:
            if ele == self.inputargs.para:
                if ele in ['local_src', 'local_xml_dir', 'test_src']:
                    return os.path.abspath(self.iter_xml[ele])
                else:
                    return "true" if (self.iter_xml[ele] == "T" or self.iter_xml[ele] == "True" or self.iter_xml[
                        ele] == "true") else "false"

        for ele in self.corpus_choices:
            if ele == self.inputargs.para:
                return self.corpus_iter_xml[ele]

        for ele in self.test_choices:
            if ele == self.inputargs.para:
                return os.path.dirname(self.test_iter_xml[ele])

    def main(self):
        self.obtain_args()
        self.read_global_xml()
        return self.obtain_paras()


if __name__ == '__main__':
    print(Read_Global_RunShell().main())
