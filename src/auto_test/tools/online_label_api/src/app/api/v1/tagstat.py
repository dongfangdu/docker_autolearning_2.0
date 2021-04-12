# -*- coding: utf-8 -*-
from sqlalchemy import func, distinct

from app.libs.builtin_extend import timeit
from app.libs.error_code import PageResultSuccess, ResultSuccess
from app.libs.qpaginate import pager
from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.models.base import db_v1
from app.models.v1.sysmng import User
from app.models.v1.tagfile import UtteranceAccess, UtteranceTrace
from app.models.v1.tagproj import TagTask, TagResult, TagProject
from app.validators.base import PageForm
from app.validators.forms_v1 import TagStatSearchForm

api = Redprint('tagstat')

@timeit
@api.route('/workload', methods=['POST'])
@auth.login_required
def tagstat_workload():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    # TODO：后续根据某个字段来扩充聚合时间的类型
    group_time_format = '%Y-%m-%d'

    form = TagStatSearchForm().validate_for_api()

    stat_tmp_1 = db_v1.session.query(TagTask.tagger_uid.label('tagger_uid'),
                                     UtteranceAccess.detect_duration.label('detect_duration'),
                                     TagResult.task_id.label('task_id'),
                                     func.from_unixtime(TagResult.label_time, group_time_format).label(
                                      'time_classication')).filter(
        TagResult.task_id == TagTask.id, TagResult.request_id == UtteranceAccess.request_id,
        TagResult.proj_id == TagProject.id, TagTask.tagger_uid == User.id).filter(TagResult.is_deleted == 0)

    if form.label_time_left.data:
        stat_tmp_1 = stat_tmp_1.filter(TagResult.label_time >= form.label_time_left.data)
    if form.label_time_right.data:
        stat_tmp_1 = stat_tmp_1.filter(TagResult.label_time <= form.label_time_right.data)
    if form.proj_code.data and form.proj_code.data != '':
        stat_tmp_1 = stat_tmp_1.filter(TagProject.proj_code.like('%' + form.proj_code.data + "%"))
    if form.proj_name.data and form.proj_name.data != '':
        stat_tmp_1 = stat_tmp_1.filter(TagProject.proj_name.like('%' + form.proj_name.data + "%"))
    if form.tagger_account.data and form.tagger_account.data != '':
        stat_tmp_1 = stat_tmp_1.filter(User.account.like('%' + form.tagger_account.data + "%"))
    if form.task_status.data is not None and form.task_status.data != '':
        stat_tmp_1 = stat_tmp_1.filter(TagTask.task_status == form.task_status.data)
    if form.label_status.data is not None and form.label_status.data != '':
        stat_tmp_1 = stat_tmp_1.filter(TagResult.tag_status == form.label_status.data)
    stat_tmp = stat_tmp_1.subquery('stat_tmp')

    group_tmp = db_v1.session.query(stat_tmp.c.tagger_uid,
                                    func.min(stat_tmp.c.time_classication).label('stat_date_start'),
                                    func.max(stat_tmp.c.time_classication).label('stat_date_end'),
                                    func.count(distinct(stat_tmp.c.task_id)).label('sum_tasks'),
                                    func.count().label('sum_utterances'),
                                    func.sum(stat_tmp.c.detect_duration).label('sum_duration')).group_by(
        stat_tmp.c.tagger_uid).subquery('group_tmp')

    q = db_v1.session.query(group_tmp)

    rvs = pager(q, page=cur_page, per_page=per_page)

    user_info = User.query.filter_by().all()
    user_info = {user.id: user for user in user_info}

    project_info = TagProject.query.filter_by().all()
    project_info = {tag_project.id: tag_project for tag_project in project_info}

    vms = []
    for rv in rvs.items:
        vm = {c: getattr(rv, c, None) for c in rv._fields}
        vm['tagger_name'] = user_info[vm['tagger_uid']].nickname
        vm['tagger_account'] = user_info[vm['tagger_uid']].account
        vm['proj_name'] = project_info[user_info[vm['tagger_uid']].proj_id].proj_name
        vm['proj_code'] = project_info[user_info[vm['tagger_uid']].proj_id].proj_code
        vms.append(vm)

    return PageResultSuccess(msg=u'标注量统计列表', data=vms, page=rvs.page_view())

@timeit
@api.route('/workload-cal', methods=['POST'])
@auth.login_required
def tagstat_workload_cal():
    form = TagStatSearchForm().validate_for_api()
    stat_tmp_1 = db_v1.session.query(UtteranceAccess.detect_duration.label('detect_duration')).filter(
        TagResult.task_id == TagTask.id, TagResult.request_id == UtteranceAccess.request_id,
        TagResult.proj_id == TagProject.id, TagTask.tagger_uid == User.id).filter(TagResult.is_deleted == 0)

    if form.label_time_left.data:
        stat_tmp_1 = stat_tmp_1.filter(TagResult.label_time >= form.label_time_left.data)
    if form.label_time_right.data:
        stat_tmp_1 = stat_tmp_1.filter(TagResult.label_time <= form.label_time_right.data)
    if form.proj_code.data and form.proj_code.data != '':
        stat_tmp_1 = stat_tmp_1.filter(TagProject.proj_code.like('%' + form.proj_code.data + "%"))
    if form.proj_name.data and form.proj_name.data != '':
        stat_tmp_1 = stat_tmp_1.filter(TagProject.proj_name.like('%' + form.proj_name.data + "%"))
    if form.tagger_account.data and form.tagger_account.data != '':
        stat_tmp_1 = stat_tmp_1.filter(User.account.like('%' + form.tagger_account.data + "%"))
    if form.task_status.data is not None and form.task_status.data != '':
        stat_tmp_1 = stat_tmp_1.filter(TagTask.task_status == form.task_status.data)
    if form.label_status.data is not None and form.label_status.data != '':
        stat_tmp_1 = stat_tmp_1.filter(TagResult.tag_status == form.label_status.data)

    stat_tmp = stat_tmp_1.subquery('stat_tmp')

    total_duration = db_v1.session.query(func.sum(stat_tmp.c.detect_duration).label('sum_duration')).first()
    return ResultSuccess(msg=u'计算总标注量', data={'total_duration': total_duration})


@api.route('/workload-old', methods=['POST'])
@auth.login_required
def tagstat_workload_old():
    cur_page, per_page = PageForm.fetch_page_param(PageForm().validate_for_api())

    # TODO：后续根据某个字段来扩充聚合时间的类型
    group_time_format = '%Y-%m-%d'

    stat_tmp_1 = db_v1.session.query(TagTask.tagger_uid.label('tagger_uid'),
                                     UtteranceAccess.detect_duration.label('detect_duration'),
                                     func.from_unixtime(TagResult.label_time, group_time_format).label(
                                      'time_classication')).filter(
        TagResult.task_id == TagTask.id, TagResult.request_id == UtteranceAccess.request_id).filter(
        TagResult.tag_status == 1, TagResult.is_deleted == 0)

    stat_tmp_2 = db_v1.session.query(TagTask.tagger_uid.label('tagger_uid'),
                                     UtteranceTrace.detect_duration.label('detect_duration'),
                                     func.from_unixtime(TagResult.label_time, group_time_format).label(
                                      'time_classication')).filter(
        TagResult.task_id == TagTask.id, TagResult.request_id == UtteranceTrace.request_id).filter(
        TagResult.tag_status == 1, TagResult.is_deleted == 0)

    stat_tmp = stat_tmp_1.union_all(stat_tmp_2).subquery('stat_tmp')

    group_tmp = db_v1.session.query(stat_tmp.c.tagger_uid, stat_tmp.c.time_classication,
                                    func.sum(stat_tmp.c.detect_duration).label('sum_duration')).group_by(
        stat_tmp.c.tagger_uid, stat_tmp.c.time_classication).subquery('group_tmp')

    q = db_v1.session.query(group_tmp)

    rvs = pager(q, page=cur_page, per_page=per_page)

    user_info = User.query.filter_by().all()
    user_info = {user.id: user for user in user_info}

    project_info = TagProject.query.filter_by().all()
    project_info = {tag_project.id: tag_project for tag_project in project_info}

    vms = []
    for rv in rvs.items:
        vm = {c: getattr(rv, c, None) for c in rv._fields}
        vm['tagger_name'] = user_info[vm['tagger_uid']].nickname
        vm['tagger_account'] = user_info[vm['tagger_uid']].account
        vm['proj_name'] = project_info[user_info[vm['tagger_uid']].proj_id].proj_name
        vm['proj_code'] = project_info[user_info[vm['tagger_uid']].proj_id].proj_code
        vms.append(vm)

    return PageResultSuccess(msg=u'标注成功', data=vms, page=rvs.page_view())
