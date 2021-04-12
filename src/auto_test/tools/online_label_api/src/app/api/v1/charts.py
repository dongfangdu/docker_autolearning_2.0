# -*- coding: utf-8 -*-
from sqlalchemy import text
from datetime import datetime
from app.libs.builtin_extend import timeit
from app.libs.error_code import ResultSuccess
from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.models.base import db_v1
from app.validators.forms_v1 import StatisticSearchForm
from decimal import *

api = Redprint('charts')

@api.route('/chartsdataload', methods=['POST'])
@auth.login_required
def charts_dataload():
    # TODO：后续根据某个字段来扩充聚合时间的类型
    group_time_format = '%Y-%m-%d'
    form = StatisticSearchForm().validate_for_api()

    # 注1 时间
    sql_condition_time = ""
    if form.label_time_left.data and form.label_time_right.data:
        datetime1 = datetime.fromtimestamp(form.label_time_left.data)
        datetime2 = datetime.fromtimestamp(form.label_time_right.data)
        sql_condition_time = """and utterance_access.time >= '{0}'
         and utterance_access.time <= '{1}'
         """.format(datetime1, datetime2)

    # 注2 项目编号
    sql_condition_task = ""
    sql_dict = {}
    sql_condition_delay_task = ""
    if form.task_code.data and form.task_code.data != '':
        sql_condition_task = """
            INNER JOIN tag_result
            ON utterance_access.request_id = tag_result.request_id
            AND tag_result.task_id in (select tag_task.id as task_id from tag_task
                                       where tag_task.task_code like :task_code_like_str_2)
            """
        sql_dict['task_code_like_str_2'] = '%' + format(form.task_code.data) + '%'
        sql_condition_delay_task = """
                    INNER JOIN tag_result
                    ON al_ng_diting.request_id = tag_result.request_id
                    AND tag_result.task_id in (select tag_task.id as task_id from tag_task
                                               where tag_task.task_code like :task_code_like_str_22)
                    """
        sql_dict['task_code_like_str_22'] = '%' + format(form.task_code.data) + '%'

    # 注3 法庭0、案件1、角色2
    sql_condition_dt = ""
    sql_condition_delay_dt = ""
    if (form.court_id.data and form.court_id.data != '') or (form.case_id.data and form.case_id.data != '') or (form.role_id.data and form.role_id.data != ''):
        sql_condition_dt = """INNER JOIN al_ng_diting
                              ON utterance_access.request_id = al_ng_diting.request_id """
        sql_condition_delay_dt = """INNER JOIN al_ng_diting_relation
                                    ON al_ng_diting.uuid = al_ng_diting_relation.uuid"""

        if form.court_id.data and form.court_id.data != '':
            sql_condition_dt = sql_condition_dt + """ AND al_ng_diting.uuid IN (SELECT uuid FROM al_ng_diting_relation 
		                                                                        WHERE al_ng_diting_relation.court_id LIKE :court_id_like_str_30 )"""
            sql_dict['court_id_like_str_30'] = '%' + format(form.court_id.data) + '%'

            sql_condition_delay_dt = sql_condition_delay_dt + """ AND al_ng_diting_relation.court_id LIKE :court_id_like_str_300"""
            sql_dict['court_id_like_str_300'] = '%' + format(form.court_id.data) + '%'

        if form.case_id.data and form.case_id.data != '':
            sql_condition_dt = sql_condition_dt + """ AND al_ng_diting.uuid IN (SELECT uuid FROM al_ng_diting_relation 
    	           			                                                    WHERE al_ng_diting_relation.case_id LIKE :case_id_like_str_31)"""
            sql_dict['case_id_like_str_31'] = '%' + format(form.case_id.data) + '%'

            sql_condition_delay_dt = sql_condition_delay_dt + """ AND al_ng_diting_relation.case_id LIKE :case_id_like_str_311"""
            sql_dict['case_id_like_str_311'] = '%' + format(form.case_id.data) + '%'

        if form.role_id.data and form.role_id.data != '':
            sql_condition_dt = sql_condition_dt + """ AND al_ng_diting.uuid IN (SELECT uuid FROM al_ng_diting_relation 
      		           			                                                WHERE al_ng_diting_relation.role_id LIKE :role_id_like_str_32)"""
            sql_dict['role_id_like_str_32'] = '%' + format(form.role_id.data) + '%'

            sql_condition_delay_dt = sql_condition_delay_dt + """ AND al_ng_diting_relation.role_id LIKE :role_id_like_str_322"""
            sql_dict['role_id_like_str_322'] = '%' + format(form.role_id.data) + '%'

    # 注：三个图的基础查询语句
    sql_chart_1 = """
           select count(*),sum(tmp2.rtfgt5), sum(tmp2.rtfgt9), sum(tmp2.rtfgt12),sum(tmp2.totrtf12), sum(tmp2.wait100), sum(tmp2.totrtf5),sum(tmp2.dugt29)  
           from(
                  select case when real_rtf > 0.5 then 1 else 0 end as 'rtfgt5'
                        ,case when real_rtf > 0.9 then 1 else 0 end as 'rtfgt9'
                        ,case when real_rtf > 1.2 then 1 else 0 end as 'rtfgt12'
                        ,case when total_rtf > 1.2 and latency > 500 then 1 else 0 end as 'totrtf12'
                        ,case when wait_cost_time > 100 then 1 else 0 end as 'wait100'
                        ,case when real_rtf <= 0.5 and total_rtf > 1.2 and latency > 500 then 1 else 0 end as 'totrtf5'
                        ,case when (detect_duration/1000) >= 29 then 1 else 0 end as 'dugt29'
                  from utterance_access 
                  INNER JOIN utterance
                  ON utterance.request_id = utterance_access.request_id
                  AND utterance_access.is_deleted = 0 {0} {1} {2} )
                  as tmp2
   
           """.format(sql_condition_time, sql_condition_task, sql_condition_dt)

    sql_chart_2 = """SELECT  COUNT(*),SUM(tmp.detect_duration), sum(tmp.rtfyc), sum(tmp.cutyc), sum(tmp.volyc), sum(tmp.preyc), sum(tmp.latteryc),sum(tmp.rtfdu), sum(tmp.cutdu),sum(tmp.voldu), sum(tmp.predu), sum(tmp.latterdu)
               from (
               SELECT
                 utterance_access.request_id
               , detect_duration
               , case when real_rtf > 0.9 then 1 ELSE 0 end as 'rtfyc'
               , case when real_rtf > 0.9 then detect_duration else 0 end as 'rtfdu'
               , case when cut_ratio > 0 then 1 ELSE 0 end as 'cutyc'
               , case when cut_ratio > 0 then detect_duration ELSE 0 end as 'cutdu'
               , case when volume > 97 or volume < 10 then 1 ELSE 0 end as 'volyc'
               , case when volume > 97 or volume < 10 then detect_duration else 0 end as 'voldu'
               , case when pre_snr < 0 then 1 ELSE 0 end as 'preyc'
               , case when pre_snr < 0 then detect_duration else 0 end as 'predu'
               , case when latter_snr < 0 then 1 ELSE 0 end as 'latteryc'
               , case when latter_snr < 0 then detect_duration else 0 end as 'latterdu'
               from utterance_access 
               inner JOIN utterance 
               on utterance_access.request_id = utterance.request_id 
               and utterance_access.is_deleted = 0 {0} {1} {2})
               AS tmp
               """.format(sql_condition_time, sql_condition_task, sql_condition_dt)

    sql_chart_3 = """SELECT al_ng_diting .http_cost_time , al_ng_diting .trans_delay ,utterance_access.time
               FROM  al_ng_diting 
               INNER JOIN utterance_access
               ON al_ng_diting.request_id = utterance_access.request_id
               AND utterance_access.is_deleted = 0 {0} {1} {2} order by utterance_access.time
               """.format(sql_condition_time, sql_condition_delay_task, sql_condition_delay_dt)

    # 注：执行语句
    # 图一
    resultproxy = db_v1.session.execute(text(sql_chart_1), sql_dict)
    resultpre = resultproxy.fetchall()
    result1 = []
    chart_1_result = []
    if resultpre[0][0] and resultpre[0][0] != 0:
        for i in range(1, 8):
            result1.append((float(Decimal(resultpre[0][i]).quantize(Decimal('0.00')))/float(Decimal(resultpre[0][0]).quantize(Decimal('0.00'))))*100)
        value = ['偏慢', '超时', '严重超时', '出现延时', '排队等识别',  '传输延时', 'vad切分过长']
        for i in range(0, 7):
            item = dict()
            item['识别时长'] = value[i]
            item['识别概况'] = result1[i]
            chart_1_result.append(item)

    # 图二
    resultproxy2 = db_v1.session.execute(text(sql_chart_2), sql_dict)
    resultpre2 = resultproxy2.fetchall()
    result2 = []
    chart_3_result = []
    result4 = []
    chart_2_result = []
    if resultpre2[0][0] and resultpre2[0][0] != 0:
        for i in range(0, 12):
            result2.append(float(Decimal(resultpre2[0][i]).quantize(Decimal('0.00'))))
        for i in range(2, 7):
            chart_3_result.append(result2[i])
        for i in range(7, 12):
            result4.append(result2[i])
        if result2[0] and result2[0] != 0:
            result33 = [(i/result2[0])*100 for i in chart_3_result]
        if result2[1] and result2[1] != 0:
            result44 = [(i / result2[1]) * 100 for i in result4]
        value2 = ['实时率', '截幅比', '音量', '前信噪比', '后信噪比']
        for i in range(0, 5):
            item = dict()
            item['音频质量'] = value2[i]
            item['异常值个数占比'] = result33[i]
            item['异常值时长占比'] = result44[i]
            chart_2_result.append(item)
    # print chart_2_result

    # 注：图三
    # print sql_chart_3
    resultproxy3 = db_v1.session.execute(text(sql_chart_3), sql_dict)
    resultpre3 = resultproxy3.fetchall()
    chart_3_result = []
    if resultpre3:
        for i in range(0, len(resultpre3)):
            item = dict()
            item['识别时间'] = resultpre3[i][2].strftime("%Y/%m/%d %H:%M:%S")
            item['diting到asr传输时延'] = resultpre3[i][0]
            item['客户端到ditting传输时延'] = resultpre3[i][1]
            chart_3_result.append(item)
    # print(chart_3_result)
    return ResultSuccess(msg=u'统计成功', data = [chart_1_result, chart_2_result, chart_3_result])



