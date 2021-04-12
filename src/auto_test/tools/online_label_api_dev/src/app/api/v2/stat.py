# -*- coding: utf-8 -*-
import logging

import os
from datetime import datetime
from flask import current_app
from sqlalchemy import text, func, distinct

from app.libs.enums import LabelUserMapRelTypeEnum
from app.libs.error import APIException
from app.libs.error_code import ResultSuccess, PageResultSuccess
from app.libs.qpaginate import pager
from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.models.base import db_v2, DB_V2_TABLE_PREFIX
from app.models.v2.web.label import LabelTask, LabelResult, LabelProject, LabelUtteranceInfo, LabelUserMap
from app.models.v2.web.sysmgr import User
from app.validators.base import PageForm
from app.validators.forms_v2 import StatisticSearchForm, LabelStatSearchForm

api = Redprint('stat')
logger = logging.getLogger(__name__)


@api.route('/list-workload', methods=['POST'])
@auth.login_required
def stat_list_workload():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    # TODO：后续根据某个字段来扩充聚合时间的类型
    group_time_format = '%Y-%m-%d'

    form = LabelStatSearchForm().validate_for_api()

    # 已被标注的
    stat_tmp_label_status_1 = db_v2.session.query(User.id.label('label_uid'),
                                                  LabelUtteranceInfo.detect_duration.label('detect_duration'),
                                                  LabelResult.proj_id.label('proj_id'),
                                                  LabelResult.task_id.label('task_id'),
                                                  func.from_unixtime(LabelResult.label_time, group_time_format).label(
                                                      'time_classication')).filter(
        LabelResult.is_deleted == 0,
        LabelResult.request_id == LabelUtteranceInfo.request_id,
        LabelResult.proj_id != -1,
        LabelResult.label_uid == User.id,
        LabelResult.label_status == 1
    )
    # 未被标注的
    stat_tmp_label_status_0 = db_v2.session.query(User.id.label('label_uid'),
                                                  LabelUtteranceInfo.detect_duration.label('detect_duration'),
                                                  LabelResult.proj_id.label('proj_id'),
                                                  LabelResult.task_id.label('task_id'),
                                                  func.from_unixtime(LabelResult.label_time, group_time_format).label(
                                                      'time_classication')).filter(
        LabelResult.is_deleted == 0,
        LabelResult.request_id == LabelUtteranceInfo.request_id,
        LabelResult.proj_id != -1,
        LabelResult.task_id == LabelUserMap.rel_id,
        LabelUserMap.rel_type == LabelUserMapRelTypeEnum.TASK.value,
        LabelUserMap.uid == User.id,
        LabelUserMap.is_deleted == 0,
        LabelResult.label_status == 0
    )

    if form.label_time_left.data:
        stat_tmp_label_status_1 = stat_tmp_label_status_1.filter(LabelResult.label_time >= form.label_time_left.data)
        stat_tmp_label_status_0 = stat_tmp_label_status_0.filter(LabelResult.label_time >= form.label_time_left.data)
    if form.label_time_right.data:
        stat_tmp_label_status_1 = stat_tmp_label_status_1.filter(LabelResult.label_time <= form.label_time_right.data)
        stat_tmp_label_status_0 = stat_tmp_label_status_0.filter(LabelResult.label_time <= form.label_time_right.data)
    if form.proj_code.data and form.proj_code.data != '':
        stat_tmp_label_status_1 = stat_tmp_label_status_1.filter(
            LabelResult.proj_code.like('%' + form.proj_code.data + "%"))
        stat_tmp_label_status_0 = stat_tmp_label_status_0.filter(
            LabelResult.proj_code.like('%' + form.proj_code.data + "%"))
    if form.proj_name.data and form.proj_name.data != '':
        stat_tmp_label_status_1 = stat_tmp_label_status_1.filter(
            LabelResult.proj_name.like('%' + form.proj_name.data + "%"))
        stat_tmp_label_status_0 = stat_tmp_label_status_0.filter(
            LabelResult.proj_name.like('%' + form.proj_name.data + "%"))
    if form.tagger_account.data and form.tagger_account.data != '':
        stat_tmp_label_status_1 = stat_tmp_label_status_1.filter(
            User.account.like('%' + form.tagger_account.data + "%"))
        stat_tmp_label_status_0 = stat_tmp_label_status_0.filter(
            User.account.like('%' + form.tagger_account.data + "%"))
    # if form.task_status.data is not None and form.task_status.data != '':
    #     stat_sql = stat_sql.filter(LabelTask.task_status == form.task_status.data)

    stat_tmp = stat_tmp_label_status_1.union(stat_tmp_label_status_0).subquery('stat_tmp')
    if form.label_status.data is not None and form.label_status.data != '':
        if form.label_status.data == 0:
            stat_tmp = stat_tmp_label_status_0.subquery('stat_tmp')
        if form.label_status.data == 1:
            stat_tmp = stat_tmp_label_status_1.subquery('stat_tmp')

    group_tmp = db_v2.session.query(stat_tmp.c.label_uid,
                                    stat_tmp.c.proj_id,
                                    func.min(stat_tmp.c.time_classication).label('stat_date_start'),
                                    func.max(stat_tmp.c.time_classication).label('stat_date_end'),
                                    func.count(distinct(stat_tmp.c.task_id)).label('sum_task'),
                                    func.count().label('sum_uttr'),
                                    func.sum(stat_tmp.c.detect_duration).label('sum_duration')).group_by(
        stat_tmp.c.label_uid, stat_tmp.c.proj_id).subquery('group_tmp')

    q = db_v2.session.query(group_tmp)

    rvs = pager(q, page=cur_page, per_page=per_page)

    user_info = User.query.filter_by().all()
    user_info = {user.id: user for user in user_info}

    project_info = LabelProject.query.filter_by().all()
    project_info = {label_proj.id: label_proj for label_proj in project_info}

    vms = []
    for rv in rvs.items:
        vm = {c: getattr(rv, c, None) for c in rv._fields}
        vm['label_user_name'] = user_info[vm['label_uid']].nickname
        vm['label_user_account'] = user_info[vm['label_uid']].account
        vm['proj_name'] = project_info[vm['proj_id']].proj_name
        vm['proj_code'] = project_info[vm['proj_id']].proj_code
        vm['proj_difficulty'] = project_info[vm['proj_id']].proj_difficulty
        vms.append(vm)

    return PageResultSuccess(msg=u'标注量统计列表', data=vms, page=rvs.page_view())


@api.route('/calc-workload', methods=['POST'])
@auth.login_required
def stat_calc_workload():
    form = LabelStatSearchForm().validate_for_api()
    stat_tmp_1 = db_v2.session.query(LabelUtteranceInfo.detect_duration.label('detect_duration')).filter(
        LabelResult.task_id == LabelTask.id, LabelResult.request_id == LabelUtteranceInfo.request_id,
        LabelResult.proj_id == LabelProject.id, LabelResult.label_uid == User.id).filter(LabelResult.is_deleted == 0)

    if form.label_time_left.data:
        stat_tmp_1 = stat_tmp_1.filter(LabelResult.label_time >= form.label_time_left.data)
    if form.label_time_right.data:
        stat_tmp_1 = stat_tmp_1.filter(LabelResult.label_time <= form.label_time_right.data)
    if form.proj_code.data and form.proj_code.data != '':
        stat_tmp_1 = stat_tmp_1.filter(LabelProject.proj_code.like('%' + form.proj_code.data + "%"))
    if form.proj_name.data and form.proj_name.data != '':
        stat_tmp_1 = stat_tmp_1.filter(LabelProject.proj_name.like('%' + form.proj_name.data + "%"))
    if form.tagger_account.data and form.tagger_account.data != '':
        stat_tmp_1 = stat_tmp_1.filter(User.account.like('%' + form.tagger_account.data + "%"))
    if form.task_status.data is not None and form.task_status.data != '':
        stat_tmp_1 = stat_tmp_1.filter(LabelTask.task_status == form.task_status.data)
    if form.label_status.data is not None and form.label_status.data != '':
        stat_tmp_1 = stat_tmp_1.filter(LabelResult.label_status == form.label_status.data)

    stat_tmp = stat_tmp_1.subquery('stat_tmp')

    total_duration = db_v2.session.query(func.sum(stat_tmp.c.detect_duration).label('sum_duration')).first()
    return ResultSuccess(msg=u'计算总标注量', data={'total_duration': total_duration})


@api.route('/time-spend', methods=['POST'])
@auth.login_required
def stat_time_spend():
    form = StatisticSearchForm().validate_for_api()

    sql_cond = " "
    sql_cond_dict = {}
    if form.label_time_left.data:
        sql_cond += " AND {table_prefix}utterace_access.time >= :label_time_left ".format(
            table_prefix=DB_V2_TABLE_PREFIX)
        sql_cond_dict['label_time_left'] = datetime.fromtimestamp(form.label_time_left.data)
    if form.label_time_right.data:
        sql_cond += " AND {table_prefix}utterace_access.time <= :label_time_right ".format(
            table_prefix=DB_V2_TABLE_PREFIX)
        sql_cond_dict['label_time_right'] = datetime.fromtimestamp(form.label_time_right.data)
    if form.court_id.data and form.court_id.data != '':
        sql_cond += " AND {table_prefix}ng_diting_relation.court_id LIKE :court_id ".format(
            table_prefix=DB_V2_TABLE_PREFIX)
        sql_cond_dict['court_id'] = '%' + form.court_id.data + '%'
    if form.case_id.data and form.case_id.data != '':
        sql_cond += " AND {table_prefix}ng_diting_relation.case_id LIKE :case_id ".format(
            table_prefix=DB_V2_TABLE_PREFIX)
        sql_cond_dict['case_id'] = '%' + form.case_id.data + '%'
    if form.role_id.data and form.role_id.data != '':
        sql_cond += " AND {table_prefix}ng_diting_relation.role_id LIKE :role_id ".format(
            table_prefix=DB_V2_TABLE_PREFIX)
        sql_cond_dict['role_id'] = '%' + form.role_id.data + '%'

    sql_temp_dir = os.path.dirname(__file__)
    sql_temp_filename = 'stat_time_spend_sql_temp.txt'
    with open(os.path.join(sql_temp_dir, sql_temp_filename), 'r') as f:
        stat_sql = str(f.read()).format(table_prefix=DB_V2_TABLE_PREFIX)

    if not stat_sql:
        raise APIException(u'内部sql模板丢失', 500, 5200)

    result_proxy = db_v2.session.execute(text(stat_sql.format(sql_cond=sql_cond)), sql_cond_dict,
                                         bind=db_v2.get_engine(current_app, '{}engine'.format(DB_V2_TABLE_PREFIX)))
    rows = result_proxy.fetchall()

    chart_item_dict = {
        'cnt_rtfgt5': '偏慢',
        'cnt_rtfgt9': '超时',
        'cnt_rtfgt12': '严重超时',
        'cnt_totrtf12': '出现延时',
        'cnt_wait100': '排队等识别',
        'cnt_totrtf5': '传输延时',
        'cnt_dugt29': 'vad切分过长',
    }

    chart_data = []

    for k in chart_item_dict.keys():
        item = {}
        item['识别时长'] = chart_item_dict[k]
        item['识别概况'] = float(rows[0][k] or 0) / float(rows[0]['cnt'] or 1) * 100
        chart_data.append(item)

    return ResultSuccess(msg=u'统计成功', data=chart_data)


@api.route('/abnormal-ratio', methods=['POST'])
@auth.login_required
def stat_abnormal_ratio():
    form = StatisticSearchForm().validate_for_api()
    sql_cond = " "
    sql_cond_dict = {}
    if form.label_time_left.data:
        sql_cond += " AND {table_prefix}utterace_access.time >= :label_time_left ".format(
            table_prefix=DB_V2_TABLE_PREFIX)
        sql_cond_dict['label_time_left'] = datetime.fromtimestamp(form.label_time_left.data)
    if form.label_time_right.data:
        sql_cond += " AND {table_prefix}utterace_access.time <= :label_time_right ".format(
            table_prefix=DB_V2_TABLE_PREFIX)
        sql_cond_dict['label_time_right'] = datetime.fromtimestamp(form.label_time_right.data)
    if form.court_id.data and form.court_id.data != '':
        sql_cond += " AND {table_prefix}ng_diting_relation.court_id LIKE :court_id ".format(
            table_prefix=DB_V2_TABLE_PREFIX)
        sql_cond_dict['court_id'] = '%' + form.court_id.data + '%'
    if form.case_id.data and form.case_id.data != '':
        sql_cond += " AND {table_prefix}ng_diting_relation.case_id LIKE :case_id ".format(
            table_prefix=DB_V2_TABLE_PREFIX)
        sql_cond_dict['case_id'] = '%' + form.case_id.data + '%'
    if form.role_id.data and form.role_id.data != '':
        sql_cond += " AND {table_prefix}ng_diting_relation.role_id LIKE :role_id ".format(
            table_prefix=DB_V2_TABLE_PREFIX)
        sql_cond_dict['role_id'] = '%' + form.role_id.data + '%'

    sql_temp_dir = os.path.dirname(__file__)
    sql_temp_filename = 'stat_abnormal_ratio_sql_temp.txt'
    with open(os.path.join(sql_temp_dir, sql_temp_filename), 'r') as f:
        stat_sql = str(f.read()).format(table_prefix=DB_V2_TABLE_PREFIX)

    if not stat_sql:
        raise APIException(u'内部sql模板丢失', 500, 5200)

    result_proxy = db_v2.session.execute(text(stat_sql.format(sql_cond=sql_cond)), sql_cond_dict,
                                         bind=db_v2.get_engine(current_app, '{}engine'.format(DB_V2_TABLE_PREFIX)))
    rows = result_proxy.fetchall()

    chart_item_dict = {
        'rtf': '实时率',
        'trr': '截幅比',
        'vol': '音量',
        'pre': '前信噪比',
        'post': '后信噪比',
    }

    chart_data = []

    for k in chart_item_dict.keys():
        item = {}
        item['音频质量'] = chart_item_dict[k]
        item['异常值个数占比'] = float(rows[0]['cnt_{}'.format(k)] or 0) * 100
        item['异常值时长占比'] = float(rows[0]['sum_du_{}'.format(k)] or 0) * 100
        chart_data.append(item)
    return ResultSuccess(msg=u'统计成功', data=chart_data)


@api.route('/transfer-delay', methods=['POST'])
@auth.login_required
def stat_transfer_delay():
    form = StatisticSearchForm().validate_for_api()
    sql_cond = " "
    sql_cond_dict = {}
    if form.label_time_left.data:
        sql_cond += " AND {table_prefix}utterace_access.time >= :label_time_left ".format(
            table_prefix=DB_V2_TABLE_PREFIX)
        sql_cond_dict['label_time_left'] = datetime.fromtimestamp(form.label_time_left.data)
    if form.label_time_right.data:
        sql_cond += " AND {table_prefix}utterace_access.time <= :label_time_right ".format(
            table_prefix=DB_V2_TABLE_PREFIX)
        sql_cond_dict['label_time_right'] = datetime.fromtimestamp(form.label_time_right.data)
    if form.court_id.data and form.court_id.data != '':
        sql_cond += " AND {table_prefix}ng_diting_relation.court_id LIKE :court_id ".format(
            table_prefix=DB_V2_TABLE_PREFIX)
        sql_cond_dict['court_id'] = '%' + form.court_id.data + '%'
    if form.case_id.data and form.case_id.data != '':
        sql_cond += " AND {table_prefix}ng_diting_relation.case_id LIKE :case_id ".format(
            table_prefix=DB_V2_TABLE_PREFIX)
        sql_cond_dict['case_id'] = '%' + form.case_id.data + '%'
    if form.role_id.data and form.role_id.data != '':
        sql_cond += " AND {table_prefix}ng_diting_relation.role_id LIKE :role_id ".format(
            table_prefix=DB_V2_TABLE_PREFIX)
        sql_cond_dict['role_id'] = '%' + form.role_id.data + '%'

    sql_temp_dir = os.path.dirname(__file__)
    sql_temp_filename = 'stat_transfer_delay_sql_temp.txt'
    with open(os.path.join(sql_temp_dir, sql_temp_filename), 'r') as f:
        stat_sql = str(f.read()).format(table_prefix=DB_V2_TABLE_PREFIX)

    if not stat_sql:
        raise APIException(u'内部sql模板丢失', 500, 5200)

    result_proxy = db_v2.session.execute(text(stat_sql.format(sql_cond=sql_cond)), sql_cond_dict,
                                         bind=db_v2.get_engine(current_app, '{}engine'.format(DB_V2_TABLE_PREFIX)))
    rows = result_proxy.fetchall()

    chart_data = []
    for row in rows:
        item = {}
        item['识别时间'] = row['stt_time'].strftime("%Y/%m/%d %H:%M:%S")
        item['diting到asr传输时延'] = row['http_cost_time']
        item['客户端到ditting传输时延'] = row['trans_delay']
        chart_data.append(item)
    return ResultSuccess(msg=u'统计成功', data=chart_data)
