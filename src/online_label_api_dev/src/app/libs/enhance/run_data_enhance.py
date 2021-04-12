# -*- coding: utf -*-
import argparse
#from data_enhance import DataEnhancement
from app.libs.enhance.data_enhance import DataEnhancement
#from enums import EnhanceTypeEnum
from app.libs.enhance.libs.enums import EnhanceTypeEnum

if __name__ == '__main__':
    # check input
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--enhance-dir', action='store', required=True, help=u'待增强音频文件夹路径')

    enhance_type_help = '; '.join(['{} for {}'.format(e.value, e.name) for e in EnhanceTypeEnum])
    enhance_type_choices = [e.value for e in EnhanceTypeEnum]
    parser.add_argument('-t', '--enhance-type',
                        action='store',
                        type=int,
                        choices=enhance_type_choices,
                        required=True,
                        help=u'增强类型: {}'.format(enhance_type_help))
    parser.add_argument('-o', '--out-file', action='store', required=True, help=u'增强结果输出文件')

    inputargs = parser.parse_args()

    # print inputargs.enhance_dir
    # print inputargs.enhance_type
    # print inputargs.out_file

    result = DataEnhancement().enhance_data(inputargs.enhance_type, inputargs.enhance_dir)
    with open(inputargs.out_file, 'w') as fp:
        fp.write(result)





