# -*- coding: utf8 -*-
import os
import time

from app import create_app
from app.libs.builtin_extend import get_uuid
from app.models.base import db_v1, db_v2
from app.models.v2.engine.ng import NgDiting, NgDitingRelation
from app.models.v2.engine import UtteranceAudio, UtteranceAccess as NewAccess, UtteranceAccess
from app.models.v2.label import LabelrawResult, LabelrawUtteranceInfo
from app.models.v1.sysmng import Region as OldRegion
from app.models.v1.sysmng import Role as OldRole
from app.models.v1.sysmng import User as OldUser
from app.models.v1.tagfile import UtteranceAccess as OldAccess, Utterance
from app.models.v1.tagproj import TagProject, TagResult
from app.models.v2.web.common import Region as NewRegion
from app.models.v2.web.label import LabelProject, LabelUtteranceInfo
from app.models.v2.web.label import LabelUserMap
from app.models.v2.web import Role as NewRole
from app.models.v2.web import User as NewUser

from app.models.v2.web.label import LabelDitingInfo


def user_transfer():
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')

    with app.app_context():
        old_user_list = OldUser.query.filter_by().all()
        with db_v1.auto_commit():
            for old_user in old_user_list:
                new_user = NewUser()
                new_user.account = old_user.account
                new_user.password = '123456'
                new_user.nickname = old_user.nickname
                new_user.telephone = old_user.telephone
                new_user.ac_type = old_user.ac_type
                new_user.ac_status = old_user.ac_status
                new_user.rid = old_user.rid

                db_v1.session.add(new_user)


def user_addnew():
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')

    with app.app_context():
        with db_v1.auto_commit():
            new_user = NewUser()
            new_user.account = 'gsv_test01'
            new_user.password = '123456'
            new_user.nickname = 'gsv_test01'
            new_user.telephone = None
            new_user.ac_type = 100
            new_user.ac_status = 11
            new_user.rid = 5

            db_v1.session.add(new_user)

            new_user = NewUser()
            new_user.account = 'gsv_test02'
            new_user.password = '123456'
            new_user.nickname = 'gsv_test02'
            new_user.telephone = None
            new_user.ac_type = 100
            new_user.ac_status = 11
            new_user.rid = 5

            db_v1.session.add(new_user)

            new_user = NewUser()
            new_user.account = 'csv_test01'
            new_user.password = '123456'
            new_user.nickname = 'csv_test01'
            new_user.telephone = None
            new_user.ac_type = 100
            new_user.ac_status = 11
            new_user.rid = 6

            db_v1.session.add(new_user)

            new_user = NewUser()
            new_user.account = 'csv_test02'
            new_user.password = '123456'
            new_user.nickname = 'csv_test02'
            new_user.telephone = None
            new_user.ac_type = 100
            new_user.ac_status = 11
            new_user.rid = 6

            db_v1.session.add(new_user)


def role_transfer():
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')

    with app.app_context():
        old_list = OldRole.query.filter_by().all()
        with db_v1.auto_commit():
            for old_ in old_list:
                new_ = NewRole()
                new_.rname = old_.rname
                new_.rcode = old_.rcode
                new_.rdesc = old_.rdesc

                db_v1.session.add(new_)


def role_addnew():
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')

    with app.app_context():
        with db_v1.auto_commit():
            new_ = NewRole()
            new_.rname = '运维人员'
            new_.rcode = 'supervisor'
            new_.rdesc = '通用运维人员，主要职责是监控引擎识别的情况。'

            db_v1.session.add(new_)

            new_ = NewRole()
            new_.rname = '法院运维人员'
            new_.rcode = 'supervisor_court'
            new_.rdesc = '法院运维人员，主要职责是结合法院相关业务进行对引擎识别的情况的监控。'

            db_v1.session.add(new_)


def region_transfer():
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')

    with app.app_context():
        old_list = OldRegion.query.filter_by().all()
        with db_v1.auto_commit():
            for old_ in old_list:
                new_ = NewRegion()
                new_.id = old_.id
                new_.name = old_.name
                new_.parent_id = old_.parent_id
                new_.level = old_.level

                db_v1.session.add(new_)


def project_transer():
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    with app.app_context():
        old_list = TagProject.query.filter_by().all()
        with db_v1.auto_commit():
            for old_ in old_list:
                new_ = LabelProject()
                # new_.id = LableProject.id
                new_.proj_code = old_.proj_code
                new_.proj_name = old_.proj_name
                new_.create_uid = old_.create_uid
                new_.region_id = old_.region_id
                new_.proj_desc = old_.proj_desc
                new_.proj_status = old_.proj_status

                db_v1.session.add(new_)
    pass


def labeluser_transfer():
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    with app.app_context():
        user_list = NewUser.query.filter_by().all()
        with db_v1.auto_commit():
            for user in user_list:
                new_ = LabelUserMap()
                old_user = OldUser.query.filter_by(account=user.account).first()
                if not old_user:
                    continue
                new_.uid = user.id
                # print old_user.id, old_user.account
                tp = TagProject.query.filter_by(id=old_user.proj_id).first()
                if not tp:
                    continue
                # print tp.proj_code
                lp = LabelProject.query.filter_by(proj_code=tp.proj_code).first()
                new_.rel_id = lp.id
                new_.rel_type = 1

                db_v1.session.add(new_)


def uttr_access_transfer():
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    with app.app_context():

        counter = 0
        counter_limit = 200
        offset_v = 262000
        step = 5000
        while True:
            counter += 1
            old_list = OldAccess.query.filter_by().order_by(OldAccess.id).limit(step).offset(offset_v).all()
            if len(old_list) < 1 or counter > counter_limit:
                break
            print 'first id: ', old_list[0].id
            with db_v1.auto_commit():
                new_list = []
                for old_ in old_list:
                    new_ = NewAccess()
                    new_.insert_time = int(time.time())
                    new_.is_deleted = 0
                    new_.ng_version = '2.6'
                    new_.request_id = old_.request_id
                    new_.time = old_.time
                    new_.app = old_.app
                    new_.group = old_.group
                    new_.ip = old_.ip
                    new_.app_key = old_.app_key
                    new_.session_id = old_.session_id
                    new_.device_uuid = old_.device_uuid
                    new_.uid = old_.uid
                    new_.start_timestamp = old_.start_timestamp
                    new_.latency = old_.latency
                    new_.status_code = old_.status_code
                    new_.status_message = old_.status_message
                    new_.backend_apps = old_.backend_apps
                    new_.duration = old_.duration
                    new_.audio_format = old_.audio_format
                    new_.audio_url = old_.audio_url
                    new_.sample_rate = old_.sample_rate
                    new_.method = old_.method
                    new_.packet_count = old_.packet_count
                    new_.avg_packet_duration = old_.avg_packet_duration
                    new_.total_rtf = old_.total_rtf
                    new_.raw_rtf = old_.raw_rtf
                    new_.real_rtf = old_.real_rtf
                    new_.detect_duration = old_.detect_duration
                    new_.total_cost_time = old_.total_cost_time
                    new_.receive_cost_time = old_.receive_cost_time
                    new_.wait_cost_time = old_.wait_cost_time
                    new_.process_time = old_.process_time
                    new_.processor_id = old_.processor_id
                    new_.user_id = old_.user_id
                    new_.vocabulary_id = old_.vocabulary_id
                    new_.keyword_list_id = old_.keyword_list_id
                    new_.customization_id = old_.customization_id
                    new_.class_vocabulary_id = old_.class_vocabulary_id
                    new_.result = old_.result
                    new_.group_name = old_.group_name

                    new_list.append(new_)

                db_v1.session.bulk_save_objects(new_list)

            offset_v += step
            print 'offset: ', offset_v
            print 'last id: ', old_list[-1].id


def uttr_audio_transfer():
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    with app.app_context():

        counter = 0
        counter_limit = 200
        offset_v = 0
        step = 5000
        while True:
            counter += 1
            old_list = Utterance.query.filter_by().order_by(Utterance.id).limit(step).offset(offset_v).all()
            if len(old_list) < 1 or counter > counter_limit:
                break
            print 'first id: ', old_list[0].id
            with db_v1.auto_commit():
                new_list = []
                for old_ in old_list:
                    new_ = UtteranceAudio()
                    new_.insert_time = int(time.time())
                    new_.request_id = old_.request_id
                    new_.path = old_.path
                    new_.url = old_.url
                    new_.truncation_ratio = old_.cut_ratio
                    new_.volume = old_.volume
                    new_.snr = old_.snr
                    new_.pre_snr = old_.pre_snr
                    new_.post_snr = old_.latter_snr
                    new_.is_assigned = old_.is_assigned

                    new_list.append(new_)

                db_v1.session.bulk_save_objects(new_list)

            offset_v += step
            print 'offset: ', offset_v
            print 'last id: ', old_list[-1].id


def labelraw_result_transfer():
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    with app.app_context():

        counter = 0
        counter_limit = 200
        offset_v = 0
        step = 2
        while True:
            counter += 1
            old_list = db_v1.session.query(TagResult, Utterance).filter(TagResult.request_id == Utterance.request_id,
                                                                        TagResult.tag_status == 1).filter_by().order_by(
                TagResult.id).limit(step).offset(offset_v).all()
            if len(old_list) < 1 or counter > counter_limit:
                break
            print 'first id: ', old_list[0][0].id
            with db_v1.auto_commit():
                new_list = []
                for old_ in old_list:
                    new_ = LabelrawResult()
                    new_.insert_time = int(time.time())
                    new_.label_uuid = get_uuid()
                    new_.label_text = old_[0].label_text
                    new_.label_time = old_[0].label_time
                    new_.request_id = old_[0].request_id
                    new_.uttr_url = old_[1].url

                    new_list.append(new_)

                db_v1.session.bulk_save_objects(new_list)

            offset_v += step
            print 'offset: ', offset_v
            print 'last id: ', old_list[-1][0].id


def labelraw_uttr_info():
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    with app.app_context():

        counter = 0
        counter_limit = 200
        offset_v = 0
        step = 2000
        while True:
            counter += 1
            old_list = db_v1.session.query(TagResult, Utterance, OldAccess).filter(
                TagResult.request_id == Utterance.request_id,
                TagResult.request_id == OldAccess.request_id,
                TagResult.tag_status == 1).filter_by().order_by(
                TagResult.id).limit(step).offset(offset_v).all()
            if len(old_list) < 1 or counter > counter_limit:
                break
            print 'first id: ', old_list[0][0].id
            with db_v1.auto_commit():
                new_list = []
                for old_ in old_list:
                    new_ = LabelrawUtteranceInfo()
                    new_.insert_time = int(time.time())
                    new_.is_deleted = 0
                    new_.version = '2.6'
                    # new_.id = old_[2].id
                    new_.request_id = old_[2].request_id
                    new_.time = old_[2].time
                    new_.app = old_[2].app
                    new_.group = old_[2].group
                    new_.ip = old_[2].ip
                    new_.app_key = old_[2].app_key
                    new_.session_id = old_[2].session_id
                    new_.device_uuid = old_[2].device_uuid
                    new_.uid = old_[2].uid
                    new_.start_timestamp = old_[2].start_timestamp
                    new_.latency = old_[2].latency
                    new_.status_code = old_[2].status_code
                    new_.status_message = old_[2].status_message
                    new_.backend_apps = old_[2].backend_apps
                    new_.duration = old_[2].duration
                    new_.audio_format = old_[2].audio_format
                    new_.audio_url = old_[2].audio_url
                    new_.sample_rate = old_[2].sample_rate
                    new_.method = old_[2].method
                    new_.packet_count = old_[2].packet_count
                    new_.avg_packet_duration = old_[2].avg_packet_duration
                    new_.total_rtf = old_[2].total_rtf
                    new_.raw_rtf = old_[2].raw_rtf
                    new_.real_rtf = old_[2].real_rtf
                    new_.detect_duration = old_[2].detect_duration
                    new_.total_cost_time = old_[2].total_cost_time
                    new_.receive_cost_time = old_[2].receive_cost_time
                    new_.wait_cost_time = old_[2].wait_cost_time
                    new_.process_time = old_[2].process_time
                    new_.processor_id = old_[2].processor_id
                    new_.user_id = old_[2].user_id
                    new_.vocabulary_id = old_[2].vocabulary_id
                    new_.keyword_list_id = old_[2].keyword_list_id
                    new_.customization_id = old_[2].customization_id
                    new_.class_vocabulary_id = old_[2].class_vocabulary_id
                    new_.result = old_[2].result
                    new_.group_name = old_[2].group_name
                    new_.path = old_[1].path
                    new_.url = old_[1].url
                    new_.truncation_ratio = old_[1].cut_ratio
                    new_.volume = old_[1].volume
                    new_.snr = old_[1].snr
                    new_.pre_snr = old_[1].pre_snr
                    new_.post_snr = old_[1].latter_snr

                    new_list.append(new_)

                db_v1.session.bulk_save_objects(new_list)

            offset_v += step
            print 'offset: ', offset_v
            print 'last id: ', old_list[-1][0].id


def label_utterance_info():
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')

    request_ids = ['0f24ab9420cdeaac9a2b293c1f2ccec2', '9a778770403a28e60a14fac7fca0895f',
                   'd5dce7803041bcf4e999beb531307810', 'fe3af1e2a33229e4845450a48e6968b5',
                   'f3b58a4b036a4a0ec65a5630305f53af', 'd6e0a3d14aa675ab6c33b3761d46be80',
                   '4102e7716f70c5870d75b314ed7ef662', 'a322b432f4e2094146a278ed884c2375',
                   '2993ebc22c6caa262ab7242b1615c5b6']
    with app.app_context():

        counter = 0
        counter_limit = 9
        offset_v = 0
        step = 2000
        while True:
            counter += 1
            old_list = db_v1.session.query(UtteranceAccess, UtteranceAudio).filter(
                UtteranceAudio.request_id == UtteranceAccess.request_id,
                UtteranceAudio.request_id.in_(request_ids)
            ).filter_by().order_by(
                UtteranceAudio.id).limit(step).offset(offset_v).all()
            print len(old_list)
            if len(old_list) < 1 or counter > counter_limit:
                break
            print 'first id: ', old_list[0][0].id
            with db_v1.auto_commit():
                new_list = []
                for old_ in old_list:
                    new_ = LabelUtteranceInfo()
                    new_.ng_version = old_[0].ng_version
                    new_.request_id = old_[0].request_id
                    new_.time = old_[0].time
                    new_.app = old_[0].app
                    new_.group = old_[0].group
                    new_.ip = old_[0].ip
                    new_.app_key = old_[0].app_key
                    new_.session_id = old_[0].session_id
                    new_.device_uuid = old_[0].device_uuid
                    new_.uid = old_[0].uid
                    new_.start_timestamp = old_[0].start_timestamp
                    new_.latency = old_[0].latency
                    new_.status_code = old_[0].status_code
                    new_.status_message = old_[0].status_message
                    new_.backend_apps = old_[0].backend_apps
                    new_.duration = old_[0].duration
                    new_.audio_format = old_[0].audio_format
                    new_.audio_url = old_[0].audio_url
                    new_.sample_rate = old_[0].sample_rate
                    new_.method = old_[0].method
                    new_.packet_count = old_[0].packet_count
                    new_.avg_packet_duration = old_[0].avg_packet_duration
                    new_.total_rtf = old_[0].total_rtf
                    new_.raw_rtf = old_[0].raw_rtf
                    new_.real_rtf = old_[0].real_rtf
                    new_.detect_duration = old_[0].detect_duration
                    new_.total_cost_time = old_[0].total_cost_time
                    new_.receive_cost_time = old_[0].receive_cost_time
                    new_.wait_cost_time = old_[0].wait_cost_time
                    new_.process_time = old_[0].process_time
                    new_.processor_id = old_[0].processor_id
                    new_.user_id = old_[0].user_id
                    new_.vocabulary_id = old_[0].vocabulary_id
                    new_.keyword_list_id = old_[0].keyword_list_id
                    new_.customization_id = old_[0].customization_id
                    new_.class_vocabulary_id = old_[0].class_vocabulary_id
                    new_.result = old_[0].result
                    new_.group_name = old_[0].group_name
                    new_.path = old_[1].path
                    new_.url = old_[1].url
                    new_.truncation_ratio = old_[1].truncation_ratio
                    new_.volume = old_[1].volume
                    new_.snr = old_[1].snr
                    new_.pre_snr = old_[1].pre_snr
                    new_.post_snr = old_[1].post_snr
                    new_.uttr_status = 1

                    new_list.append(new_)

                db_v1.session.bulk_save_objects(new_list)

            offset_v += step
            print 'offset: ', offset_v
            print 'last id: ', old_list[-1][0].id

def label_diting_info():
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    with app.app_context():
        old_list = db_v2.session.query(NgDiting, NgDitingRelation).filter(
            NgDiting.uuid == NgDitingRelation.uuid
        ).all()
        diting_info_list = []
        for diting, diting_relation in old_list:
            diting_info = LabelDitingInfo()
            for v_key in diting.keys():
                if v_key in ['id', 'insert_time', 'is_deleted', ]:
                    continue
                setattr(diting_info, v_key, getattr(diting, v_key, None))
            for v_key in diting_relation.keys():
                if v_key in ['id', 'insert_time', 'is_deleted', ]:
                    continue
                setattr(diting_info, v_key, getattr(diting_relation, v_key, None))
            diting_info_list.append(diting_info)

        with db_v2.auto_commit():
            # db_v2.session.bulk_save_objects(diting_info_list)
            diting_info_dict_list = [dict(diting_info) for diting_info in diting_info_list]
            db_v2.session.execute(LabelDitingInfo.__table__.insert().prefix_with('IGNORE'), diting_info_dict_list)

        print len(old_list)


if __name__ == '__main__':
    # user_transfer()
    # role_transfer()
    # role_addnew()
    # user_addnew()
    # region_transfer()
    # project_transer()
    # labeluser_transfer()
    # uttr_access_transfer()
    # uttr_audio_transfer()
    # labelraw_result_transfer()
    # labelraw_uttr_info()
    # label_utterance_info()
    label_diting_info()
    pass
