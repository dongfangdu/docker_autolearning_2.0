# -*- coding:utf-8 -*-
import json
import os

import xmltodict

from libs.common import get_project_dir, get_uuid

# from lxml import etree
# from lxml.etree import tostring


if __name__ == '__main__':
    running_param_dir = os.path.join(get_project_dir(), 'cfg', 'running_param')
    if not os.path.exists(running_param_dir):
        os.makedirs(running_param_dir)

    train_uuid = get_uuid()
    train_module = 'am_training_pipeline'
    running_param_name = 'data_parse_temp'
    running_param_xml_template = os.path.join(
        get_project_dir(), 'bin', train_module,
        '{}.xml'.format(running_param_name))

    running_param_xml = os.path.join(
        running_param_dir, '{}_{}.xml'.format(running_param_name, train_uuid))
    print running_param_xml

    with open(running_param_xml_template, mode='r') as f:
        xmlparse = xmltodict.parse(f.read())
        jsonstr = json.dumps(xmlparse, indent=2)
        print jsonstr

    xml_str = xmltodict.unparse(xmlparse, pretty=True)
    print xml_str

    # xmltodict.unparse()

    # open(running_param_xml, 'a').close()
    # parser = etree.XMLParser(encoding='utf-8', strip_cdata=False, remove_blank_text=True)
    # xml = etree.parse(running_param_xml_template, parser=parser)
    # root = xml.getroot()
    #
    # tree = etree.ElementTree(root)
    # print tostring(indent(root))
    # print etree.tostring(indent(root), method='xml', pretty_print=False, xml_declaration=True, encoding='utf-8')
    # tree.write(running_param_xml, pretty_print=False, xml_declaration=True, encoding='utf-8')
    # etree.write(running_param_xml, xml_declaration=True, method='xml ')
