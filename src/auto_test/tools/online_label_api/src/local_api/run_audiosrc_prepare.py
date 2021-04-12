# -*- coding: utf8 -*-
import json
import shutil
import subprocess
import subprocess as sp
import threading
from collections import defaultdict

import magic
import os
import time

from app import create_app
from app.libs.asr_func.filetrans_handler import FileTransRestful
from app.libs.builtin_extend import current_timestamp_sec, get_uuid
from app.libs.file_utils import generate_file_md5
from app.libs.ng_utils import get_ng_version
from app.libs.path_utils import get_tmp_dir, get_bin_dir
from app.models.base import db_v2
from app.models.v2.engine import AudiosrcFileinfo, AudiosrcFiletrans


class AudiosrcPrepareHandler:
    __cfg = None

    def __init__(self, cfg_path='./'):
        pass

    def _do_uncompress(self, filepath):
        pass

    def _do_transformat(self, filepath):
        pass

    def _do_move(self, src_filepath, dst_filepath):
        pass

    def _do_copy(self, src_filepath, dst_filepath):
        pass


def audiosrc_prepare():
    app = create_app(os.getenv('FLASK_CONFIG') or 'default', logging_cfg='./cfg/logging_ds.yaml')
    logger = app.logger

    # TODO 后续得改为后续的流处理，但每个单独步骤可以单独处理，日志
    upload_uuid = get_uuid()
    upload_dir = os.path.abspath(u'/home/user/qinyp/work/wav_process/改变采样率/2019年')
    if not os.path.exists(upload_dir):
        logger.error(u'输入路径不存在：{}'.format(upload_dir))
        return False

    pending_dir_list = []
    pending_dir_list.append(upload_dir)
    # 解压
    is_handle_compress = False
    if is_handle_compress:
        mt_uncompress_wanna = ['application/x-rar', 'application/x-7z-compressed', 'application/zip']
        mt_uncompress_allow = {}
        for mt_uncompress in mt_uncompress_wanna:
            if mt_uncompress == 'application/x-rar':
                handle_tool = os.path.join(get_bin_dir(), 'rar')
                return_code = os.system('{handle_tool} 1>/dev/null 2>&1'.format(handle_tool=handle_tool))
                if return_code == 0:
                    handle_command = '{handle_tool} x -o+ \"{{file_src}}\" \"{{file_dst}}\"'
                    mt_uncompress_allow[mt_uncompress] = handle_command.format(handle_tool=handle_tool)
            if mt_uncompress == 'application/x-7z-compressed':
                handle_tool = '7za'
                return_code = os.system('{handle_tool} 1>/dev/null 2>&1'.format(handle_tool=handle_tool))
                if return_code == 0:
                    handle_command = '{handle_tool} x "{{file_src}}" "{{file_dst}}"'
                    mt_uncompress_allow[mt_uncompress] = handle_command.format(handle_tool=handle_tool)
            if mt_uncompress == 'application/zip':
                handle_tool = 'unzip'
                return_code = os.system('{handle_tool} 1>/dev/null 2>&1'.format(handle_tool=handle_tool))
                if return_code == 0:
                    handle_command = '{handle_tool} -o "{{file_src}}" -d "{{file_dst}}"'
                    mt_uncompress_allow[mt_uncompress] = handle_command.format(handle_tool=handle_tool)

        # print mt_uncompress_allow
        if len(mt_uncompress_allow) > 0:
            compress_tmp_dir = os.path.join(get_tmp_dir(), 'asrc_prep_compress')
            if not os.path.exists(compress_tmp_dir):
                os.makedirs(compress_tmp_dir, mode=0775)
            pending_dir_list.append(compress_tmp_dir)

            for pending_dir in pending_dir_list:
                for root, dirs, files in os.walk(pending_dir):
                    for filename in files:
                        file_path = os.path.join(root, filename)
                        magic_type = magic.from_file(file_path, mime=True)
                        if magic_type not in mt_uncompress_allow.keys():
                            continue
                        # logger.info(file_path)
                        dst_file_path = file_path.replace(pending_dir, compress_tmp_dir)
                        # dst_file_dir = os.path.dirname(dst_file_path)
                        dst_file_dir = dst_file_path.replace('.', '_')
                        if not os.path.exists(dst_file_dir):
                            os.makedirs(dst_file_dir, mode=0775)
                        cmd = mt_uncompress_allow[magic_type].format(file_src=file_path, file_dst=dst_file_dir)
                        cmd_without_output = '{} 1>/dev/null 2>&1'.format(cmd)
                        logger.info(cmd_without_output)

                        return_code = sp.call([cmd_without_output, ], shell=True)
                        logger.info('return_code: {}'.format(return_code))

    # 转wav
    pending_dir_list.append(os.path.join(get_tmp_dir(), 'asrc_prep_compress'))
    is_handle_transformat = False
    if is_handle_transformat:
        mt_transformat_allow_prefix = ['audio', 'video', ]
        mt_transformat_allow = ['application/octet-stream', ]
        mt_transformat_notneed = ['audio/x-wav', ]

        transformat_tool = os.path.join(get_bin_dir(), 'ffmpeg')

        transformat_tmp_dir = os.path.join(get_tmp_dir(), 'asrc_prep_transformat')
        if not os.path.exists(transformat_tmp_dir):
            os.makedirs(transformat_tmp_dir, mode=0775)
        pending_dir_list.append(transformat_tmp_dir)

        for pending_dir in pending_dir_list:
            for root, dirs, files in os.walk(pending_dir):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    magic_type = magic.from_file(file_path, mime=True)
                    if magic_type.split('/')[0] not in mt_transformat_allow_prefix \
                            and magic_type not in mt_transformat_allow:
                        continue
                    if magic_type in mt_transformat_notneed:
                        continue
                    logger.info(u'MIME类型 -- 文件名：{} -- {}'.format(magic_type, file_path))

                    tmp_file_path = file_path.replace(pending_dir, transformat_tmp_dir)
                    tmp_file_name = os.path.basename(tmp_file_path)
                    # dst_file_dir = os.path.dirname(dst_file_path)
                    dst_file_dir = os.path.join(os.path.dirname(tmp_file_path), str(tmp_file_name).replace('.', '_'))
                    if not os.path.exists(dst_file_dir):
                        os.makedirs(dst_file_dir, mode=0775)
                    dst_file_name = os.path.splitext(tmp_file_name)[0] + '.wav'
                    dst_file_path = os.path.join(dst_file_dir, dst_file_name)

                    if magic_type.split('/')[0] in mt_transformat_allow_prefix:
                        cmd = '{handle_tool} -i "{file_src}" -n -f wav -ar 16000 -acodec pcm_s16le "{file_dst}"'.format(
                            handle_tool=transformat_tool,
                            file_src=file_path,
                            file_dst=dst_file_path,
                        )
                        logger.debug(cmd)
                        cmd_without_output = '{} 1>/dev/null 2>&1'.format(cmd)
                        return_code = sp.call([cmd_without_output, ], shell=True)
                        logger.info('return_code: {}'.format(return_code))
                        # sys.exit(1)
                    if magic_type in mt_transformat_allow:
                        if os.path.splitext(tmp_file_name)[1] == '.pcm':
                            cmd = '{handle_tool} -f s16le -ar 16000 -i "{file_src}" -n "{file_dst}"'.format(
                                handle_tool=transformat_tool,
                                file_src=file_path,
                                file_dst=dst_file_path,
                            )
                            logger.debug(cmd)
                            cmd_without_output = '{} 1>/dev/null 2>&1'.format(cmd)
                            return_code = sp.call([cmd_without_output, ], shell=True)
                            logger.info('return_code: {}'.format(return_code))
                        else:
                            cmd = '{handle_tool} -i "{file_src}" -y -f wav -ar 16000 -acodec pcm_s16le "{file_dst}"'.format(
                                handle_tool=transformat_tool,
                                file_src=file_path,
                                file_dst=dst_file_path,
                            )
                            # cmd = 'ffprobe -show_format /home/user/hezw/计量经济学课本\ \ \ \ \ （庞皓版）.pdf'
                            # cmd = 'ffprobe -show_format "{file_src}"'.format(
                            #                             #     file_src=file_path,
                            #                             # )
                            logger.debug(cmd)
                            cmd_without_output = '{} 1>/dev/null 2>&1'.format(cmd)
                            return_code = sp.call([cmd_without_output, ], shell=True)
                            logger.info('return_code: {}'.format(return_code))

    # wav文件改名，入库
    pending_dir_list.append(os.path.join(get_tmp_dir(), 'asrc_prep_transformat'))
    is_handle_rename = True
    if is_handle_rename:
        mt_rename_allow = ['audio/x-wav', ]

        audiosrc_fileinfo_list = []
        upload_time = current_timestamp_sec()
        for pending_dir in pending_dir_list:
            for root, dirs, files in os.walk(pending_dir):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    magic_type = magic.from_file(file_path, mime=True)
                    if magic_type not in mt_rename_allow:
                        continue
                    rel_path = os.path.relpath(file_path, pending_dir)
                    asrc_md5 = generate_file_md5(root, filename)
                    asrc_size = os.path.getsize(file_path)
                    asrc_uuid = get_uuid()
                    new_filename = asrc_uuid + '.wav'
                    file_url = os.path.join(time.strftime('/audiosrc/%Y/%m/%d', time.localtime(upload_time)),
                                            new_filename)

                    audiosrc_fileinfo = AudiosrcFileinfo()
                    audiosrc_fileinfo.asrc_uuid = asrc_uuid
                    audiosrc_fileinfo.asrc_url = file_url
                    audiosrc_fileinfo.asrc_md5 = asrc_md5
                    audiosrc_fileinfo.asrc_size = asrc_size
                    audiosrc_fileinfo.asrc_mime_type = magic_type
                    audiosrc_fileinfo.asrc_rel_path = rel_path
                    audiosrc_fileinfo.asrc_upload_time = upload_time
                    audiosrc_fileinfo.upload_uuid = upload_uuid
                    audiosrc_fileinfo.upload_dir = pending_dir

                    audiosrc_fileinfo_list.append(audiosrc_fileinfo)

        with app.app_context():
            audiosrc_fileinfo_dict_list = [dict(audiosrc_fileinfo) for audiosrc_fileinfo in audiosrc_fileinfo_list]
            with db_v2.auto_commit():
                db_v2.session.execute(AudiosrcFileinfo.__table__.insert().prefix_with('IGNORE'),
                                      audiosrc_fileinfo_dict_list)
                # db_v2.session.execute(AudiosrcFileinfo.__table__.insert(), audiosrc_fileinfo_dict_list)

            # TODO 唯一性处理要提前处理
            # with open(os.path.join(get_var_dir(), 'result.csv'), 'wb') as f:
            #     writer = csv.DictWriter(f, fieldnames=AudiosrcFileinfo().keys())
            #     writer.writeheader()
            #     writer.writerows(audiosrc_fileinfo_dict_list)

    # audio_file_list = []
    # audio_file_mark_list = []
    #
    # regions_dict = {}
    # rel_path_region_dict = {}
    # with app.app_context():
    #     regions = Region.query.filter_by().all()
    #     regions_dict = {r.name: r.id for r in regions}
    #
    # for root, dirs, files in os.walk(upload_dir):
    #     for filename in files:
    #
    #         rel_path = os.path.relpath(root, upload_dir)
    #         file_path = os.path.join(root, filename)
    #         magic_type = magic.from_file(file_path, mime=True)
    #         logger.info('{} {}'.format(magic_type, filename))
    #         if not magic_type.split('/')[0] in magic_type_prefix_allow:
    #             logger.info('{} {}'.format(magic_type, filename))
    #             continue

    # if magic_type != 'audio/x-wav':
    #     print u'%s 文件不是wave格式，而是%s' % (try_decode(file_path), magic_type)
    #     continue
    # file_md5 = generate_file_md5(root, filename)
    # basename, ext = os.path.splitext(filename)
    # ext = '.wav'
    # upload_time = current_timestamp_sec()
    # file_uuid = get_uuid()
    # new_filename = file_uuid + ext
    #
    # # 处理编码
    # filename = try_decode(filename)
    # rel_path = try_decode(rel_path)
    #
    # audio_file = AudioFile()
    # audio_file.file_name = filename
    # audio_file.file_uuid = file_uuid
    # audio_file.upload_time = upload_time
    # file_url = os.path.join(time.strftime('/audiosrc/%Y/%m/%d', time.localtime(upload_time)), new_filename)
    # audio_file.file_url = file_url
    # audio_file.file_md5 = file_md5
    # audio_file.analysis_status = 0
    # audio_file.insert_time = upload_time
    # audio_file.rel_path = rel_path
    #
    # audio_file_list.append(audio_file)
    #
    # # 跟上面的的region字典整合成guess_region_from_string的函数
    # mark_region = rel_path_region_dict.get(rel_path, None)
    # if not mark_region:
    #     contain_region_list = []
    #     for region_name in regions_dict.keys():
    #         if region_name in rel_path:
    #             contain_region_list.append(region_name)
    #     rel_path_region_dict[rel_path] = ','.join(contain_region_list)
    #     mark_region = rel_path_region_dict.get(rel_path, None)
    #
    # if mark_region:
    #     audio_file_mark2 = AudioFileMark()
    #     audio_file_mark2.insert_time = upload_time
    #     audio_file_mark2.file_uuid = file_uuid
    #     audio_file_mark2.mark_key = u'地区'
    #     audio_file_mark2.mark_value = mark_region
    #
    #     audio_file_mark_list.append(audio_file_mark2)
    # with app.app_context():
    #     with db_v1.auto_commit():
    #         for audio_file in audio_file_list:
    #             db_v1.session.add(audio_file)
    #         for audio_file_mark in audio_file_mark_list:
    #             db_v1.session.add(audio_file_mark)
    #     # /home/admin/online_label_system/label_data/audiosrc/2019/05/30/6195511b3a424be686970a042242593b.wav
    #
    #     file_server_dir = '/home/admin/online_label_system/label_data'
    #     for audio_file in audio_file_list:
    #         s_dir = os.path.join(upload_tmp_dir, audio_file.rel_path)
    #         s_path = os.path.join(s_dir, audio_file.file_name)
    #         d_path = os.path.join(file_server_dir, audio_file.file_url[1:])
    #         d_dir = os.path.dirname(d_path)
    #         if not os.path.isdir(d_dir):
    #             os.makedirs(d_dir)
    #         shutil.move(s_path, d_path)
    #         print u'文件 %s 已成功存储到 %s' % (audio_file.file_name, d_dir)


class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def run(self, timeout):
        def target():
            print 'Thread started'
            self.process = subprocess.Popen(self.cmd, shell=True)
            self.process.communicate()
            print 'Thread finished'

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            print 'Terminating process'
            self.process.terminate()
            thread.join()
        print self.process.returncode


def mov_file():
    app = create_app(os.getenv('FLASK_CONFIG') or 'default', logging_cfg='./cfg/logging_ds.yaml')
    logger = app.logger

    dst_dir = '/home/admin/online_label_data'
    with app.app_context():
        asrc_fileinfo_list = AudiosrcFileinfo.query.filter(
            AudiosrcFileinfo.is_deleted == 0,
        )

        for asrc_fileinfo in asrc_fileinfo_list:

            print asrc_fileinfo.upload_dir, asrc_fileinfo.asrc_rel_path, asrc_fileinfo.asrc_url

            src_file = os.path.join(asrc_fileinfo.upload_dir, asrc_fileinfo.asrc_rel_path)
            if not os.path.exists(src_file):
                continue

            dst_rel_path = asrc_fileinfo.asrc_url
            if dst_rel_path[0] == '/':
                dst_rel_path = dst_rel_path[1:]
            dst_file = os.path.join(dst_dir, dst_rel_path)
            if os.path.exists(dst_file):
                continue
            dst_file_dir = os.path.dirname(dst_file)
            if not os.path.exists(dst_file_dir):
                os.makedirs(dst_file_dir, mode=0775)
            shutil.move(src_file, dst_file)
            logger.info('{} --> {}'.format(src_file, dst_file))


def do_recog():
    app = create_app(os.getenv('FLASK_CONFIG') or 'default', logging_cfg='./cfg/logging_ds.yaml')
    logger = app.logger

    dst_dir = '/home/admin/online_label_data'
    with app.app_context():
        asrc_fileinfo_list = AudiosrcFileinfo.query.filter(
            AudiosrcFileinfo.is_deleted == 0,
        ).all()
        print len(asrc_fileinfo_list)

        asrc_filetrans_list = AudiosrcFiletrans.query.filter(
            AudiosrcFiletrans.is_deleted == 0,
        ).all()

        recoged_file_list = [a.file_uuid for a in asrc_filetrans_list]
        print len(recoged_file_list)

        asrc_filetrans_tasks = defaultdict(dict)
        ng_version = get_ng_version()
        for asrc_fileinfo in asrc_fileinfo_list:
            file_uuid = asrc_fileinfo.asrc_uuid
            if file_uuid in recoged_file_list:
                continue

            dst_rel_path = asrc_fileinfo.asrc_url
            if dst_rel_path[0] == '/':
                dst_rel_path = dst_rel_path[1:]
            dst_file = os.path.join(dst_dir, dst_rel_path)
            if not os.path.exists(dst_file):
                continue

            task_id = FileTransRestful(file_path=dst_file, protocol='file').register_file_flow()
            print task_id, asrc_fileinfo.asrc_uuid
            asrc_filetrans_tasks[task_id]['dst_file'] = dst_file
            asrc_filetrans_tasks[task_id]['file_uuid'] = asrc_fileinfo.asrc_uuid

            # break

        asr_ft_list = []
        for task_id, asrc_ft_dict in asrc_filetrans_tasks.items():
            # print task_id
            asrc_ft = AudiosrcFiletrans()
            asrc_ft.file_uuid = asrc_filetrans_tasks[task_id]['file_uuid']
            asrc_ft.ft_task_id = task_id
            asrc_ft.ng_version = ng_version
            # print dict(asrc_ft)
            asr_ft_list.append(asrc_ft)
        print len(asr_ft_list)

        with db_v2.auto_commit():
            db_v2.session.bulk_save_objects(asr_ft_list)
            # for asr_ft in asr_ft_list:
            #     db_v2.session.add(asr_ft)

        # asrc_ft.file_uuid = asrc_filetrans_tasks[task_id]['file_uuid']
    time.sleep(3)
    pass


def wait_for_finished(task_id_list, sleep_epoch=2, timeout=None):
    _check_queue = task_id_list
    succ_task = []
    fail_task = []
    non_valid_task = []  # 包含非法task_id和超时的
    _timeout = timeout or 60 * 15

    cur_time = current_timestamp_sec()
    while True:
        # print len(_check_queue)
        if (current_timestamp_sec() - cur_time) > _timeout:
            print u"超时跳出"
            non_valid_task = non_valid_task + _check_queue
            break

        if len(_check_queue) < 1:
            break
        task_id = _check_queue.pop()
        result = FileTransRestful.get_redis_result(task_id)

        if not result:
            non_valid_task.append(task_id)
            continue

        status_text = result['status_text']

        if 'QUEUEING' == status_text or 'RUNNING' == status_text:
            _check_queue.append(task_id)
            time.sleep(sleep_epoch)
        elif 'SUCCESS_WITH_NO_VALID_FRAGMENT' == status_text or 'SUCCESS' == status_text:
            succ_task.append(task_id)
        else:
            fail_task.append(task_id)
    return succ_task, fail_task, non_valid_task


def wait_recog():

    app = create_app(os.getenv('FLASK_CONFIG') or 'default', logging_cfg='./cfg/logging_ds.yaml')
    logger = app.logger

    dst_dir = '/home/admin/online_label_data'

    succ_task = []
    fail_task = []
    non_valid_task = []  # 包含非法task_id和超时的

    with app.app_context():
        asrc_recog_list = db_v2.session.query(AudiosrcFileinfo, AudiosrcFiletrans).filter(
            AudiosrcFileinfo.asrc_uuid == AudiosrcFiletrans.file_uuid,
            AudiosrcFiletrans.is_deleted == 0,
            AudiosrcFileinfo.is_deleted == 0,
            # AudiosrcFiletrans.ft_status_code.notin_(['21050003', '21050000']),
        ).all()

        print len(asrc_recog_list)
        with db_v2.auto_commit():

            for asrc_finfo, asrc_ft in asrc_recog_list:
                task_id = asrc_ft.ft_task_id
                print task_id
                result = FileTransRestful.get_redis_result(task_id)

                if not result:
                    non_valid_task.append(task_id)
                    continue

                status_text = result['status_text']
                status_code = result['status_code']

                if 'QUEUEING' == status_text or 'RUNNING' == status_text:
                    time.sleep(3)
                else:
                    asrc_ft.ft_status_text = status_text
                    asrc_ft.ft_status_code = status_code
                    redis_text = {
                        'request': FileTransRestful.get_redis_request(task_id),
                        'running': FileTransRestful.get_redis_running(task_id),
                        'result': FileTransRestful.get_redis_result(task_id),
                    }
                    asrc_ft.ft_redis_text = json.dumps(redis_text, indent=2, ensure_ascii=False)
                    asrc_ft.ft_log_text = FileTransRestful.get_ft_log_info(task_id)

                    tmp_filepath = FileTransRestful.get_tmp_file_path(task_id)
                    print tmp_filepath
                    if os.path.exists(tmp_filepath):
                        dst_rel_path = asrc_finfo.asrc_url
                        if dst_rel_path[0] == '/':
                            dst_rel_path = dst_rel_path[1:]
                        dst_file = os.path.join(dst_dir, dst_rel_path)
                        shutil.move(tmp_filepath, dst_file)


                # break



if __name__ == '__main__':
    # do_recog()
    # wait_recog()
    pass

    # command = Command(u'scp -i /home/admin/.ssh/id_rsa -l 500 /home/user/hezw/reg_need/福建福州/1106-1/113212/113212-审判长.wav root@192.168.106.170:/home/user/hezw/scp_test/1232.wav')
    # command.run(timeout=3)
    # command.run(timeout=1)

    # command = u'scp -i /home/admin/.ssh/id_rsa  /home/user/hezw/reg_need/福建福州/1106-1/113212/113212-审判长.wav root@192.168.106.170:/home/user/hezw/scp_test/1232.wav'
    # command = u'rsync -av -e "ssh -i /home/admin/.ssh/id_rsa" /home/user/hezw/reg_need/福建福州/1106-1/113212/113212-审判长.wav root@192.168.106.170:/home/user/hezw/scp_test2/2019/22'
    # password = 'yjyjs123'
    #
    # try:
    #     ssh = pexpect.spawn(command, timeout=3000)
    #     i = ssh.expect(['password:', 'continue connecting (yes/no)?', pexpect.EOF], timeout=5)
    #     print i
    #     if i == 0:
    #         ssh.sendline(password)
    #     elif i == 1:
    #         ssh.sendline('yes')
    #         ssh.expect('password: ')
    #         ssh.sendline(password)
    #     ssh.read()
    #     # ssh.exitstatus
    #     # ssh.status
    #     ssh.close()
    # except Exception as exp:
    #     print(traceback.format_exc())
    #     print(exp.message)

    # import subprocess as sp
    #
    # child = sp.Popen(command, shell=True, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE).wait()
    # # streamdata = child.communicate(input='yjyjs123')
    # child.stdin.write('yjyjs123\n')
    # child.stdin.flush()
    # streamdata = child.communicate()
    # return_code = child.returncode
    # print return_code
    # print streamdata
    # if return_code != 0:
    #     logger.error(streamdata[1])
    #     logger.info(u'建立{}数据表失败'.format(bind.name))
    # else:
    #     logger.info(streamdata[0])
    #     logger.info(u'建立{}数据表成功'.format(bind.name))
    # pass
    # 只调用restful接口
    # parser = argparse.ArgumentParser()
    # audiosrc_prepare()
    # command = '{handle_tool} x {{filepath}}'
    # print command.format(handle_tool='abc').format(filepath='123')

    # 只解析
    # parser()

    # audiosrc_prepare()
