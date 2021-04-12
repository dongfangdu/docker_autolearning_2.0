# -*- coding: utf8 -*-
import random
import traceback
import json 
import codecs
import httplib2
import os
import time
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError

from app import create_app
from app.libs.builtin_extend import get_uuid
from app.libs.enums import PrepareTypeEnum, PdataSrcTypeEnum, PrepareStatusEnum, EnhanceTypeEnum
from app.models.base import db_v2
from app.models.v2.engine.prepare import PrepareDataInfo, PrepareRequestInfo
from app.models.v2.engine.utterance import UtteranceAudioAll, UtteranceAccessAll
from app.models.v2.label.labelraw import LabelrawResult, LabelrawUtteranceInfo
from app.models.v2.web.label import LabelResult, LabelUtteranceInfo
from precog import cal_ppl, precog
from app.libs.enhance.data_enhance import DataEnhancement
from sqlalchemy import or_, and_, not_
from multiprocessing import Pool, cpu_count


def prepare_train_data(dp, p_uuid):
    time.sleep(1)
    prepare_status = PrepareStatusEnum.RUNNING.value
    prepare_data_path = None
    dp.logger.info(u'训练数据筛选处理开始')
    with dp.app.app_context():
        duration_limit = dp.app.config['DATA_SELECTION_TRAIN_DURATION_LIMIT']
        label_duration_limit = round(random.randint(40, 60) * duration_limit / 100)
        ng_duration_limit = duration_limit - label_duration_limit

        exclude_request_ids = set()
        exclude_rvs = db_v2.session.query(PrepareDataInfo.request_id).filter(
            PrepareRequestInfo.prepare_uuid == PrepareDataInfo.prepare_uuid,
            or_(PrepareRequestInfo.prepare_type == PrepareTypeEnum.TEST_DATA.value,
                PrepareRequestInfo.prepare_type == PrepareTypeEnum.TRAIN_DATA.value),
            PrepareRequestInfo.is_deleted == 0
        ).all()

        exclude_request_ids = exclude_request_ids.union(set([request_id for request_id, in exclude_rvs]))

        # exclude_ng_set = set()

        # prepare_data_info_list = []
        label_data_info_list = []
        enhan_data_info_list = []
        ident_data_info_list = []

        label_switch = dp.app.config['LABEL_KEY']
        enhan_switch = dp.app.config['ENHAN_KEY']
        ident_switch = dp.app.config['IDENT_KEY']

        # 准备标注数据
        if label_switch == 'T':
            dp.logger.info(u'标注数据准备开始')
            rvs = db_v2.session.query(LabelResult, LabelUtteranceInfo).outerjoin(
                LabelUtteranceInfo, LabelResult.request_id == LabelUtteranceInfo.request_id
                ).filter(
                LabelResult.label_status == 1,
                not_(LabelResult.label_text.like("%~%")),
                not_(LabelResult.label_text.op('regexp')('[0-9]'))
            ).all()

            # rvs = db_v2.session.query(LabelrawResult, LabelrawUtteranceInfo).outerjoin(
            #     LabelrawUtteranceInfo, LabelrawResult.request_id == LabelrawUtteranceInfo.request_id
            #     ).filter(not_(LabelrawResult.label_text.like("%~%")),
            #              not_(LabelrawResult.label_text.op('regexp')('[0-9]'))
            #     ).all()

            label_total_cnt = len(rvs)
            if label_total_cnt < 1:
                # prepare_status = PrepareStatusEnum.IDK.value
                # return {'dp': dp, 'prepare_uuid': p_uuid, 'prepare_status': prepare_status,
                #        'prepare_data_path': prepare_data_path}
                dp.logger.info(u'没有标注数据了')

            prepare_loop_counter = 0
            prepare_loop_counter_limit = dp.app.config['LABEL_LOOP_COUNTER_LIMIT']

            duration_sum = 0
            duration_limit = label_duration_limit

            prepare_data_items = dict()
            while True:
                if label_total_cnt < 1:
                    break
                if prepare_loop_counter > prepare_loop_counter_limit:
                    dp.logger.info(u'准备音频总时长 {} ms'.format(duration_sum))
                    break
                # if duration_sum > duration_limit:
                #     dp.logger.info(u'准备音频总时长 {} ms'.format(duration_sum))
                #     break

                idx = random.randint(0, label_total_cnt - 1)
                request_id = rvs[idx][0].request_id
                # request_id = rvs[idx][0].request_id
                prepare_loop_counter += 1
                if request_id not in exclude_request_ids:
                    prepare_data_items[request_id] = idx
                    duration_sum += rvs[idx][1].detect_duration

                    # duration_sum += rvs[idx][1].detect_duration

            for i in prepare_data_items.values():
                data_info = PrepareDataInfo()
                data_info.prepare_uuid = p_uuid
                data_info.pdata_uuid = get_uuid()
                data_info.pdata_src_type = PdataSrcTypeEnum.LABELED_SRC.value
                # data_info.pdata_url = rvs[i][1].url
                # data_info.pdata_text = rvs[i][0].label_text
                # data_info.request_id = rvs[i][0].request_id
                # data_info.uttr_url = rvs[i][1].url
                # data_info.uttr_result = rvs[i][1].result
                # data_info.uttr_duration = rvs[i][1].detect_duration
                # data_info.label_uuid = rvs[i][0].label_uuid
                # data_info.label_text = rvs[i][0].label_text
                data_info.pdata_url = rvs[i][1].url
                data_info.pdata_text = rvs[i][0].label_text
                data_info.request_id = rvs[i][0].request_id
                data_info.uttr_url = rvs[i][1].url
                data_info.uttr_result = rvs[i][1].result
                data_info.uttr_duration = rvs[i][1].detect_duration
                data_info.label_uuid = rvs[i][0].label_uid
                data_info.label_text = rvs[i][0].label_text
                label_data_info_list.append(data_info)
            dp.logger.info(u'标注数据准备结束')
        else:
            dp.logger.info(u'标注数据没有准备')
        
        # 准备识别数据
        if ident_switch == 'T':
            dp.logger.info(u'识别数据准备开始')
            if label_switch == 'T':
                exclude_request_ids = exclude_request_ids.union(prepare_data_items.keys())

            # rvs = db_v2.session.query(LabelResult, LabelUtteranceInfo).outerjoin(
            #     LabelUtteranceInfo, LabelResult.request_id == LabelUtteranceInfo.request_id
            #     ).filter(
            #     or_(LabelResult.proj_id == 1, LabelResult.proj_id == 5, LabelResult.proj_id == 21),
            #     LabelResult.label_status == 0,
            #     not_(LabelUtteranceInfo.result.like("%~%")),
            #     not_(LabelUtteranceInfo.result.op('regexp')('[0-9]')),
            #     ).order_by(desc(LabelUtteranceInfo.time)).limit(1000000).all()

            rvs = db_v2.session.query(UtteranceAudioAll, UtteranceAccessAll).filter(
                    UtteranceAudioAll.request_id == UtteranceAccessAll.request_id,
                    not_(UtteranceAccessAll.result.like("%~%")),
                    not_(UtteranceAccessAll.result.op('regexp')('[0-9]'))
                    ).order_by(desc(UtteranceAccessAll.time)).limit(1000000).all()

            ident_total_cnt = len(rvs)
            prepare_loop_counter = 0
            prepare_loop_counter_limit = dp.app.config['IDENT_LOOP_COUNTER_LIMIT']
            duration_sum = 0
            duration_limit = ng_duration_limit

            prepare_data_items = dict()
            while True:
                if ident_total_cnt < 1:
                    dp.logger.info(u'没有识别数据了')
                    break
                if prepare_loop_counter > prepare_loop_counter_limit:
                    dp.logger.info(u'准备音频总时长 {} ms'.format(duration_sum))
                    break
                # if duration_sum > duration_limit:
                #     dp.logger.info(u'准备音频总时长 {} ms'.format(duration_sum))
                #     break

                idx = random.randint(0, ident_total_cnt - 1)
                duration_sum += rvs[idx][1].detect_duration
                request_id = rvs[idx][0].request_id
                real_rtf = rvs[idx][1].real_rtf
                result = rvs[idx][1].result
                # duration_sum += rvs[idx][1].detect_duration
                # request_id = rvs[idx][0].request_id
                # real_rtf = rvs[idx][1].real_rtf
                # result = rvs[idx][1].result
                ppl = cal_ppl(result)
                pre_wer = precog(real_rtf, ppl)
                threshold_pre_wer = dp.app.config['THRESHOLD_PRE_WER']
                threshold_length = dp.app.config['THRESHOLD_LENGTH']
                prepare_loop_counter += 1
                if request_id not in exclude_request_ids and pre_wer <= threshold_pre_wer and len(result) >= threshold_length:
                    prepare_data_items[request_id] = idx


            for i in prepare_data_items.values():
                data_info = PrepareDataInfo()
                data_info.prepare_uuid = p_uuid
                data_info.pdata_uuid = get_uuid()
                data_info.pdata_src_type = PdataSrcTypeEnum.RECOGNIZED_SRC.value
                data_info.pdata_url = rvs[i][0].url
                data_info.pdata_text = rvs[i][1].result
                data_info.request_id = rvs[i][0].request_id
                data_info.uttr_url = rvs[i][0].url
                data_info.uttr_result = rvs[i][1].result
                data_info.uttr_duration = rvs[i][1].detect_duration
                # data_info.pdata_url = rvs[i][1].url
                # data_info.pdata_text = rvs[i][1].result
                # data_info.request_id = rvs[i][0].request_id
                # data_info.uttr_url = rvs[i][1].url
                # data_info.uttr_result = rvs[i][1].result
                # data_info.uttr_duration = rvs[i][1].detect_duration
                data_info.label_uuid = None
                data_info.label_text = None
                ident_data_info_list.append(data_info)
            dp.logger.info(u'识别数据准备结束')
        else:
            dp.logger.info(u'识别数据没有准备')

        try:
            target_dir = dp.app.config['DATA_SELECTION_TRAIN_PREPARE_DIR']
            target_dir = os.path.join(target_dir, '{}/data'.format(p_uuid))
            target_dir = os.path.abspath(target_dir)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            if label_switch == 'T':
                dp.logger.info(u'标注数据拉取开始')
                for label_data_info in label_data_info_list:
                    tmp_res = download_train_data(dp, p_uuid, target_dir, label_data_info)
                dp.logger.info(u'标注数据拉取结束')
            # 准备增强数据
            if label_switch == 'T' and enhan_switch == 'T' and len(label_data_info_list) > 0:
                dp.logger.info(u'标注数据增强开始')
                wav_target_dir = os.path.join(target_dir, 'wav')
                # dp.logger.info(wav_target_dir)
                enhance_res = DataEnhancement().enhance_data(EnhanceTypeEnum.VOICE_CONVERSION.value, wav_target_dir)
                # dp.logger.info(enhance_res)
                enh_data_path = json.loads(enhance_res)['final_save_path']
                # dp.logger.info(enh_data_path)
                dp.logger.info(u'标注数据增强结束')
                for wav_ele in os.listdir(enh_data_path):
                    data_info = PrepareDataInfo()
                    data_info.prepare_uuid = "Null"
                    data_info.pdata_uuid = get_uuid()
                    data_info.pdata_src_type = PdataSrcTypeEnum.ENHANCED_SRC.value
                    data_info.pdata_url = wav_ele
                    data_info.pdata_text = "Null"
                    data_info.request_id = wav_ele[:-4]
                    data_info.uttr_url = wav_ele
                    data_info.uttr_result = "Null"
                    data_info.uttr_duration = 0
                    data_info.label_uuid = "Null"
                    data_info.label_text = "Null"
                    data_info.enhance_code = EnhanceTypeEnum.ADJUST_VOLUME.value
                    enhan_data_info_list.append(data_info)
                #
                dp.logger.info(u'增强数据拉取开始')
                txt_target_dir = os.path.join(target_dir, 'txt')
                txt_target_dir = os.path.abspath(txt_target_dir)
                if not os.path.exists(txt_target_dir):
                    os.mkdir(txt_target_dir)
                txt_target_filepath = os.path.join(txt_target_dir, 'wav_txt_map.txt')
                txt_target_filepath = os.path.abspath(txt_target_filepath)
                data_txt = loadfromfile(txt_target_filepath)
                pool = Pool(50)
                cores = cpu_count()
                for wav_ele in os.listdir(enh_data_path):
                    # os.system('cp %s %s'%(os.path.join(enh_data_path, wav_ele), os.path.join(wav_target_dir, 'enh_' + wav_ele)))
                    # n, ln = findnum(data_txt, wav_ele.split("_")[0])
                    # # print(ln)
                    pool.apply_async(pool_enh_data, (enh_data_path, wav_ele, wav_target_dir, data_txt, txt_target_filepath))
                pool.close()
                pool.join()
                dp.logger.info(u'增强数据拉取结束')
            else:
                dp.logger.info(u'增强数据没有准备')
            #
            if ident_switch == 'T':
                dp.logger.info(u'识别数据拉取开始')
                for ident_data_info in ident_data_info_list:
                    tmp_res = download_train_data(dp, p_uuid, target_dir, ident_data_info)
                dp.logger.info(u'识别数据拉取结束')
            #
            prepare_data_info_list = label_data_info_list + enhan_data_info_list + ident_data_info_list

            dp.logger.info(u'训练数据入库开始')
            with db_v2.auto_commit():
                db_v2.session.bulk_save_objects(prepare_data_info_list)
            dp.logger.info(u'训练数据入库成功')
            dp.logger.info(u'标注数据入库条数：{}'.format(len(label_data_info_list)))
            dp.logger.info(u'增强数据入库条数：{}'.format(len(enhan_data_info_list)))
            dp.logger.info(u'识别数据入库条数：{}'.format(len(ident_data_info_list)))
            dp.logger.info(u'训练数据入库条数：{}'.format(len(prepare_data_info_list)))
            prepare_status = PrepareStatusEnum.DB_DONE.value
            prepare_data_path = target_dir
            prepare_status = PrepareStatusEnum.FINISHED.value
            #

        except SQLAlchemyError:
            dp.logger.error(traceback.format_exc())
            dp.logger.info(u'训练数据入库失败')
            prepare_status = PrepareStatusEnum.FAILED.value

    prepare_type = PrepareTypeEnum.TRAIN_DATA.value
    dp.logger.info(u'训练数据筛选处理结束')
    return {'dp': dp, 'prepare_uuid': p_uuid, 'prepare_type': prepare_type, 'prepare_status': prepare_status, 'prepare_data_path': prepare_data_path,
            'prepare_data_cnt': len(prepare_data_info_list)}


def pool_enh_data(enh_data_path, wav_ele, wav_target_dir, data_txt, txt_target_filepath):
    os.system('cp %s %s'%(os.path.join(enh_data_path, wav_ele), os.path.join(wav_target_dir, 'enh_' + wav_ele)))
    n, ln = findnum(data_txt, wav_ele.split("_")[0])
    with codecs.open(txt_target_filepath, 'a+', encoding='utf-8') as f:
        f.write(u'{}\t{}'.format('enh_' + wav_ele, ln.split('\t')[1]))


def loadfromfile(filename):
    with open(filename, 'rt') as handle:
        return handle.readlines()


def findnum(lst, num):
    for i, ln in enumerate(lst):
        if ln.startswith(num):
            return i, ln


def download_train_data(dp, p_uuid, target_dir, prepare_data_info):
    wav_target_dir = os.path.join(target_dir, 'wav')
    wav_target_dir = os.path.abspath(wav_target_dir)
    if not os.path.exists(wav_target_dir):
        os.mkdir(wav_target_dir)

    uttr_url = prepare_data_info.pdata_url
    filename = uttr_url.split('/')[-1]
    wav_target_filepath = os.path.join(wav_target_dir, filename)
    wav_target_filepath = os.path.abspath(wav_target_filepath)

    # print wav_target_filepath

    h = httplib2.Http()
    fs_host = dp.app.config['FS_HOST']
    fs_port = dp.app.config['FS_PORT']
    #dp.logger.info(uttr_url)
    #dp.logger.info(wav_target_filepath)
    url = 'http://{}:{}{}'.format(fs_host, fs_port, uttr_url)
    #dp.logger.info(url)
    resp, content = h.request(url)
    if resp['status'] == '200':
        with open(wav_target_filepath, 'wb') as f:
            f.write(content)

    os.system("ffmpeg -i %s -ar 16000 %s -y >/dev/null 2>&1 &" % (wav_target_filepath, wav_target_filepath))

    txt_target_dir = os.path.join(target_dir, 'txt')
    txt_target_dir = os.path.abspath(txt_target_dir)
    if not os.path.exists(txt_target_dir):
        os.mkdir(txt_target_dir)
    txt_target_filepath = os.path.join(txt_target_dir, 'wav_txt_map.txt')
    txt_target_filepath = os.path.abspath(txt_target_filepath)
    with codecs.open(txt_target_filepath, 'a+', encoding='utf-8') as f:
        f.write(u'{}\t{}\n'.format(filename, prepare_data_info.pdata_text))
    return True

