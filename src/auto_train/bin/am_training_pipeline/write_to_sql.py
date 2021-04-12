#coding=utf-8
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine, or_,DateTime
from sqlalchemy.orm import sessionmaker
from datetime import datetime
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import uuid
import time
import json
import os
import sys

import logging
import codecs

folder_path = os.path.split( os.path.realpath( sys.argv[0] ) )[0]

#LOG_FORMAT = "[%(asctime)s] - [%(levelname)s] - [%(message)s]"
LOG_FORMAT = '[%(asctime)s] [%(levelname)s - %(lineno)d] -- [%(message)s]'
#logging.basicConfig(filename='./log_autotrain/train.log', level=logging.DEBUG, format=LOG_FORMAT)
my_logger = logging.getLogger(__name__)
my_logger.setLevel(level=logging.DEBUG)
fh = logging.FileHandler( folder_path +'/log_autotrain/train.log', encoding='utf8')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt=LOG_FORMAT)
fh.setFormatter(formatter)
my_logger.addHandler(fh)
time.sleep(2)

import paramiko
from ConfigParser import ConfigParser
cf = ConfigParser()
cf.read( folder_path + '/../../cfg/config.ini')
db_host = cf.get("DataBase","host")
db_port = cf.get("DataBase","port")
#db_port = int(float(db_port))
db_user = cf.get("DataBase","user")
db_name = cf.get("DataBase","db")
db_password = cf.get("DataBase","passwd")
db_tablename = cf.get("DataBase","tablename")
file_host = cf.get("FileSave", "host")
file_port = cf.get("FileSave", "port")
file_port = int(float(file_port))
file_user = cf.get("FileSave", "user")
file_password = cf.get("FileSave", "passwd")
file_path = cf.get("FileSave", "dst_path")


#  创建数据库连接
#engine = create_engine("mysql+pymysql://root:@192.168.108.197:3306/zx_auto_train", echo=False)
my_logger.info(u'开始连接数据库.....')
engine_cfg = "mysql+pymysql://" + db_user + ":" + db_password +"@" + db_host + ":" + db_port + "/" + db_name
engine = create_engine(engine_cfg, echo=False)
Base = declarative_base()  # 生成orm基类
my_logger.info(u'连接数据库成功!')

class AlTrainOutput(Base):   # 继承基类
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

def train_write2sql():
    print("Begin update train result to sql! insert new model message")
    time.sleep(20)
    my_logger.info(u'=========Begin Write To Sql===========')
    Base.metadata.create_all(engine)  # 创建表格
    session_class = sessionmaker(bind=engine)  # 返回的是类，创建与数据库的会话session类 ,这里返回给session的是个class,不是实例
    session = session_class()  # 这里再实例化，
    fileobj = open( folder_path + '/train_id.txt', 'r')
    lines = fileobj.readlines()
    train_id = lines[-1]
    train_id = train_id.strip()
    print("write to sql where the train_id is",train_id)
    fileobj.close()
    print("write to sql where the train_id is",train_id)
    data = session.query(AlTrainOutput).filter(AlTrainOutput.train_id == train_id).first()
    print(data)
    new_model_uuid = str(uuid.uuid1())
    print(new_model_uuid)
    my_logger.info(u'Begin parse dcs_pipline_bak.xml')
    tree = ET.parse( folder_path + '/dcs_am_pipeline_bak.xml')
    root = tree.getroot()
    print("pipline_bak.xml outputDir is:",root.attrib['outputDir'])
    new_model_url = root.attrib['outputDir'] + '/models/nnet_smbr'
    new_model_time = datetime.now()
    data.new_model_uuid = new_model_uuid or ''
    data.new_model_url = new_model_url

    my_logger.info(u'Connect to filesave host')
    t = paramiko.Transport((file_host, file_port))
    t.connect(username=file_user, password=file_password)
    sftp = paramiko.SFTPClient.from_transport(t)
    my_logger.info(u'*Connect filesavehost Successfully')
    localpath = new_model_url
    remotepath = file_path + '/' + data.new_model_uuid
    sftp.put(localpath, remotepath)
    t.close()
    data.model_save_path = remotepath
# train_endtime = time.time()
# model_endtime = time.strftime("%Y%m%d%H%M", time.localtime(train_endtime))
    data.new_model_time = new_model_time
#    data.model_status = 1
    data.train_status = 1
    session.commit()  # 直到此时数据才插入表中
    my_logger.info(u'Write to sql successfully ')
    my_logger.info(u'已在数据库中插入本轮训练生成的数据 ')
    my_logger.info(u'=========End Write To Sql===========')
    my_logger.info(u'end one round of training')
    my_logger.info(u'*END*')


if __name__ == '__main__':
    train_write2sql()

