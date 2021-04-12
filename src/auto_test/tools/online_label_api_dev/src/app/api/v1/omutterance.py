# -*- coding: utf-8 -*-
import logging
import shutil
import sys

import os
import time
from datetime import datetime
from flask import g, current_app
from sqlalchemy import or_

from app.libs.builtin_extend import datetime2timestamp
from app.libs.error_code import PageResultSuccess, ResultSuccess, ParameterException, CreateSuccess, ParserSuccess, \
    DownloadSuccess
from app.libs.file_utils import save_to_csv, zip_dir
from app.libs.qpaginate import pager
from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.models.base import db_v1, asynchronous_executor
from app.models.v1.omfile import AlNgDitingRelation, AlNgDiting, OmAsyncParserTask, OmAsyncDownloadTask
from app.models.v1.sysmng import User
from app.models.v1.tagfile import UtteranceAccess, Utterance
from app.models.v1.tagproj import TagTask, TagResult
from app.validators.base import PageForm
from app.validators.forms_v1 import OmDataSearchForm, OmCalcwerForm, OmTagTaskForm, OmParserForm, OmDownloadForm

api = Redprint('omutterance')
logger = logging.getLogger(__name__)


@api.route('/invoke-log-parser', methods=['POST'])
@auth.login_required
def omutterance_invoke_log_parser():
    form = OmParserForm().validate_for_api()
    # logger.info('解析开始')
    parser_time = form.parser_time.data / 1000

    parser_task = OmAsyncParserTask()
    with db_v1.auto_commit():
        form.populate_obj(parser_task)
        parser_task.start_time = parser_time
        parser_task.create_uid = g.user.uid
        parser_task.parser_status = 0
        db_v1.session.add(parser_task)
    id = parser_task.id

    asynchronous_executor.submit(invoke_log_parser, id).add_done_callback(done_log_parser)
    return ParserSuccess(msg=u'200', data={"code": 200})


def invoke_log_parser(id):
    paser_result = OmAsyncParserTask.query.filter_by(id=id).first_or_404()
    with db_v1.auto_commit():
        if paser_result:
            paser_result.parser_status = 1
            db_v1.session.add(paser_result)
    web_project_dir = os.path.dirname(current_app.instance_path)
    log_parser_dir = os.path.join(os.path.dirname(web_project_dir), 'log_parser')
    log_parser_process_path = os.path.join(log_parser_dir, 'src', 'run_log_parser.py')
    try:
        sys.path.insert(0, os.path.join(log_parser_dir, 'src'))
        import run_log_parser
        run_log_parser.RunLogParser(log_parser_process_path).main()
        finish_time = int(time.time())
        return dict(id=id, parser_status=2, result_msg="解析成功", finish_time=finish_time)

    except Exception as exp:
        finish_time = int(time.time())
        return dict(id=id, parser_status=3, result_msg=exp.message, finish_time=finish_time)


def done_log_parser(future):
    result = future.result()
    id = result.get("id")
    parser_status = result.get("parser_status")
    finish_time = result.get("finish_time")
    result_msg = result.get("result_msg")
    parser_result = OmAsyncParserTask.query.filter_by(id=id).first_or_404()
    with db_v1.auto_commit():
        if parser_result:
            parser_result.parser_status = parser_status
            parser_result.result_msg = result_msg
            parser_result.finish_time = finish_time
            db_v1.session.add(parser_result)


@api.route('/list', methods=['POST'])
@auth.login_required
def omutterance_list():
    page_form = PageForm().validate_for_api()
    cur_page = page_form.page.data if page_form.page.data else 1
    per_page = page_form.limit.data if page_form.limit.data else current_app.config['DEFAULT_LISTNUM_PER_PAGE']

    form = OmDataSearchForm().validate_for_api()
    column_name = form.column_name.data
    column_order = form.column_order.data

    is_outer_join = True

    task_ids = None
    # 这里是查出tagresult里面的taskids是什么
    if form.task_code.data and form.task_code.data != '':
        is_outer_join = False
        task_rvs = db_v1.session.query(TagTask.id).filter(
            TagTask.task_code.like('%' + form.task_code.data + "%")).filter_by().all()
        task_ids = [task_id for task_id, in task_rvs]
    sub_q = db_v1.session.query(TagResult.id.label('tag_result_id'),
                                TagResult.request_id.label('request_id'),
                                TagResult.is_deleted.label('tag_result_is_deleted'),
                                TagResult.tag_status.label('tag_status'),
                                TagResult.task_id.label('task_id'),
                                TagResult.proj_id.label('proj_id'),
                                TagResult.wer.label('wer'),
                                TagResult.sub_count.label('sub_count'),
                                TagResult.delete_count.label('delete_count'),
                                TagResult.insertion_count.label('insertion_count'),
                                TagResult.label_text.label('label_text'),
                                ) \
        .filter(TagResult.is_deleted == 0).subquery('sub_q')
    q = db_v1.session.query(
        UtteranceAccess.time.label('time'),
        Utterance.request_id.label('request_id'),
        UtteranceAccess.result.label('result'),
        UtteranceAccess.real_rtf.label('real_rtf'),
        Utterance.cut_ratio.label('cut_ratio'),
        Utterance.volume.label('volume'),
        Utterance.pre_snr.label('pre_snr'),
        Utterance.latter_snr.label('latter_snr'),
        UtteranceAccess.detect_duration.label('detect_duration'),
        sub_q.c.tag_status.label('tag_status'),
        sub_q.c.label_text.label('label_text'),
        sub_q.c.tag_result_id.label('tag_result_id'),
        sub_q.c.task_id.label('task_id'),
        sub_q.c.proj_id.label('proj_id'),
        sub_q.c.tag_result_is_deleted.label('tag_result_is_deleted'),
        sub_q.c.wer.label('wer'),
        sub_q.c.insertion_count.label('insertion_count'),
        sub_q.c.delete_count.label('delete_count'),
        sub_q.c.sub_count.label('sub_count'),
        UtteranceAccess.total_rtf.label('total_rtf'),
        UtteranceAccess.latency.label('latency'),
        UtteranceAccess.total_cost_time.label('total_cost_time'),
        UtteranceAccess.process_time.label('process_time'),
        UtteranceAccess.receive_cost_time.label('receive_cost_time'),
        UtteranceAccess.wait_cost_time.label('wait_cost_time'),
        UtteranceAccess.raw_rtf.label('raw_rtf'),
        UtteranceAccess.avg_packet_duration.label('avg_packet_duration'),
        UtteranceAccess.packet_count.label('packet_count'),
        UtteranceAccess.audio_format.label('audio_format'),
        UtteranceAccess.sample_rate.label('sample_rate'),
        AlNgDitingRelation.case_id.label('case_id'),
        AlNgDitingRelation.role_id.label('role_id'),
        AlNgDitingRelation.court_id.label('court_id')) \
        .filter(Utterance.request_id == UtteranceAccess.request_id,
                Utterance.request_id == AlNgDiting.request_id,
                AlNgDiting.uuid == AlNgDitingRelation.uuid,
                ) \
        .join(sub_q, sub_q.c.request_id == Utterance.request_id, isouter=is_outer_join) \
        .filter(Utterance.is_deleted == 0, UtteranceAccess.is_deleted == 0)

    if task_ids is not None:
        if len(task_ids) == 0:
            page_view_item = {'page': cur_page, 'limit': per_page, 'total': 0}
            return PageResultSuccess(msg=u'语句管理列表', data=[], page=page_view_item)
        q = q.filter(sub_q.c.task_id.in_(task_ids))

    if form.label_time_left.data:
        q = q.filter(UtteranceAccess.time >= datetime.fromtimestamp(form.label_time_left.data))
    if form.label_time_right.data:
        q = q.filter(UtteranceAccess.time <= datetime.fromtimestamp(form.label_time_right.data))
    if form.court_id.data and form.court_id.data != '':
        q = q.filter(AlNgDitingRelation.court_id.like('%' + form.court_id.data + "%"))
    if form.case_id.data and form.case_id.data != '':
        q = q.filter(AlNgDitingRelation.case_id.like('%' + form.case_id.data + "%"))
    if form.role_id.data and form.role_id.data != '':
        q = q.filter(AlNgDitingRelation.role_id.like('%' + form.role_id.data + "%"))

    if column_order == 'ascending':
        if column_name == 'request_id':
            q = q.order_by(Utterance.request_id.asc())
        if column_name == 'court_id':
            q = q.order_by(AlNgDitingRelation.court_id.asc())
        if column_name == 'case_id':
            q = q.order_by(AlNgDitingRelation.case_id.asc())
        if column_name == 'role_id':
            q = q.order_by(AlNgDitingRelation.role_id.asc())
        if column_name == 'time':
            q = q.order_by(UtteranceAccess.time.asc())
        if column_name == 'result':
            q = q.order_by(UtteranceAccess.result.asc())
        if column_name == 'tag_status':
            q = q.order_by(sub_q.c.tag_status.asc())
        if column_name == 'label_text':
            q = q.order_by(sub_q.c.label_text.asc())
        if column_name == 'real_rtf':
            q = q.order_by(UtteranceAccess.real_rtf.asc())
        if column_name == 'cut_ratio':
            q = q.order_by(Utterance.cut_ratio.asc())
        if column_name == 'volume':
            q = q.order_by(Utterance.volume.asc())
        if column_name == 'pre_snr':
            q = q.order_by(Utterance.pre_snr.asc())
        if column_name == 'latter_snr':
            q = q.order_by(Utterance.latter_snr.asc())
        if column_name == 'detect_duration':
            q = q.order_by(UtteranceAccess.detect_duration.asc())
        if column_name == 'wer':
            q = q.order_by(sub_q.c.wer.asc())
        if column_name == 'insertion_count':
            q = q.order_by(sub_q.c.insertion_count.asc())
        if column_name == 'delete_count':
            q = q.order_by(sub_q.c.delete_count.asc())
        if column_name == 'sub_count':
            q = q.order_by(sub_q.c.sub_count.asc())
        if column_name == 'total_rtf':
            q = q.order_by(UtteranceAccess.total_rtf.asc())
        if column_name == 'latency':
            q = q.order_by(UtteranceAccess.latency.asc())
        if column_name == 'total_cost_time':
            q = q.order_by(UtteranceAccess.total_cost_time.asc())
        if column_name == 'process_time':
            q = q.order_by(UtteranceAccess.process_time.asc())
        if column_name == 'receive_cost_time':
            q = q.order_by(UtteranceAccess.receive_cost_time.asc())
        if column_name == 'wait_cost_time':
            q = q.order_by(UtteranceAccess.wait_cost_time.asc())
        if column_name == 'raw_rtf':
            q = q.order_by(UtteranceAccess.raw_rtf.asc())
        if column_name == 'avg_packet_duration':
            q = q.order_by(UtteranceAccess.avg_packet_duration.asc())
        if column_name == 'packet_count':
            q = q.order_by(UtteranceAccess.packet_count.asc())
        if column_name == 'audio_format':
            q = q.order_by(UtteranceAccess.audio_format.asc())
        if column_name == 'sample_rate':
            q = q.order_by(UtteranceAccess.sample_rate.asc())
    elif column_order == 'descending':
        if column_name == 'request_id':
            q = q.order_by(Utterance.request_id.desc())
        if column_name == 'court_id':
            q = q.order_by(AlNgDitingRelation.court_id.desc())
        if column_name == 'case_id':
            q = q.order_by(AlNgDitingRelation.case_id.desc())
        if column_name == 'role_id':
            q = q.order_by(AlNgDitingRelation.role_id.desc())
        if column_name == 'time':
            q = q.order_by(UtteranceAccess.time.desc())
        if column_name == 'result':
            q = q.order_by(UtteranceAccess.result.desc())
        if column_name == 'tag_status':
            q = q.order_by(sub_q.c.tag_status.desc())
        if column_name == 'label_text':
            q = q.order_by(sub_q.c.label_text.desc())
        if column_name == 'real_rtf':
            q = q.order_by(UtteranceAccess.real_rtf.desc())
        if column_name == 'cut_ratio':
            q = q.order_by(Utterance.cut_ratio.desc())
        if column_name == 'volume':
            q = q.order_by(Utterance.volume.desc())
        if column_name == 'pre_snr':
            q = q.order_by(Utterance.pre_snr.desc())
        if column_name == 'latter_snr':
            q = q.order_by(Utterance.latter_snr.desc())
        if column_name == 'detect_duration':
            q = q.order_by(UtteranceAccess.detect_duration.desc())
        if column_name == 'wer':
            q = q.order_by(sub_q.c.wer.desc())
        if column_name == 'insertion_count':
            q = q.order_by(sub_q.c.insertion_count.desc())
        if column_name == 'delete_count':
            q = q.order_by(sub_q.c.delete_count.desc())
        if column_name == 'sub_count':
            q = q.order_by(sub_q.c.sub_count.desc())
        if column_name == 'total_rtf':
            q = q.order_by(UtteranceAccess.total_rtf.desc())
        if column_name == 'latency':
            q = q.order_by(UtteranceAccess.latency.desc())
        if column_name == 'total_cost_time':
            q = q.order_by(UtteranceAccess.total_cost_time.desc())
        if column_name == 'process_time':
            q = q.order_by(UtteranceAccess.process_time.desc())
        if column_name == 'receive_cost_time':
            q = q.order_by(UtteranceAccess.receive_cost_time.desc())
        if column_name == 'wait_cost_time':
            q = q.order_by(UtteranceAccess.wait_cost_time.desc())
        if column_name == 'raw_rtf':
            q = q.order_by(UtteranceAccess.raw_rtf.desc())
        if column_name == 'avg_packet_duration':
            q = q.order_by(UtteranceAccess.avg_packet_duration.desc())
        if column_name == 'packet_count':
            q = q.order_by(UtteranceAccess.packet_count.desc())
        if column_name == 'audio_format':
            q = q.order_by(UtteranceAccess.audio_format.desc())
        if column_name == 'sample_rate':
            q = q.order_by(UtteranceAccess.sample_rate.desc())
    rvs = pager(q, page=cur_page, per_page=per_page)

    task_info = TagTask.query.filter_by().all()
    task_info = {tag_task.id: tag_task for tag_task in task_info}

    vms = []
    for rv in rvs.items:
        vmc = {c: getattr(rv, c, None) for c in rv._fields}
        vmc['time'] = datetime2timestamp(vmc['time'])
        if vmc['tag_result_id'] and vmc['tag_result_is_deleted'] == 0:
            vmc['label_text'] = vmc['label_text']
            vmc['tag_status'] = vmc['tag_status']
            if task_info.get(vmc['task_id']):
                vmc['task_code'] = task_info[vmc['task_id']].task_code
            else:
                vmc['task_code'] = ''
        else:
            vmc['label_text'] = ''
            vmc['tag_status'] = 0
            vmc['task_code'] = ''
        vms.append(vmc)
    return PageResultSuccess(msg=u'语句管理列表', data=vms, page=rvs.page_view())


@api.route('/calc-wer', methods=['POST'])
@auth.login_required
def omutterance_calc_wer():
    """
	计算被选语句中已标注语句的错误率. 若选中的语句均未标注,返回语句未标注的提示/异常.
	"""
    form = OmCalcwerForm().validate_for_api()
    is_calc_all = form.is_calc_all.data
    req_id_list = form.req_id_list.data
    if is_calc_all == 1:
        stat_tmp_1 = db_v1.session.query(
            Utterance.request_id.label('request_id')
        ).filter(
            TagResult.task_id == TagTask.id,
            TagResult.request_id == Utterance.request_id,
            TagResult.request_id == UtteranceAccess.request_id,
            Utterance.request_id == AlNgDiting.request_id,
            AlNgDiting.uuid == AlNgDitingRelation.uuid,
        ).filter(Utterance.is_deleted == 0, UtteranceAccess.is_deleted == 0, TagResult.is_deleted == 0)
        if form.label_time_left.data:
            stat_tmp_1 = stat_tmp_1.filter(UtteranceAccess.time >= datetime.fromtimestamp(form.label_time_left.data))
        if form.label_time_right.data:
            stat_tmp_1 = stat_tmp_1.filter(UtteranceAccess.time <= datetime.fromtimestamp(form.label_time_right.data))
        if form.task_code.data and form.task_code.data != '':
            stat_tmp_1 = stat_tmp_1.filter(TagTask.task_code.like('%' + form.task_code.data + "%"))
        if form.court_id.data and form.court_id.data != '':
            stat_tmp_1 = stat_tmp_1.filter(AlNgDitingRelation.court_id.like('%' + form.court_id.data + "%"))
        if form.case_id.data and form.case_id.data != '':
            stat_tmp_1 = stat_tmp_1.filter(AlNgDitingRelation.case_id.like('%' + form.case_id.data + "%"))
        if form.role_id.data and form.role_id.data != '':
            stat_tmp_1 = stat_tmp_1.filter(AlNgDitingRelation.role_id.like('%' + form.role_id.data + "%"))

        req_id_list_all = []
        for i in stat_tmp_1:
            for j in i:
                req_id_list_all.append(j)

    if not (is_calc_all == 1):
        if not req_id_list and len(req_id_list) < 1:
            raise ParameterException(msg=u'未选中任何语句')

    if is_calc_all == 1:
        if not req_id_list_all and len(req_id_list_all) < 1:
            raise ParameterException(msg=u'没有查询到符合条件的语句')

    q = db_v1.session.query(
        TagResult.insertion_count, TagResult.sub_count, TagResult.delete_count, TagResult.label_text
    ).filter(TagResult.tag_status != 0)

    if is_calc_all == 0:
        q = q.filter(TagResult.request_id.in_(req_id_list))
    elif is_calc_all == 1:
        q = q.filter(TagResult.request_id.in_(req_id_list_all))
    query_results = q.all()

    if not query_results:
        raise ParameterException(msg=u'选中的语句均未标注')

    # calc wer
    i, s, d, c = [0] * 4
    for item in query_results:
        i += item[0] or 0
        s += item[1] or 0
        d += item[2] or 0
        c += len(item[-1] or '')
    wer = 100
    if c != 0:
        wer = float(i + s + d) / c * 100
    return ResultSuccess(msg=u'错误率计算成功', data={'wer': round(wer, 2)})


@api.route('/download-data', methods=['POST'])
@auth.login_required
def omutterance_download_data():
    form = OmDataSearchForm().validate_for_api()

    task_code = form.task_code.data
    court_id = form.court_id.data
    case_id = form.case_id.data
    role_id = form.role_id.data
    label_time_left = form.label_time_left.data
    label_time_right = form.label_time_right.data
    form2 = OmDownloadForm().validate_for_api()
    download_time = form2.download_time.data / 1000
    download_task = OmAsyncDownloadTask()
    with db_v1.auto_commit():
        form.populate_obj(download_task)
        download_task.start_time = download_time
        download_task.create_uid = g.user.uid
        download_task.download_status = 0
        db_v1.session.add(download_task)
    id = download_task.id
    query_list = dict(id=id,
                      task_code=task_code,
                      court_id=court_id,
                      case_id=case_id,
                      role_id=role_id,
                      label_time_right=label_time_right,
                      label_time_left=label_time_left,
                      )
    asynchronous_executor.submit(download_utterance_data, query_list).add_done_callback(done_download_data)

    return DownloadSuccess(msg=u'数据下载成功', data='成功')


def download_utterance_data(query_list):
    id = query_list.get('id')
    download_result = OmAsyncDownloadTask.query.filter_by(id=id).first_or_404()
    with db_v1.auto_commit():
        if download_result:
            download_result.parser_status = 1
            db_v1.session.add(download_result)
    task_code = query_list.get('task_code')
    court_id = query_list.get('court_id')
    case_id = query_list.get('case_id')
    role_id = query_list.get('role_id')
    label_time_right = query_list.get('label_time_right')
    label_time_left = query_list.get('label_time_left')

    is_outer_join = True
    task_ids = None
    # 这里是查出tagresult里面的taskids是什么
    if task_code and task_code != '':
        is_outer_join = False
        task_rvs = db_v1.session.query(TagTask.id).filter(
            TagTask.task_code.like('%' + task_code + "%")).filter_by().all()
        task_ids = [task_id for task_id, in task_rvs]
    sub_q = db_v1.session.query(TagResult.id.label('tag_result_id'),
                                TagResult.request_id.label('request_id'),
                                TagResult.is_deleted.label('tag_result_is_deleted'),
                                TagResult.tag_status.label('tag_status'),
                                TagResult.task_id.label('task_id'),
                                TagResult.proj_id.label('proj_id'),
                                TagResult.wer.label('wer'),
                                TagResult.sub_count.label('sub_count'),
                                TagResult.delete_count.label('delete_count'),
                                TagResult.insertion_count.label('insertion_count'),
                                TagResult.label_text.label('label_text'), ) \
        .filter(TagResult.is_deleted == 0).subquery('sub_q')
    q = db_v1.session.query(
        UtteranceAccess.time.label('time'),
        Utterance.request_id.label('request_id'),
        UtteranceAccess.result.label('result'),
        sub_q.c.tag_result_id.label('tag_result_id'),
        sub_q.c.request_id.label('request_id'),
        sub_q.c.tag_result_is_deleted.label('tag_result_is_deleted'),
        sub_q.c.tag_status.label('tag_status'),
        sub_q.c.task_id.label('task_id'),
        sub_q.c.proj_id.label('proj_id'),
        sub_q.c.wer.label('wer'),
        sub_q.c.insertion_count.label('insertion_count'),
        sub_q.c.delete_count.label('delete_count'),
        sub_q.c.sub_count.label('sub_count'),
        sub_q.c.label_text.label('label_text'),
        UtteranceAccess.real_rtf.label('real_rtf'),
        Utterance.cut_ratio.label('cut_ratio'),
        Utterance.volume.label('volume'),
        Utterance.pre_snr.label('pre_snr'),
        Utterance.latter_snr.label('latter_snr'),
        Utterance.path.label('path'),
        UtteranceAccess.detect_duration.label('detect_duration'),
        UtteranceAccess.total_rtf.label('total_rtf'),
        UtteranceAccess.latency.label('latency'),
        UtteranceAccess.total_cost_time.label('total_cost_time'),
        UtteranceAccess.process_time.label('process_time'),
        UtteranceAccess.receive_cost_time.label('receive_cost_time'),
        UtteranceAccess.wait_cost_time.label('wait_cost_time'),
        UtteranceAccess.raw_rtf.label('raw_rtf'),
        UtteranceAccess.avg_packet_duration.label('avg_packet_duration'),
        UtteranceAccess.packet_count.label('packet_count'),
        UtteranceAccess.audio_format.label('audio_format'),
        UtteranceAccess.sample_rate.label('sample_rate'),
        AlNgDitingRelation.case_id.label('case_id'),
        AlNgDitingRelation.role_id.label('role_id'),
        AlNgDitingRelation.court_id.label('court_id')
    ) \
        .filter(Utterance.request_id == UtteranceAccess.request_id,
                Utterance.request_id == AlNgDiting.request_id,
                AlNgDiting.uuid == AlNgDitingRelation.uuid, ) \
        .join(sub_q, sub_q.c.request_id == Utterance.request_id, isouter=is_outer_join) \
        .filter(Utterance.is_deleted == 0, UtteranceAccess.is_deleted == 0)

    if task_ids is not None:
        q = q.filter(sub_q.c.task_id.in_(task_ids))

    if label_time_left:
        q = q.filter(UtteranceAccess.time >= datetime.fromtimestamp(label_time_left))
    if label_time_right:
        q = q.filter(UtteranceAccess.time <= datetime.fromtimestamp(label_time_right))
    if court_id and court_id != '':
        q = q.filter(AlNgDitingRelation.court_id.like('%' + court_id + "%"))
    if case_id and case_id != '':
        q = q.filter(AlNgDitingRelation.case_id.like('%' + case_id + "%"))
    if role_id and role_id != '':
        q = q.filter(AlNgDitingRelation.role_id.like('%' + role_id + "%"))
    rvs = q.all()

    task_info = TagTask.query.filter_by().all()
    task_info = {tag_task.id: tag_task for tag_task in task_info}

    vms = []
    for rv in rvs:
        vm = {c: getattr(rv, c, None) for c in rv._fields}
        vm['time'] = datetime2timestamp(vm['time'])
        vm['time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(vm['time']))
        if vm['tag_result_id'] and vm['tag_result_is_deleted'] == 0:
            vm['label_text'] = vm['label_text']
            vm['tag_status'] = vm['tag_status']
            if task_info.get(vm['task_id']):
                vm['task_code'] = task_info[vm['task_id']].task_code
            else:
                vm['task_code'] = ''
        else:
            vm['task_code'] = ''
        vms.append(vm)
    # logger.info('下载数据信息为 %s' ,vms)

    info_list = vms
    try:
        if info_list is None or len(info_list) == 0:
            finish_time = int(time.time())
            return dict(id=id, result_msg='没有需要下载的语句信息', finish_time=finish_time)
        download_root = os.path.join(os.path.dirname(current_app.instance_path), 'download')
        str_time = time.strftime('%Y%m%d%H%M%S')
        download_dir = os.path.join(download_root, str_time)
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        # 拷贝音频文件
        data_dir = os.path.join(download_dir, 'data')
        os.mkdir(data_dir)

        for info in info_list:
            src_audio_path = info.get('path', None)
            if src_audio_path is None or src_audio_path == "":
                logger.info('音频路径为空，无法拷贝')
            file_name = os.path.split(src_audio_path)[1]
            dst_audio_path = os.path.join(data_dir, file_name)
            try:
                shutil.copyfile(src_audio_path, dst_audio_path)
                logger.info('复制音频文件%s成功', src_audio_path)
            except Exception as exp:
                logger.error(exp)

        # 生成csv文件
        csv_headers = info_list[0].keys()
        csv_file = os.path.join(download_dir, 'utterance_info.csv')
        save_to_csv(info_list, csv_headers, csv_file)

        zip_file = os.path.join(download_root, 'download_{0}.zip'.format(time.strftime('%Y%m%d%H%M%S')))
        zip_dir(download_dir, zip_file)
        finish_time = int(time.time())
        return dict(id=id, result_msg='下载成功', download_path=zip_file, finish_time=finish_time, download_status=2)
    except Exception as exp:
        finish_time = int(time.time())
        return dict(id=id, result_msg=exp.message, download_status=3, finish_time=finish_time)


def done_download_data(future):
    result = future.result()
    id = result.get("id")
    result_msg = result.get("result_msg")
    finish_time = result.get("finish_time")
    download_status = result.get("download_status")
    download_path = result.get("download_path")

    download_result = OmAsyncDownloadTask.query.filter_by(id=id).first_or_404()
    with db_v1.auto_commit():
        if download_result:
            download_result.result_msg = result_msg
            download_result.finish_time = finish_time
            download_result.download_status = download_status
            download_result.download_path = download_path
            db_v1.session.add(download_result)


@api.route('/search-task', methods=['POST'])
@auth.login_required
def omutterance_search_task():
    form = OmDataSearchForm().validate_for_api()

    is_outer_join = True

    # if查询条件有task_code,则查询出相应的id编号
    if form.task_code.data and form.task_code.data != '':
        raise ParameterException(msg=u'新建任务时，请不要输入任务编号')

    sub_q = db_v1.session.query(Utterance.request_id.label('request_id'),
                                TagResult.request_id.label('tag_result_request_id'),
                                TagResult.task_id.label('tag_result_task_id'),
                                UtteranceAccess.time.label('time'),
                                AlNgDitingRelation.role_id.label('role_id'),
                                AlNgDitingRelation.case_id.label('case_id'),
                                AlNgDitingRelation.court_id.label('court_id'), ) \
        .filter(Utterance.request_id == UtteranceAccess.request_id,
                Utterance.request_id == AlNgDiting.request_id,
                AlNgDiting.uuid == AlNgDitingRelation.uuid,
                ) \
        .join(TagResult, TagResult.request_id == Utterance.request_id, isouter=is_outer_join) \
        .filter(Utterance.is_deleted == 0, UtteranceAccess.is_deleted == 0).subquery('sub_q')
    q = db_v1.session.query(sub_q.c.request_id.label('request_id'),
                            sub_q.c.time.label('time'),
                            sub_q.c.role_id.label('role_id'),
                            sub_q.c.case_id.label('case_id'),
                            sub_q.c.court_id.label('court_id')
                            ).filter(or_(sub_q.c.tag_result_request_id.is_(None), sub_q.c.tag_result_task_id == -1))

    if form.label_time_left.data:
        q = q.filter(sub_q.c.time >= datetime.fromtimestamp(form.label_time_left.data))
    if form.label_time_right.data:
        q = q.filter(sub_q.c.time <= datetime.fromtimestamp(form.label_time_right.data))
    if form.court_id.data and form.court_id.data != '':
        q = q.filter(sub_q.c.court_id.like('%' + form.court_id.data + "%"))
    if form.case_id.data and form.case_id.data != '':
        q = q.filter(sub_q.c.case_id.like('%' + form.case_id.data + "%"))
    if form.role_id.data and form.role_id.data != '':
        q = q.filter(sub_q.c.role_id.like('%' + form.role_id.data + "%"))

    rvs = q.all()
    req_id_list_all = []
    for rv in rvs:
        rv_dict = {c: getattr(rv, c, None) for c in rv._fields}
        vm = {}
        vm['request_id'] = rv_dict['request_id']
        req_id_list_all.append(vm['request_id'])
    return ResultSuccess(msg=u'查询成功', data={'req_id_list_all': req_id_list_all})


@api.route('/add-task', methods=['POST'])
@auth.login_required
def omutterance_add_task():
    form = OmTagTaskForm().validate_for_api()
    req_id_list_all = form.req_id_list_all.data

    # 生成任务编号
    task_code_prefix = 'OTK'
    task_cnt_by_code = TagTask.query.filter(TagTask.task_code.like(task_code_prefix + '%')).filter_by(
        with_deleted=True).count()
    task_code = task_code_prefix + str(task_cnt_by_code + 1).zfill(7)
    tag_task = TagTask()
    with db_v1.auto_commit():
        form.populate_obj(tag_task)
        tag_task.task_code = task_code
        tag_task.create_uid = g.user.uid
        tag_task.tagger_uid = g.user.uid
        tag_task.tagging_status = 0
        tag_task.audit_status = 0
        tag_task.task_status = 1
        tag_task.proj_id = 0
        db_v1.session.add(tag_task)

    query_result = db_v1.session.query(TagTask.id).filter(TagTask.task_code == task_code).first()
    task_id = query_result.id
    if not task_id:
        raise ParameterException(msg=u'没有该任务编号')

    tag_result_list = []
    for req_id in req_id_list_all:
        tag_result = TagResult()
        form.populate_obj(tag_result)
        tag_result.is_deleted = 0
        tag_result.request_id = req_id
        tag_result.proj_id = 0
        tag_result.task_id = task_id
        tag_result.tag_status = 0
        tag_result_list.append(tag_result)
    with db_v1.auto_commit():
        db_v1.session.bulk_save_objects(tag_result_list)
    return CreateSuccess(msg=u'任务新增成功', data='成功')


@api.route('/parser-history', methods=['POST'])
@auth.login_required
def omutterance_parser_history():
    page_form = PageForm().validate_for_api()
    cur_page = page_form.page.data if page_form.page.data else 1
    per_page = page_form.limit.data if page_form.limit.data else current_app.config['DEFAULT_LISTNUM_PER_PAGE']

    form = OmParserForm().validate_for_api()

    q = db_v1.session.query(
        OmAsyncParserTask.start_time.label('start_time'),
        OmAsyncParserTask.finish_time.label('finish_time'),
        OmAsyncParserTask.create_uid.label('create_uid'),
        OmAsyncParserTask.parser_status.label('parser_status'),
        OmAsyncParserTask.result_msg.label('result_msg'),
    ).filter(OmAsyncParserTask.is_deleted == 0)

    if form.label_time_left.data:
        q = q.filter(OmAsyncParserTask.start_time >= form.label_time_left.data)
    if form.label_time_right.data:
        q = q.filter(OmAsyncParserTask.start_time <= form.label_time_right.data)
    if form.parser_status.data != '':
        q = q.filter(OmAsyncParserTask.parser_status == form.parser_status.data)
    q = q.order_by(OmAsyncParserTask.start_time.desc())
    rvs = pager(q, page=cur_page, per_page=per_page)
    user_info = User.query.filter_by().all()
    user_info = {user.id: user for user in user_info}

    vms = []
    for rv in rvs.items:
        vm = {c: getattr(rv, c, None) for c in rv._fields}
        vm['create_uid'] = user_info[vm['create_uid']].nickname
        vms.append(vm)
    return PageResultSuccess(msg=u'解析历史页面', data=vms, page=rvs.page_view())


@api.route('/download-history', methods=['POST'])
@auth.login_required
def omutterance_download_history():
    page_form = PageForm().validate_for_api()
    cur_page = page_form.page.data if page_form.page.data else 1
    per_page = page_form.limit.data if page_form.limit.data else current_app.config['DEFAULT_LISTNUM_PER_PAGE']

    form = OmDownloadForm().validate_for_api()

    q = db_v1.session.query(
        OmAsyncDownloadTask.start_time.label('start_time'),
        OmAsyncDownloadTask.finish_time.label('finish_time'),
        OmAsyncDownloadTask.create_uid.label('create_uid'),
        OmAsyncDownloadTask.download_status.label('download_status'),
        OmAsyncDownloadTask.result_msg.label('result_msg'),
        OmAsyncDownloadTask.download_path.label('download_path'),
    ).filter(OmAsyncDownloadTask.is_deleted == 0)

    if form.label_time_left.data:
        q = q.filter(OmAsyncDownloadTask.start_time >= form.label_time_left.data)
    if form.label_time_right.data:
        q = q.filter(OmAsyncDownloadTask.start_time <= form.label_time_right.data)
    if form.download_status.data != '':
        q = q.filter(OmAsyncDownloadTask.download_status == form.download_status.data)
    q = q.order_by(OmAsyncDownloadTask.start_time.desc())
    rvs = pager(q, page=cur_page, per_page=per_page)
    user_info = User.query.filter_by().all()
    user_info = {user.id: user for user in user_info}

    vms = []
    for rv in rvs.items:
        vm = {c: getattr(rv, c, None) for c in rv._fields}
        vm['create_uid'] = user_info[vm['create_uid']].nickname
        vms.append(vm)
    return PageResultSuccess(msg=u'下载历史页面', data=vms, page=rvs.page_view())
