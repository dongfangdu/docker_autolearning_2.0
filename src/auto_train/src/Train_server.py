# -*- coding; utf8 -*-

import os
import sys
import xml.etree.ElementTree as ET

folder_path = os.path.split(os.path.realpath(sys.argv[0]))[0]


def start_run():
    local_src = \
    ET.parse(folder_path + '/../bin/am_training_pipeline/global_config.xml').getroot().find('RunShell').attrib[
        'local_src']
    local_xml_dir = \
    ET.parse(folder_path + '/../bin/am_training_pipeline/global_config.xml').getroot().find('RunShell').attrib[
        'local_xml_dir']
    sudoPassword = 'yjyjs123'
    command = 'sudo python ' + local_src + '/asrp.py --inputxmlfilename ' + local_xml_dir + '/dcs_am_pipeline_bak.xml --printlogcode --debug'
    # print('command', command)
    # print('local_xml_dir', local_xml_dir)
    p = os.system('echo %s|sudo -S %s' % (sudoPassword, command))


if __name__ == "__main__":
    start_run()
