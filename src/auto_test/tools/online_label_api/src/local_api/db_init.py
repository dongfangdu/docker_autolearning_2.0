# -*- coding: utf8 -*-
import csv
import logging
import traceback

import os
import re
import time
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

from app import create_app
from app.libs.path_utils import get_resource_dir, get_project_dir
from app.models.base import db_v2, DB_V2_TABLE_PREFIX, DB_V2_SYSTEM_PREFIX
from app.models.v2.web import User

logger = logging.getLogger(__name__)


def create_dbs():
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')

    with app.app_context():
        sql_init_tmp_dir = os.path.join(get_resource_dir(), 'sql_init_tmp')
        if not os.path.exists(sql_init_tmp_dir):
            os.makedirs(sql_init_tmp_dir)

        mysql_tool = os.path.join(get_project_dir(), 'bin/mysql')
        if not os.path.exists(mysql_tool):
            raise RuntimeError(u'dump工具不存在')

        db_url_dict_keys = ['database', 'host', 'password_original', 'port', 'username']
        for check_bind in db_v2.get_bind_names():
            if not check_bind:
                continue
            engine = db_v2.get_engine(app=app, bind=check_bind)
            db_type = str(check_bind).replace(DB_V2_TABLE_PREFIX, '')
            db_url_dict = {
                'mysql_tool': mysql_tool
            }
            for k in db_url_dict_keys:
                db_url_dict[k] = getattr(engine.url, k, '')

            with open(os.path.join(get_resource_dir(), 'sql_templates/create_db.txt')) as f:
                # create_db_script.append(str(f.read()).format(**{'db_name': engine.url.database}))
                create_sql = str(f.read()).format(**{'db_name': engine.url.database})

            script_file = os.path.join(sql_init_tmp_dir, 'create_db_{}.sql'.format(db_type))
            with open(script_file, mode='w+') as f:
                f.write('{}\n'.format(create_sql))
            db_url_dict['script_file'] = script_file

            command = '{mysql_tool} -h{host} -P{port} -u{username} -p{password_original} < {script_file}' \
                .format(**db_url_dict)

            # create_table_sql_template = str(os.popen(command).read())
            import subprocess as sp
            child = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
            streamdata = child.communicate()
            return_code = child.returncode
            if return_code != 0:
                logger.error(streamdata[1])
                logger.info(u'建立{}数据库失败'.format(db_type))
            else:
                logger.info(streamdata[0])
                logger.info(u'建立{}数据库成功'.format(db_type))


def init_sql_template():
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    with app.app_context():
        sql_init_tmp_dir = os.path.join(get_resource_dir(), 'sql_init_tmp')
        if not os.path.exists(sql_init_tmp_dir):
            os.makedirs(sql_init_tmp_dir)

        dump_tool = os.path.join(get_project_dir(), 'bin/mysqldump')
        if not os.path.exists(dump_tool):
            raise RuntimeError(u'dump工具不存在')

        db_url_dict_keys = ['database', 'host', 'password_original', 'port', 'username']
        for bind in db_v2.get_binds():
            db_url = db_v2.get_engine(app=app, bind=bind.info['bind_key']).url
            db_url_dict = {
                'dump_tool': dump_tool
            }
            for k in db_url_dict_keys:
                db_url_dict[k] = getattr(db_url, k, '')
            # print bind.name, bind.info['bind_key'], db_url_dict
            db_url_dict['tablename'] = bind.name
            bind_type = str(bind.info['bind_key']).replace(DB_V2_TABLE_PREFIX, '')

            dump_command = '{dump_tool} -h{host} -P{port} -u{username} -p{password_original} --no-data' \
                           ' --skip-add-drop-table --skip-comments {database} --table {tablename}' \
                .format(**db_url_dict)

            # print dump_command
            # print db_url_dict['tablename']
            # continue

            create_table_sql_template = str(os.popen(dump_command).read())

            create_table_sql_template = re.sub(re.compile(r'CREATE TABLE.*?\(', re.S),
                                               'CREATE TABLE `{}`.`{}` ('.format(db_url_dict['database'], bind.name),
                                               create_table_sql_template)
            create_table_sql_template = re.sub(re.compile(r'AUTO_INCREMENT=\d+\s', re.S), '', create_table_sql_template)
            database_template = str(db_url_dict['database']).replace(DB_V2_SYSTEM_PREFIX, '{system_name}')
            table_template = str(bind.name).replace(DB_V2_TABLE_PREFIX, '{table_prefix}')
            create_table_sql_template = create_table_sql_template.replace(str(db_url_dict['database']),
                                                                          database_template)
            create_table_sql_template = create_table_sql_template.replace(str(bind.name), table_template)

            # create_table_sql_template = create_table_sql_template.replace()
            template_target_dir = os.path.join(get_resource_dir(), 'sql_templates/{}'.format(bind_type))
            if not os.path.exists(template_target_dir):
                os.makedirs(template_target_dir)

            template_sql_name = 'create_table_{}.txt'.format(str(bind.name).replace(DB_V2_TABLE_PREFIX, ''))
            with open(os.path.join(template_target_dir, template_sql_name), mode='w+') as f:
                f.write(create_table_sql_template)

        logger.info(len(db_v2.get_binds()))


def create_tables():
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    with app.app_context():
        sql_init_tmp_dir = os.path.join(get_resource_dir(), 'sql_init_tmp')
        if not os.path.exists(sql_init_tmp_dir):
            os.makedirs(sql_init_tmp_dir)

        mysql_tool = os.path.join(get_project_dir(), 'bin/mysql')
        if not os.path.exists(mysql_tool):
            raise RuntimeError(u'dump工具不存在')

        db_url_dict_keys = ['database', 'host', 'password_original', 'port', 'username']
        for bind in db_v2.get_binds():
            db_url = db_v2.get_engine(app=app, bind=bind.info['bind_key']).url
            db_url_dict = {
                'mysql_tool': mysql_tool
            }
            for k in db_url_dict_keys:
                db_url_dict[k] = getattr(db_url, k, '')
            # print bind.name, bind.info['bind_key'], db_url_dict
            db_url_dict['tablename'] = bind.name
            bind_type = str(bind.info['bind_key']).replace(DB_V2_TABLE_PREFIX, '')

            template_target_dir = os.path.join(get_resource_dir(), 'sql_templates/{}'.format(bind_type))
            template_sql_name = 'create_table_{}.txt'.format(str(bind.name).replace(DB_V2_TABLE_PREFIX, ''))
            with open(os.path.join(template_target_dir, template_sql_name), mode='rb') as f:
                create_table_sql = str(f.read()).format(system_name=DB_V2_SYSTEM_PREFIX,
                                                        table_prefix=DB_V2_TABLE_PREFIX)
            # print create_table_sql

            script_file = os.path.join(sql_init_tmp_dir, 'create_table_{}.sql'.format(bind.name))
            with open(script_file, mode='w+') as f:
                f.write('{}\n'.format(create_table_sql))

            db_url_dict['script_file'] = script_file

            command = '{mysql_tool} -h{host} -P{port} -u{username} -p{password_original} < {script_file}' \
                .format(**db_url_dict)

            # print command

            # create_table_sql_template = str(os.popen(command).read())
            import subprocess as sp
            child = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
            streamdata = child.communicate()
            return_code = child.returncode
            if return_code != 0:
                logger.error(streamdata[1])
                logger.info(u'建立{}数据表失败'.format(bind.name))
            else:
                logger.info(streamdata[0])
                logger.info(u'建立{}数据表成功'.format(bind.name))
            # break


def init_data():
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')

    with app.app_context():
        init_data_from_csv = False
        if init_data_from_csv:
            Base = automap_base()
            eng = db_v2.get_engine(bind='{}web'.format(DB_V2_TABLE_PREFIX))
            Base.prepare(eng, reflect=True)
            Session = sessionmaker(bind=eng)
            session = Session()

            init_data_dir = os.path.join(get_resource_dir(), 'init_data')
            if not os.path.exists(init_data_dir):
                # os.makedirs(init_data_dir)
                logger.info(u'初始化数据目录不存在: {}'.format(init_data_dir))
                return

            for root, dirs, files in os.walk(init_data_dir):
                for filename in files:
                    # with codecs.open(os.path.join(root, filename), mode='r', encoding='utf-8') as f:
                    table_name = '{}{}'.format(DB_V2_TABLE_PREFIX, filename.split('.')[0])
                    try:
                        with open(os.path.join(root, filename), mode='r') as f:
                            dict_reader = csv.DictReader(f)
                            # print filename.split('.')[0]
                            session.execute(Base.classes[table_name].__table__.insert().prefix_with('IGNORE'),
                                            list(dict_reader))
                            session.commit()
                    except Exception as e:
                        logger.error(traceback.format_exc())
                        logger.error(e.message)
                        logger.error(u'{}表初始数据添加成功'.format(table_name))
                        continue

                    logger.info(u'{}表初始数据添加成功'.format(table_name))

            session.close()

        with db_v2.auto_commit():
            # 创建一个超级管理员
            user = User()
            # user.id = 1
            user.account = 'superadmin'
            user.password = '123456'
            user.nickname = '超级管理员'
            user.telephone = ''
            user.ac_type = 100
            user.ac_status = 1
            user.create_time = int(time.time())
            user.rid = 1
            # print dict(user)
            db_v2.session.add(user)
            # db_v2.session.execute(User.__table__.insert().prefix_with('IGNORE'), dict(user))
        logger.info(u'初始用户添加成果')


if __name__ == '__main__':
    init_sql_template()
    # create_dbs()
    # create_tables()
    # init_data()
    # app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    # with app.app_context():
    #     train_request_info_list = TrainRequestInfo.query.filter_by().all()
    #     print len(train_request_info_list)
    # import sys
    # print sys.executable

    pass
