# -*- coding: utf-8 -*-
import json

import time
from datetime import datetime
from sqlalchemy import Column, Integer, String, create_engine, DateTime, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import uuid
import os
import sys

folder_path = os.path.split(os.path.realpath(sys.argv[0]))[0]
print(folder_path + '/../../tools/prepare_api')
sys.path.append(folder_path + '/../../tools/prepare_api')
from data_prepare import DataPrepare
import logging

# LOG_FORMAT = "[%(asctime)s] - [%(levelname)s] - [%(message)s]"
LOG_FORMAT = '[%(asctime)s] [%(levelname)s - %(lineno)d] -- [%(message)s]'
# logging.basicConfig(filename='./log_autotrain/train.log', level=logging.DEBUG, format=LOG_FORMAT)
my_logger = logging.getLogger(__name__)
my_logger.setLevel(level=logging.DEBUG)

log_path = folder_path + '/log_autotrain/train.log'

fh = logging.FileHandler(log_path, encoding='utf8')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt=LOG_FORMAT)
fh.setFormatter(formatter)
my_logger.addHandler(fh)
time.sleep(2)

from ConfigParser import ConfigParser

cf = ConfigParser()
cf.read(folder_path + '/../../cfg/config.ini')
db_host = cf.get("DataBase", "host")
db_port = cf.get("DataBase", "port")
# db_port = int(float(db_port))
db_user = cf.get("DataBase", "user")
db_name = cf.get("DataBase", "db")
db_password = cf.get("DataBase", "passwd")
db_tablename = cf.get("DataBase", "tablename")
TrainPackage = cf.get("RunShell", "train_package")
LocalXml = cf.get("RunShell", "local_xml_dir")
run_dp = cf.get("RunShell", "run_dp")
run_dpf = cf.get("RunShell", "run_dpf")
run_train = cf.get("RunShell", "run_train")
InitModel = cf.get("InitModel", "init_model")

#  创建连接
# engine = create_engine("mysql+pymysql://root:@192.168.108.197:3306/zx_auto_train", echo=False)
my_logger.info(u'*Begin*')
my_logger.info(u'开始连接数据库.....')
engine_cfg = "mysql+pymysql://" + db_user + ":" + db_password + "@" + db_host + ":" + db_port + "/" + db_name
engine = create_engine(engine_cfg, echo=False)
Base = declarative_base()  # 生成orm基类
my_logger.info(u'连接数据库成功!')


class AlTrainInput2(Base):  # 继承基类
    __tablename__ = db_tablename
    train_id = Column(String(64), primary_key=True)
    init_model_uuid = Column(String(64))
    init_model_url = Column(String(255))
    model_status = Column(Integer(), default=0)
    prepare_id = Column(String(64))
    corpus_url = Column(String(255))
    corpus_status = Column(Integer(), default=0)
    start_time = Column(DateTime())
    new_model_uuid = Column(String(64))
    new_model_url = Column(String(255))
    new_model_time = Column(DateTime())
    train_status = Column(Integer(), default=0)
    test_status = Column(Integer(), default=0)
    model_save_path = Column(String(255))


def write_to_sql():
    print("=========Begin Write To Global===========")
    my_logger.info(u'New round of training')
    my_logger.info(u'=========Begin Write To Global===========')

    Base.metadata.create_all(engine)  # 创建表格
    session_class = sessionmaker(bind=engine)  # 返回的是类，创建与数据库的会话session类 ,这里返回给session的是个class,不是实例
    session = session_class()  # 这里再实例化，生成session实例，这个session就和pymysql里的cursor一样
    train_id = str(uuid.uuid1())
    print('train_id  is:', train_id)
    init_model_uuid = str(uuid.uuid1())
    altraininput2_obj = AlTrainInput2(train_id=train_id)  # 生成要创建的数据对象1
    session.add(altraininput2_obj)
    session.commit()  # 直到此时数据才插入表中

    data = session.query(AlTrainInput2).filter(AlTrainInput2.train_id == train_id).first()
    data2 = session.query(AlTrainInput2).filter(
        and_(AlTrainInput2.model_status == 0, AlTrainInput2.train_id != train_id)).first()
    if data:
        tree = ET.parse(folder_path + '/global_config.xml')
        root = tree.getroot()
        dictionarycorpus = root.find('corpus').attrib
        print("---[global.xml corpus is:]---", dictionarycorpus)
        corpus_url = dictionarycorpus['corpus']
        print(corpus_url)

        PreModel = root.find('corpus').attrib['initModel']
        print('PreModel in xml is', PreModel)
        PreModel_status = os.path.exists(PreModel)
        print('PreModel is exits??', PreModel_status)

        if data2 and data2.new_model_uuid:
            data.init_model_uuid = data2.new_model_uuid
        else:
            data.init_model_uuid = init_model_uuid

        if data2 and data2.new_model_url:
            data.init_model_url = data2.new_model_url
            data2.model_status = 1
        elif PreModel_status is True:
            data.init_model_url = root.find('corpus').attrib['initModel']
        else:
            data.init_model_url = InitModel
            root.find('corpus').attrib['initModel'] = InitModel

        dp = DataPrepare()
        req_res = dp.prepare_data(prepare_type=1)
        res_dict = json.loads(req_res)
        data.corpus_url = root.find('corpus').attrib['corpus']
        prepare_result = dp.is_ready(res_dict['prepare_uuid'])
        prepare_result = json.loads(prepare_result)

        my_logger.info(u'训练数据准备中...................')
        print('训练数据准备中...................')
        counter = 0
        counter_limit = 20
        while counter < counter_limit:
            if prepare_result['prepare_status'] == 1:
                break
            else:
                prepare_result = dp.is_ready(res_dict['prepare_uuid'])
                prepare_result = json.loads(prepare_result)
                time.sleep(15)
                counter = counter + 1

        if prepare_result['prepare_data_path']:
            data.corpus_url = prepare_result['prepare_data_path']

        data.prepare_id = res_dict['prepare_uuid']

        my_logger.info(u'训练数据准备已完成')
        print('训练数据完成，现开始训练')
        # if not data.corpus_url:
        # data.corpus_url = root.find('corpus').attrib['corpus']
        print(data.init_model_url)
        root.find('corpus').attrib['initModel'] = data.init_model_url or ''
        root.find('corpus').attrib['corpus'] = data.corpus_url or ''
        root.find('RunShell').attrib['local_src'] = TrainPackage or ''
        root.find('RunShell').attrib['run_dp'] = run_dp or ''
        root.find('RunShell').attrib['run_dpf'] = run_dpf or ''
        root.find('RunShell').attrib['run_train'] = run_train or ''
        tree.write('global_config.xml')
        my_logger.info(u'global_config.xml写入完成')
        my_logger.info("===============Finish Write To Global=============")

        # train_starttime = time.time()
        # start_time = time.strftime("%Y%m%d%H%M", time.localtime(train_starttime))
        start_time = datetime.now()
        data.start_time = start_time
        data.corpus_status = 1
        session.commit()
        print("已在数据库中插入训练所需初始数据")
        my_logger.info(u'已在数据库中插入训练所需初始数据')

        print('data.corpus_url is :', data.corpus_url)
        print('globalxml corpus is:', root.find('corpus').attrib['corpus'])

        fileobject = open(folder_path + '/train_id.txt', 'a+')
        fileobject.write(train_id + '\n')
        fileobject.close()
        my_logger.info(u'已将train_id插入文本中')
        print('====Start data parsed====')
        time.sleep(20)

    else:
        print('No match model or data package!')
        logging.error(u'No match model or data package!')


if __name__ == '__main__':
    write_to_sql()
