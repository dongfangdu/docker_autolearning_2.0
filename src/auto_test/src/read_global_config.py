import argparse
import os
from configobj import ConfigObj


def Read_Global_Config(config_file):
    parser = argparse.ArgumentParser()
    parser.add_argument('--Folder_Tag', '-f')
    parser.add_argument('--Sub_Tag', '-s')
    inputargs = parser.parse_args()
    try:
        cfg_parser = ConfigObj(config_file)
        print(cfg_parser[inputargs.Folder_Tag][inputargs.Sub_Tag])
    except:
        pass
        # raise Exception


if __name__ == '__main__':
    Read_Global_Config('../cfg/config.ini')
