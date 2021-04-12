# -*- coding: utf-8 -*-
import json
import logging
import traceback

import codecs
import httplib2
import os
from datetime import datetime
from flask import current_app
from sqlalchemy import desc, asc

from app.api.sysmgr.async_req import create_async_req, done_async_req, run_async_req, get_async_req_default_future
from app.libs.enums import AsyncReqStatusEnum, AsyncReqTypeEnum, PrepareTypeEnum
from app.libs.error_code import ResultSuccess, PageResultSuccess
from app.libs.qpaginate import pager
from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.models.base import asynchronous_executor, db_v2, DB_V2_TABLE_PREFIX
from app.models.v2.engine.ng import NgDitingRelation, NgDiting
from app.models.v2.engine.utterance import UtteranceAudio, UtteranceAccess
from app.models.v2.web.common import AsyncReq
from app.models.v2.web.label import LabelResult, LabelUtteranceInfo, LabelDitingInfo
from app.models.v2.web.sysmgr import User
from app.validators.base import PageForm, ColumnSortForm
from app.validators.forms_v2 import BgprocParseSearchForm, UtteranceSVSearchForm, UtteranceIDListForm
from local_api.data_prepare import DataPrepare

api = Redprint('bgproc')
logger = logging.getLogger(__name__)


@api.route('/select-label', methods=['POST'])
@auth.login_required
def bgproc_select_web():
    dp = DataPrepare()
    p_res = json.loads(dp.prepare_data(prepare_type=PrepareTypeEnum.LABEL_DATA.value))

    return ResultSuccess(msg=u'标注数据自动挑选开始', data=p_res)


@api.route('/list-parse-log', methods=['POST'])
@auth.login_required
def bgproc_list_parse_log():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())
    form = BgprocParseSearchForm().validate_for_api()

    q = db_v2.session.query(AsyncReq, User).filter(
        AsyncReq.is_deleted == 0,
        AsyncReq.req_type == AsyncReqTypeEnum.LOG_PARSER_SV.value,
        AsyncReq.req_create_uid == User.id
    ).order_by(desc(AsyncReq.req_create_time))

    if form.label_time_left.data:
        q = q.filter(AsyncReq.req_create_time >= form.label_time_left.data)
    if form.label_time_right.data:
        q = q.filter(AsyncReq.req_create_time <= form.label_time_right.data)
    if form.req_status.data is not None and form.req_status.data != '':
        q = q.filter(AsyncReq.req_status == form.req_status.data)

    rvs = pager(q, page=cur_page, per_page=per_page)

    vms = []
    for rv in rvs.items:
        rv_dict = {c: getattr(rv, c, None) for c in rv._fields}
        vm = dict(rv_dict['AsyncReq'])
        vm['creator_name'] = rv_dict['User'].nickname
        vm['result_msg'] = json.loads(rv_dict['AsyncReq'].req_result or '{}', encoding='utf8').get('result_msg')
        vms.append(vm)

    return PageResultSuccess(msg=u'解析历史页面', data=vms, page=rvs.page_view())


@api.route('/parse-log', methods=['POST'])
@auth.login_required
def bgproc_parse_log():
    req_uuid = create_async_req(AsyncReqTypeEnum.LOG_PARSER_SV.value)
    asynchronous_executor.submit(invoke_log_parser, req_uuid).add_done_callback(done_async_req)
    return ResultSuccess(msg=u'数据解释开始', data={'req_uuid': req_uuid})


def invoke_log_parser(req_uuid):
    run_async_req(req_uuid)
    async_future = get_async_req_default_future(req_uuid)

    base_plugin_cfg = current_app.config.get('PLUGINS')
    if not base_plugin_cfg:
        async_future['req_status'] = AsyncReqStatusEnum.FAILED.value
        async_future['req_errno'] = 5002001
        async_future['req_errmsg'] = 'FAILED'
        async_future['req_result'] = json.dumps(dict(result_msg=u'插件模块配置不存在'), ensure_ascii=False)
        return async_future

    log_parser_cfg = base_plugin_cfg.get('LOG_PARSER')
    if not log_parser_cfg:
        async_future['req_status'] = AsyncReqStatusEnum.FAILED.value
        async_future['req_errno'] = 5002002
        async_future['req_errmsg'] = 'FAILED'
        async_future['req_result'] = json.dumps(dict(result_msg=u'解析入库模块配置不存在'), ensure_ascii=False)
        return async_future

    log_parser_params_verify = ['PLUGIN_PATH', 'PLUGIN_MAIN_RUNNER', 'PLUGIN_VENV_PATH', ]
    params_lost = []
    for param_need in log_parser_params_verify:
        if not log_parser_cfg.get(param_need):
            params_lost.append(param_need)
    if len(params_lost) > 0:
        async_future['req_status'] = AsyncReqStatusEnum.FAILED.value
        async_future['req_errno'] = 5002003
        async_future['req_errmsg'] = 'FAILED'
        async_future['req_result'] = json.dumps(dict(result_msg=u'解析入库模块配置不正确，缺少参数 {}'.format(','.join(params_lost))),
                                                ensure_ascii=False)
        return async_future

    log_parser_modules_dir = log_parser_cfg['PLUGIN_PATH']
    if not log_parser_modules_dir[0] == '/':
        log_parser_modules_dir = os.path.abspath(os.path.join(current_app.root_path, log_parser_modules_dir))
    log_parser_main_runner_path = log_parser_cfg['PLUGIN_MAIN_RUNNER']
    if not log_parser_main_runner_path[0] == '/':
        log_parser_main_runner_path = os.path.abspath(os.path.join(log_parser_modules_dir, log_parser_main_runner_path))
    log_parser_venv_path = log_parser_cfg['PLUGIN_VENV_PATH']
    if not log_parser_venv_path[0] == '/':
        log_parser_venv_path = os.path.abspath(os.path.join(log_parser_modules_dir, log_parser_venv_path))
    print log_parser_venv_path
    print log_parser_main_runner_path
    try:
        command_list = [
            'source %s/bin/activate' % log_parser_venv_path,
            'python %s' % log_parser_main_runner_path,
        ]

        ret = os.system(' && '.join(command_list))

        if ret == 0:
            async_future['req_status'] = AsyncReqStatusEnum.SUCCESS.value
            async_future['req_errno'] = 2001000
            async_future['req_errmsg'] = 'SUCCESS'
            async_future['req_result'] = json.dumps(dict(result_msg=u'解析成功'), ensure_ascii=False)
        else:
            raise Exception(u'log parser call failed!')

    except Exception as exp:
        logger.error(traceback.format_exc())

        async_future['req_status'] = AsyncReqStatusEnum.FAILED.value
        async_future['req_errno'] = 5001000
        async_future['req_errmsg'] = 'FAILED'
        async_future['req_result'] = json.dumps(dict(result_msg=exp.message), ensure_ascii=False)
        return async_future

    return async_future


@api.route('/list-download-sv', methods=['POST'])
@auth.login_required
def bgproc_list_download_supervisor():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())
    form = BgprocParseSearchForm().validate_for_api()

    q = db_v2.session.query(AsyncReq, User).filter(
        AsyncReq.is_deleted == 0,
        AsyncReq.req_type == AsyncReqTypeEnum.DOWNLOAD_SV.value,
        AsyncReq.req_create_uid == User.id
    ).order_by(desc(AsyncReq.req_create_time))

    if form.label_time_left.data:
        q = q.filter(AsyncReq.req_create_time >= form.label_time_left.data)
    if form.label_time_right.data:
        q = q.filter(AsyncReq.req_create_time <= form.label_time_right.data)
    if form.req_status.data is not None and form.req_status.data != '':
        q = q.filter(AsyncReq.req_status == form.req_status.data)

    rvs = pager(q, page=cur_page, per_page=per_page)

    vms = []
    for rv in rvs.items:
        rv_dict = {c: getattr(rv, c, None) for c in rv._fields}
        vm = dict(rv_dict['AsyncReq'])
        vm['creator_name'] = rv_dict['User'].nickname
        vm['result_msg'] = json.loads(rv_dict['AsyncReq'].req_result or '{}', encoding='utf8').get('result_msg')
        vm['download_path'] = json.loads(rv_dict['AsyncReq'].req_result or '{}', encoding='utf8').get('download_path')
        vms.append(vm)

    return PageResultSuccess(msg=u'运维下载历史页面', data=vms, page=rvs.page_view())


@api.route('/download-audio', methods=['POST'])
@auth.login_required
def download_audio():
    req_uuid = create_async_req(AsyncReqTypeEnum.DOWNLOAD_SV.value)

    req_id_list = UtteranceIDListForm().validate_for_api().req_id_list.data
    asynchronous_executor.submit(download_utterance_data, req_uuid, req_id_list).add_done_callback(done_async_req)
    return ResultSuccess(msg=u'数据下载开始', data={'req_uuid': req_uuid})


@api.route('/download-all-sv-audio', methods=['POST'])
@auth.login_required
def download_all_supervisor_audio():
    req_uuid = create_async_req(AsyncReqTypeEnum.DOWNLOAD_SV.value)

    column_name, column_order = ColumnSortForm.fetch_column_param(ColumnSortForm().validate_for_api())
    form = UtteranceSVSearchForm().validate_for_api()
    column_obj_map = {
        'al_engine': {
            'id': UtteranceAudio.id,  # default

            'request_id': UtteranceAudio.request_id,
            'truncation_ratio': UtteranceAudio.truncation_ratio,
            'volume': UtteranceAudio.volume,
            'pre_snr': UtteranceAudio.pre_snr,
            'post_snr': UtteranceAudio.post_snr,

            'time': UtteranceAccess.time,
            'result': UtteranceAccess.result,
            'real_rtf': UtteranceAccess.real_rtf,
            'total_rtf': UtteranceAccess.total_rtf,
            'latency': UtteranceAccess.latency,
            'total_cost_time': UtteranceAccess.total_cost_time,
            'process_time': UtteranceAccess.process_time,
            'receive_cost_time': UtteranceAccess.receive_cost_time,
            'wait_cost_time': UtteranceAccess.wait_cost_time,
            'raw_rtf': UtteranceAccess.raw_rtf,
            'avg_packet_duration': UtteranceAccess.avg_packet_duration,
            'packet_count': UtteranceAccess.packet_count,
            'audio_format': UtteranceAccess.audio_format,
            'sample_rate': UtteranceAccess.sample_rate,
            'detect_duration': UtteranceAccess.detect_duration,

            'court_id': NgDitingRelation.court_id,
            'case_id': NgDitingRelation.case_id,
            'role_id': NgDitingRelation.role_id,

        },
        '{}web'.format(DB_V2_TABLE_PREFIX): {
            # 'id': LabelUtteranceInfo.id,  # default
            'label_text': LabelResult.label_text,
            'label_status': LabelResult.label_status,
            'wer': LabelResult.wer,
            'ins_cnt': LabelResult.ins_cnt,
            'sub_cnt': LabelResult.sub_cnt,
            'del_cnt': LabelResult.del_cnt,
        }
    }

    db_in_search = [db_name for db_name in column_obj_map.keys() if column_name in column_obj_map[db_name].keys()][0]
    if form.task_code.data and form.task_code.data != '':
        db_in_search = '{}web'.format(DB_V2_TABLE_PREFIX)
    if form.label_status.data is not None and form.label_status.data != '':
        db_in_search = '{}web'.format(DB_V2_TABLE_PREFIX)
    logger.info('searching db: {}'.format(db_in_search))

    req_id_list = []

    if db_in_search == '{}engine'.format(DB_V2_TABLE_PREFIX):
        q = db_v2.session.query(UtteranceAudio).filter(
            UtteranceAudio.request_id == UtteranceAccess.request_id,
            UtteranceAccess.request_id == NgDiting.request_id,
            NgDiting.uuid == NgDitingRelation.uuid).filter(
            UtteranceAudio.is_deleted == 0,
            UtteranceAccess.is_deleted == 0
        )

        if form.label_time_left.data:
            q = q.filter(UtteranceAccess.time >= datetime.fromtimestamp(form.label_time_left.data))
        if form.label_time_right.data:
            q = q.filter(UtteranceAccess.time <= datetime.fromtimestamp(form.label_time_right.data))
        if form.court_id.data and form.court_id.data != '':
            q = q.filter(NgDitingRelation.court_id.like('%' + form.court_id.data + "%"))
        if form.case_id.data and form.case_id.data != '':
            q = q.filter(NgDitingRelation.case_id.like('%' + form.case_id.data + "%"))
        if form.role_id.data and form.role_id.data != '':
            q = q.filter(NgDitingRelation.role_id.like('%' + form.role_id.data + "%"))

        if column_order == 'ascending':
            q = q.order_by(asc(column_obj_map[db_in_search].get(column_name, UtteranceAudio.id)))
        else:
            q = q.order_by(desc(column_obj_map[db_in_search].get(column_name, UtteranceAudio.id)))

        req_id_list = list(set([uttr_audio.request_id for uttr_audio in q.all()]))
    elif db_in_search == '{}web'.format(DB_V2_TABLE_PREFIX):
        q = db_v2.session.query(LabelUtteranceInfo).filter(
            LabelUtteranceInfo.request_id == LabelDitingInfo.request_id,
            LabelUtteranceInfo.request_id == LabelResult.request_id,
            LabelUtteranceInfo.is_deleted == 0,
            LabelDitingInfo.is_deleted == 0,
            LabelResult.is_deleted == 0,
        )

        if form.label_time_left.data:
            q = q.filter(LabelUtteranceInfo.time >= datetime.fromtimestamp(form.label_time_left.data))
        if form.label_time_right.data:
            q = q.filter(LabelUtteranceInfo.time <= datetime.fromtimestamp(form.label_time_right.data))
        if form.court_id.data and form.court_id.data != '':
            q = q.filter(LabelDitingInfo.court_id.like('%' + form.court_id.data + "%"))
        if form.case_id.data and form.case_id.data != '':
            q = q.filter(LabelDitingInfo.case_id.like('%' + form.case_id.data + "%"))
        if form.role_id.data and form.role_id.data != '':
            q = q.filter(LabelDitingInfo.role_id.like('%' + form.role_id.data + "%"))
        if form.task_code.data and form.task_code.data != '':
            q = q.filter(LabelResult.task_code.like('%' + form.task_code.data + "%"))
        if form.label_status.data is not None and form.label_status.data != '':
            q = q.filter(LabelResult.label_status == form.label_status.data)
        if column_order == 'ascending':
            q = q.order_by(asc(column_obj_map[db_in_search].get(column_name, LabelUtteranceInfo.id)))
        else:
            q = q.order_by(desc(column_obj_map[db_in_search].get(column_name, LabelUtteranceInfo.id)))
        req_id_list = list(set([uttr_info.request_id for uttr_info in q.all()]))

    asynchronous_executor.submit(download_utterance_data, req_uuid, req_id_list).add_done_callback(done_async_req)
    return ResultSuccess(msg=u'数据下载开始', data={'req_uuid': req_uuid})


def download_utterance_data(req_uuid, req_id_list):
    async_req = run_async_req(req_uuid)
    if not async_req:
        logger.error(u'下载运维语句音频，启动失败')
        return None

    async_future = get_async_req_default_future(req_uuid)

    # 查出音频url对于文件服务器的相对路径

    try:
        uttr_audio_list = []
        select_in_step = current_app.config['SQLALCHEMY_CUSTOM_SELECT_IN_STEP']  # TODO 封装
        select_in_from = 0
        select_in_to = select_in_from + select_in_step
        select_in_loop_counter = 0
        select_in_loop_counter_limit = int(len(req_id_list) / select_in_step) + 2
        while True:
            if len(req_id_list[
                   select_in_from:select_in_to]) < 1 or select_in_loop_counter > select_in_loop_counter_limit:
                logger.debug('counter: {}'.format(select_in_loop_counter))
                break

            rvs_part = UtteranceAudio.query.filter(
                UtteranceAudio.request_id.in_(req_id_list[select_in_from:select_in_to])).all()
            uttr_audio_list += rvs_part

            select_in_from = select_in_to
            select_in_to = select_in_from + select_in_step
            select_in_loop_counter += 1
        logger.debug('uttr_audio_list length: {}'.format(len(uttr_audio_list)))
    except Exception as e:
        logger.error(traceback.format_exc())

        async_future['req_status'] = AsyncReqStatusEnum.FAILED.value
        async_future['req_errno'] = 5001001
        async_future['req_errmsg'] = 'FAILED'
        async_future['req_result'] = json.dumps(dict(result_msg=e.message), ensure_ascii=False)
        return async_future

    if len(uttr_audio_list) < 1:
        async_future['req_status'] = AsyncReqStatusEnum.FAILED.value
        async_future['req_errno'] = 4001001
        async_future['req_errmsg'] = 'FAILED'
        req_result_dict = dict(
            result_msg=u'筛选的语句全部不存在',
            download_path=''
        )
        async_future['req_result'] = json.dumps(req_result_dict, ensure_ascii=False)
        return async_future

    # 下载
    try:
        download_target_dir = current_app.config['DATA_DOWNLOAD_SV_TARGET_DIR']
        sub_dir = str(async_req.id).zfill(7)
        download_target_dir = os.path.join(download_target_dir, sub_dir)
        if not os.path.exists(download_target_dir):
            os.makedirs(download_target_dir)
        logger.info(u'下载目标路径：{}'.format(download_target_dir))

        success_list = []
        fail_list = []
        for uttr_audio in uttr_audio_list:
            uttr_url = current_app.config['UTTERANCE_FILE_SERVER'] + uttr_audio.url
            download_result = download_uttr_audio_by_http(download_target_dir, uttr_url)
            if download_result['status']:
                success_list.append((uttr_audio, download_result['msg']))
            else:
                fail_list.append((uttr_audio, download_result['msg']))

        download_situation_log = 'download_situation.log'
        download_situation_log = os.path.join(download_target_dir, download_situation_log)
        with codecs.open(download_situation_log, 'a+', encoding='utf-8') as f:
            f.writelines(u'下载任务：{}\n'.format(req_uuid))
            f.writelines(u'成功下载条数：{}\n'.format(len(success_list)))
            f.writelines(u'失败下载条数：{}\n'.format(len(fail_list)))
            f.writelines(u'\n成功下载语句ID：\n')
            for uttr_audio, msg in success_list:
                f.writelines(u'{}\n'.format(uttr_audio.request_id))

            f.writelines(u'\n失败下载语句ID：\n')
            for uttr_audio, msg in fail_list:
                f.writelines(u'{}\t{}\n'.format(uttr_audio.request_id, msg))

        async_future['req_status'] = AsyncReqStatusEnum.SUCCESS.value
        async_future['req_errno'] = 2001000
        async_future['req_errmsg'] = 'SUCCESS'
        req_result_dict = dict(
            result_msg=u'下载成功',
            download_path=download_target_dir
        )
        async_future['req_result'] = json.dumps(req_result_dict, ensure_ascii=False)

        if len(fail_list) > 0:
            async_future['req_status'] = AsyncReqStatusEnum.FAILED.value
            async_future['req_errno'] = 4001000
            async_future['req_errmsg'] = 'FAILED'
            req_result_dict['result_msg'] = u'下载部分失败，总共下载{}条：成功{}条，失败{}条'.format(
                len(uttr_audio_list), len(success_list), len(fail_list))
            async_future['req_result'] = json.dumps(req_result_dict, ensure_ascii=False)

    except Exception as e:
        logger.error(traceback.format_exc())

        async_future['req_status'] = AsyncReqStatusEnum.FAILED.value
        async_future['req_errno'] = 5001002
        async_future['req_errmsg'] = 'FAILED'
        async_future['req_result'] = json.dumps(dict(result_msg=e.message), ensure_ascii=False)
        return async_future

    return async_future


def download_uttr_audio_by_http(target_dir, uttr_url):
    downlaod_result = {
        'status': True,
        'msg': u'成功'
    }

    audio_filename = uttr_url.split('/')[-1]
    audio_filepath = os.path.join(target_dir, audio_filename)

    h = httplib2.Http()
    try:
        resp, content = h.request(uttr_url)
        if resp['status'] == '200':
            with open(audio_filepath, 'wb') as f:
                f.write(content)
        else:
            downlaod_result = {
                'status': False,
                'msg': resp['status']
            }
    except Exception as e:
        logger.error(traceback.format_exc())
        downlaod_result = {
            'status': False,
            'msg': e.message
        }

    return downlaod_result
