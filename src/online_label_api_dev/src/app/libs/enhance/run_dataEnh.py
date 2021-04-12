# -*- coding: utf8 -*-

from app.libs.enhance.data_enhance import DataEnhancement
from app.libs.enhance import configure as conf

if __name__ == "__main__":
    # ori_data_path = sys.argv[1]
    ori_data_path = "/home/user/wangyd/train_tmp_data/b786a49675f14b31932cf94d1980e235/data/wav"
    result = DataEnhancement().enhance_data(conf.config.ADD_NOISE, ori_data_path)
    #print result
