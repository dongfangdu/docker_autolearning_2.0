# -*- coding: utf8 -*-
import json
import shutil

import os
import time

from app import create_app
from app.libs.asr_func.filetrans_handler import FileTransRestful
from app.libs.builtin_extend import current_timestamp_sec, get_uuid
from app.libs.file_utils import generate_file_md5
from app.libs.string_utils import try_decode
from app.models.base import db_v1
import magic
import redis

from app.models.v1.sysmng import Region
from app.models.v1.tagfile import AudioFile, UtteranceRestful, AudioFileMark


def audiosrc_prepare():
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    upload_tmp_dir = os.path.join(app.root_path, 'uploads_tmp')
    audio_file_list = []
    audio_file_mark_list = []

    regions_dict = {}
    rel_path_region_dict = {}
    with app.app_context():
        regions = Region.query.filter_by().all()
        regions_dict = {r.name: r.id for r in regions}

    for root, dirs, files in os.walk(upload_tmp_dir):
        for filename in files:

            rel_path = os.path.relpath(root, upload_tmp_dir)
            file_path = os.path.join(root, filename)
            magic_type = magic.from_file(file_path, mime=True)
            if magic_type != 'audio/x-wav':
                print u'%s 文件不是wave格式，而是%s' % (try_decode(file_path), magic_type)
                continue
            file_md5 = generate_file_md5(root, filename)
            basename, ext = os.path.splitext(filename)
            ext = '.wav'
            upload_time = current_timestamp_sec()
            file_uuid = get_uuid()
            new_filename = file_uuid + ext

            # 处理编码
            filename = try_decode(filename)
            rel_path = try_decode(rel_path)

            audio_file = AudioFile()
            audio_file.file_name = filename
            audio_file.file_uuid = file_uuid
            audio_file.upload_time = upload_time
            file_url = os.path.join(time.strftime('/audiosrc/%Y/%m/%d', time.localtime(upload_time)), new_filename)
            audio_file.file_url = file_url
            audio_file.file_md5 = file_md5
            audio_file.analysis_status = 0
            audio_file.create_time = upload_time
            audio_file.rel_path = rel_path

            audio_file_list.append(audio_file)

            # 跟上面的的region字典整合成guess_region_from_string的函数
            mark_region = rel_path_region_dict.get(rel_path, None)
            if not mark_region:
                contain_region_list = []
                for region_name in regions_dict.keys():
                    if region_name in rel_path:
                        contain_region_list.append(region_name)
                rel_path_region_dict[rel_path] = ','.join(contain_region_list)
                mark_region = rel_path_region_dict.get(rel_path, None)

            if mark_region:
                audio_file_mark2 = AudioFileMark()
                audio_file_mark2.create_time = upload_time
                audio_file_mark2.file_uuid = file_uuid
                audio_file_mark2.mark_key = u'地区'
                audio_file_mark2.mark_value = mark_region

                audio_file_mark_list.append(audio_file_mark2)
    with app.app_context():
        with db_v1.auto_commit():
            for audio_file in audio_file_list:
                db_v1.session.add(audio_file)
            for audio_file_mark in audio_file_mark_list:
                db_v1.session.add(audio_file_mark)
        # /home/admin/online_label_system/label_data/audiosrc/2019/05/30/6195511b3a424be686970a042242593b.wav

        file_server_dir = '/home/admin/online_label_system/label_data'
        for audio_file in audio_file_list:
            s_dir = os.path.join(upload_tmp_dir, audio_file.rel_path)
            s_path = os.path.join(s_dir, audio_file.file_name)
            d_path = os.path.join(file_server_dir, audio_file.file_url[1:])
            d_dir = os.path.dirname(d_path)
            if not os.path.isdir(d_dir):
                os.makedirs(d_dir)
            shutil.move(s_path, d_path)
            print u'文件 %s 已成功存储到 %s' % (audio_file.file_name, d_dir)


def asr_restful_call():
    host = '192.168.108.197:8101'
    file_root = 'file:/home/admin/nls-filetrans/disk'

    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    file_server_dir = '/home/admin/online_label_system/label_data'
    restful_data_dir = '/home/admin/v2.6_16K/service/data/servicedata/nls-filetrans/'
    if not os.path.isdir(restful_data_dir):
        os.makedirs(restful_data_dir)

    with app.app_context():
        audio_file_list = AudioFile.query.filter_by(analysis_status=0).all()
        for audio_file in audio_file_list:
            file_store_path = os.path.join(file_server_dir, audio_file.file_url[1:])

            if not os.path.exists(file_store_path):
                print u'%s 文件不存在' % file_store_path
                continue
            if not os.path.isfile(file_store_path):
                print u'%s 该路径不是文件' % file_store_path
                continue

            file_name = os.path.basename(file_store_path)
            file_restful_path = os.path.join(restful_data_dir, file_name)

            shutil.move(file_store_path, file_restful_path)

            task_id = FileTransRestful(host=host, file_root=file_root, file_name=file_name).register_file_flow()
            if not task_id:
                print u'%s 文件调用restful接口不成功' % file_name
                continue

            with db_v1.auto_commit():
                audio_file.analysis_status = 1
                audio_file.task_id = task_id



def asr_log_parse():
    env_path = '/home/admin/online_label_system/online_label_env'
    log_parser_path = '/home/admin/online_label_system/log_parser/log_parser_v2.x'

    command_list = [
        'source %s/bin/activate' % env_path,
        'python %s/src/run_log_parser.py' % log_parser_path,
    ]

    os.system(' && '.join(command_list))


def check_finished():
    r = redis.Redis(host='192.168.108.197', port=7011, password='88630dd3d489a617b635d51ef7eedfe')
    # enterprise.nls.trans.task.result.bb5491a1828a11e9bd7a0580d66b3fad
    result_key_prefix = 'enterprise.nls.trans.task.result.'
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')

    need_parse_state = 0    # 这一轮的restful已全部执行完，可以开始解释

    file_server_dir = '/home/admin/online_label_system/label_data'
    restful_data_dir = '/home/admin/v2.6_16K/service/data/servicedata/nls-filetrans/'

    with app.app_context():
        audio_file_list = AudioFile.query.filter_by(analysis_status=1).all()

        if not audio_file_list or len(audio_file_list) == 0:
            need_parse_state = 2    # 没有调用过restful接口，不需要解析
            return need_parse_state

        for audio_file in audio_file_list:
            file_store_path = os.path.join(file_server_dir, audio_file.file_url[1:])
            file_name = os.path.basename(file_store_path)
            file_restful_path = os.path.join(restful_data_dir, file_name)

            task_id = audio_file.task_id
            result = r.get(result_key_prefix + task_id)
            if not result:
                with db_v1.auto_commit():
                    audio_file.analysis_status = 3
                shutil.move(file_restful_path, file_store_path)
                continue
            try:
                result = json.loads(result)
                status_code = result['status_code']
                status_text = result['status_text']
                if 'SUCCESS' == status_text:
                    sentences = result['sentences']

                    utterance_restful_list = []
                    cur_timestamp = current_timestamp_sec()
                    for sentence in sentences:
                        utterance_restful = UtteranceRestful()
                        utterance_restful.create_time = cur_timestamp
                        utterance_restful.task_id = task_id
                        utterance_restful.is_deleted = 0
                        utterance_restful.channel_id = sentence['channel_id']
                        utterance_restful.begin_time = sentence['begin_time']
                        utterance_restful.end_time = sentence['end_time']
                        utterance_restful.speech_rate = sentence['speech_rate']
                        utterance_restful.text = sentence['text']
                        utterance_restful.emotion_value = sentence['emotion_value']

                        utterance_restful_list.append(utterance_restful)
                    with db_v1.auto_commit():
                        db_v1.session.bulk_save_objects(utterance_restful_list)
                        audio_file.analysis_status = 2
                        audio_file.task_status_code = status_code
                        audio_file.task_status_text = status_text
                    shutil.move(file_restful_path, file_store_path)
                elif 'SUCCESS_WITH_NO_VALID_FRAGMENT' == status_text:
                    with db_v1.auto_commit():
                        audio_file.analysis_status = 2
                        audio_file.task_status_code = status_code
                        audio_file.task_status_text = status_text
                    shutil.move(file_restful_path, file_store_path)
                elif 'QUEUEING' == status_text or 'RUNNING' == status_text:
                    need_parse_state = 1
                else:
                    with db_v1.auto_commit():
                        audio_file.analysis_status = 3
                        audio_file.task_status_code = status_code
                        audio_file.task_status_text = status_text
                    shutil.move(file_restful_path, file_store_path)

            except ValueError:
                with db_v1.auto_commit():
                    audio_file.analysis_status = 3
                print('The response is not json format string')
        print 'need_parse_state: %d' % need_parse_state
        return need_parse_state


def parser():
    asr_log_parse()


def runner():
    audiosrc_prepare()
    # asr_restful_call()
    #
    # while True:
    #     need_parse_state = check_finished()
    #     if need_parse_state == 0:
    #         print u'开始执行解析'
    #         asr_log_parse()
    #         pass
    #     elif need_parse_state == 1:
    #         time.sleep(10)
    #         continue
    #     elif need_parse_state == 2:
    #         break
    #     else:
    #         print u'出现未定义的parse_state: %d' % need_parse_state
    #         break

    # time.sleep(5 * 60)  # 暂停一段时候
    #
    # asr_log_parse()


if __name__ == '__main__':
    # 只调用restful接口
    runner()

    # 只解析
    # parser()
