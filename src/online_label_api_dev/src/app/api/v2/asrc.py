# -*- coding: utf-8 -*-
import json
import logging
import shutil

import os
import time
from flask import current_app
from sqlalchemy import desc

from app.libs.asr_func.filetrans_handler import FileTransRestful
from app.libs.builtin_extend import exist_remote_file, current_timestamp_sec
from app.libs.error import APIException
from app.libs.error_code import PageResultSuccess, Success
from app.libs.ng_utils import get_ng_version, is_local_ng
from app.libs.qpaginate import pager
from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.models.base import db_v2, asynchronous_executor
from app.models.v2.engine.audiosrc import AudiosrcFileinfo, AudiosrcFiletrans
from app.validators.base import PageForm
from app.validators.forms_v2 import IDForm

api = Redprint('asrc')  # audio_source 录音原文件
logger = logging.getLogger(__name__)


@api.route('/list', methods=['POST'])
@auth.login_required
def asrc_list():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    q = db_v2.session.query(AudiosrcFileinfo).filter(
        AudiosrcFileinfo.is_deleted == 0,
    ).order_by(desc(AudiosrcFileinfo.id))

    rvs = pager(q, page=cur_page, per_page=per_page)

    vms = []
    vm_keys_asrc_fileinfo = ['id', 'asrc_uuid', 'asrc_url', 'asrc_md5', 'asrc_size', 'asrc_mime_type',
                             'asrc_rel_path', 'asrc_upload_time', 'upload_uuid', 'upload_dir', ]
    for rv in rvs.items:
        vm = {}
        for v_key in vm_keys_asrc_fileinfo:
            vm[v_key] = getattr(rv, v_key, None)
        vm['asrc_file_name'] = os.path.basename(vm['asrc_rel_path'])
        vm['asrc_file_path'] = os.path.dirname(vm['asrc_rel_path'])
        vms.append(vm)

    return PageResultSuccess(msg=u'录音文件列表', data=vms, page=rvs.page_view())


@api.route('/recog', methods=['POST'])
@auth.login_required
def asrc_recognition():
    id = IDForm().validate_for_api().id.data
    asrc_finfo = AudiosrcFileinfo.query.filter_by(id=id).first_or_404()

    asrc_ft = AudiosrcFiletrans()
    asrc_ft.ng_version = get_ng_version() or '2'
    asrc_ft.file_uuid = asrc_finfo.asrc_uuid
    asrc_ft.ft_task_id = None
    asrc_ft.ft_status_code = '10000000'
    asrc_ft.ft_status_text = u'未开始'
    asrc_ft.ft_redis_text = None
    asrc_ft.ft_log_text = None

    with db_v2.auto_commit():
        db_v2.session.add(asrc_ft)

    # 检查文件是否存在
    local_ng_flag = is_local_ng()
    file_exist_flag = False
    ft_filepath_full = None
    if local_ng_flag:   # 如果是本地引擎，则先检测本地文件路径
        rel_url = asrc_finfo.asrc_url
        if rel_url[0] == '/':
            rel_url = rel_url[1:]
        ft_filepath_full = os.path.join(current_app.config['ASRC_SAVE_DIR'], rel_url)
        file_exist_flag = os.path.exists(ft_filepath_full)

    if not file_exist_flag: # 本地路径不存在，再检测remote文件服务器
        local_ng_flag = False
        ft_filepath_full = current_app.config['UTTERANCE_FILE_SERVER'] + asrc_finfo.asrc_url
        file_exist_flag = exist_remote_file(ft_filepath_full)

    if not file_exist_flag:
        status_text = u'录音文件内部丢失：uuid为{}, 路径为{}'.format(asrc_finfo.asrc_uuid, ft_filepath_full)
        logger.error(status_text)
        with db_v2.auto_commit():
            asrc_ft.ft_status_code = '51000000'
            asrc_ft.ft_status_text = status_text
        raise APIException(msg=status_text, error_code=5100)

    if local_ng_flag:
        task_id = FileTransRestful(file_path=ft_filepath_full, protocol='file').register_file_flow()
    else:
        task_id = FileTransRestful(file_path=ft_filepath_full, protocol='http').register_file_flow()

    if task_id:
        with db_v2.auto_commit():
            asrc_ft.ft_task_id = task_id
            asrc_ft.ft_status_code = '10000001'
            asrc_ft.ft_status_text = u'识别中'

    asynchronous_executor.submit(check_recognition_finish, task_id, asrc_ft.file_uuid)

    return Success(msg=u'录音文件识别请求成功')
    # return CreateSuccess(msg=u'录音文件识别成功', data="test")


def check_recognition_finish(task_id, file_uuid):
    asrc_ft = AudiosrcFiletrans.query.filter(
        AudiosrcFiletrans.ft_task_id == task_id,
        AudiosrcFiletrans.file_uuid == file_uuid,
    ).first()
    print task_id

    if not asrc_ft:
        return

    result = None
    status_code = asrc_ft.ft_status_code
    status_text = asrc_ft.ft_status_text
    timeout = 60*15 # 15分钟
    sleep_time = 3
    cur_time = current_timestamp_sec()
    while True:
        result = FileTransRestful.get_redis_result(task_id)

        if (current_timestamp_sec() - cur_time) > timeout:

            status_code = '51000003'
            status_text = u'识别超市{}秒，task_id为{}'.format(timeout, task_id)
            break

        if not result:
            status_code = '51000002'
            status_text = u'没有识别结果，task_id为{}'.format(task_id)
            break

        status_code = result['status_code']
        status_text = result['status_text']
        if 'QUEUEING' == status_text or 'RUNNING' == status_text:
            time.sleep(sleep_time)
        else:
            break

    with db_v2.auto_commit():
        asrc_ft.ft_status_code = status_code
        asrc_ft.ft_status_text = status_text
        redis_text = {
            'request': FileTransRestful.get_redis_request(task_id),
            'running': FileTransRestful.get_redis_running(task_id),
            'result': FileTransRestful.get_redis_result(task_id),
        }
        asrc_ft.ft_redis_text = json.dumps(redis_text, indent=2, ensure_ascii=False)
        asrc_ft.ft_log_text = FileTransRestful.get_ft_log_info(task_id)

    # 恢复文件位置
    file_tmp_path = FileTransRestful.get_tmp_file_path(task_id)
    if file_tmp_path and os.path.exists(file_tmp_path):
        asrc_finfo = AudiosrcFileinfo.query.filter_by(asrc_uuid=file_uuid).first()
        if asrc_finfo:
            file_src_path = asrc_finfo.asrc_url
            if file_src_path[0] == '/':
                file_src_path = file_src_path[1:]
            file_src_path = os.path.join(current_app.config['ASRC_SAVE_DIR'], file_src_path)
            logger.debug(u'文件迁移：{} --> {}'.format(file_tmp_path, file_src_path))
            shutil.move(file_tmp_path, file_src_path)


    logger.info(u'识别结束')







@api.route('/list-recog', methods=['POST'])
@auth.login_required
def asrc_list_recognition():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    q = db_v2.session.query(AudiosrcFiletrans).filter(
        AudiosrcFiletrans.is_deleted == 0,
    ).order_by(desc(AudiosrcFiletrans.id))

    rvs = pager(q, page=cur_page, per_page=per_page)

    vms = []
    vm_keys_asrc_filetrans = ['id', 'ng_version', 'file_uuid', 'ft_task_id', 'ft_status_code', 'ft_status_text',
                              'ft_redis_text', 'ft_log_text', ]

    for rv in rvs.items:
        vm = {}
        for v_key in vm_keys_asrc_filetrans:
            vm[v_key] = getattr(rv, v_key, None)
        vms.append(vm)

    return PageResultSuccess(msg=u'录音文件识别历史', data=vms, page=rvs.page_view())
