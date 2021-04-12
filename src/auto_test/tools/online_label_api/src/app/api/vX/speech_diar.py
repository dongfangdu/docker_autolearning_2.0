# -*- coding: utf-8 -*-
import json
import logging
import shutil
import zipfile
from collections import defaultdict

import codecs
import magic
import os
import yaml
from flask import request, send_from_directory
from pydub import AudioSegment
from werkzeug.utils import secure_filename

from app.libs.asr_func.filetrans_handler import FileTransRestful
from app.libs.builtin_extend import get_uuid
from app.libs.error import APIException
from app.libs.error_code import ResultSuccess, ParameterException
from app.libs.ng_utils import get_ng_sample_rate
from app.libs.path_utils import get_cfg_dir, get_tmp_dir, get_bin_dir
from app.libs.redprint import Redprint
from app.validators.forms_vX import PathForm

api = Redprint('spdiar')  # speech_diarization 人声分离
logger = logging.getLogger(__name__)


@api.route('/ng-sr', methods=['GET'])
def spdiar_ng_samplerate():
    return str(get_ng_sample_rate(is_running=True))

@api.route('/demo', methods=['POST'])
def spdiar_demo():
    # ### 进行分离
    diar_uuid = get_uuid()
    logger.info(u'人声分离id: {}'.format(diar_uuid))

    filepath = PathForm().validate_for_api().filepath.data
    # ### 待分离音频路径
    filepath = os.path.abspath(filepath)
    logger.info(u'待处理音频路径: {}'.format(filepath))

    wav_property = do_diar_recog(diar_uuid, filepath)

    return ResultSuccess(msg=u'人声分离成功', data={'diar_uuid': diar_uuid, 'diar_recog': wav_property})


@api.route('/demo', methods=['GET'])
def spdiar_demo_get():
    diar_uuid = request.args.get("diar_uuid")
    if not diar_uuid or diar_uuid == '':
        raise ParameterException(msg=u'diar_uuid参数有误')
    # diar_res_json = os.path.join(get_spdiar_tmp_dir(), '{}.json'.format(diar_uuid))
    # if not os.path.exists(diar_res_json):
    #     raise APIException(u'人声分离结果丢失', 510, 5102)

    diar_recog_json = os.path.join(get_spdiar_tmp_dir(), '{}-recognition.json'.format(diar_uuid))
    if not os.path.exists(diar_recog_json):
        raise APIException(u'人声分离识别结果丢失', 510, 5103)

    with codecs.open(diar_recog_json, encoding='utf8') as f:
        wav_property = json.load(f)

    return ResultSuccess(msg=u'功能测试', data={'diar_uuid': diar_uuid, 'diar_recog': wav_property})


@api.route('/demo-download', methods=['GET'])
def spdiar_download():
    diar_uuid = request.args.get("diar_uuid")
    if not diar_uuid or diar_uuid == '':
        raise ParameterException(msg=u'diar_uuid参数有误')

    download_dir = get_spdiar_tmp_dir()
    download_file = '{}.zip'.format(diar_uuid)
    return send_from_directory(directory=download_dir, filename=download_file)


@api.route('/demo-upload', methods=['POST'])
def spdiar_demo_upload():
    diar_uuid = get_uuid()
    logger.info(u'人声分离id: {}'.format(diar_uuid))

    # ### 上传文件
    if 'diar_file' not in request.files:
        raise APIException(u'没有音频文件', 400, 4100)
    upload_file = request.files['diar_file']
    if not upload_file:
        raise APIException(u'没有音频文件', 400, 4100)
    if upload_file.filename == '':
        raise APIException(u'没有选择音频文件', 400, 4101)
    if not allowed_file(upload_file.filename):
        raise APIException(u'只接受文件后缀为wav和mp3的文件', 400, 4102)

    filename = secure_filename(upload_file.filename)
    ext = filename.rsplit('.', 1)[1].lower()

    content = upload_file.read()
    filepath_tmp = os.path.join(get_spdiar_tmp_dir(), '{}.{}'.format(diar_uuid, ext))
    logger.info(u'上传开始')
    with open(filepath_tmp, 'ab+') as fp:
        fp.write(content)
    logger.info(u'上传结束')

    magic_type = magic.from_file(filepath_tmp, mime=True)
    if magic_type.split('/')[0] != 'audio':
        raise APIException(u'非法文件类型，只接收MIME的audio类型，真实类型为{}'.format(magic_type), 400, 4103)

    # ALLOW_MIME_TYPE = ['audio/x-wav', 'audio/mpeg']
    ALLOW_MIME_TYPE = ['audio/x-wav', ]
    if magic_type not in ALLOW_MIME_TYPE:
        raise APIException(u'非法文件类型，只接收wav或mp3类型，真实类型为{}'.format(magic_type), 400, 4104)
    real_ext = 'wav'
    filepath = os.path.join(get_spdiar_tmp_dir(), '{}.{}'.format(diar_uuid, real_ext))
    if ext != 'wav':
        shutil.move(filepath_tmp, filepath)

    logger.info(u'合法文件: {}'.format(filepath))

    ### 进行分离和识别
    wav_property = do_diar_recog(diar_uuid, filepath)

    return ResultSuccess(msg=u'上传、人声分离、识别成功', data={'diar_uuid': diar_uuid, 'diar_recog': wav_property})


@api.route('/demo-upload-test', methods=['GET'])
def spdiar_demo_upload_test():
    # print json.dumps(wav_property, ensure_ascii=False, indent=4)
    diar_uuid = '2074721c5984489082b16b07c18e61fb'

    wav_property = {
        "77151cb5a63b45dfb6afc3d34cb011f4": {
            "channels": 1,
            "duration_seconds": 38.23,
            "file_path": "/home/user/hezw/work_py/online_label_api_dev/tmp/speech_diarization/e7ac678107fd47618626befc8f3e7077-piece/77151cb5a63b45dfb6afc3d34cb011f4.wav",
            "is_main_speaker": True,
            "is_recognized": True,
            "recog_path": "/home/user/hezw/work_py/online_label_api_dev/tmp/speech_diarization/e7ac678107fd47618626befc8f3e7077-piece/77151cb5a63b45dfb6afc3d34cb011f4_16000.wav",
            "recog_text": "你好\n现在进行。\n录音测试开始测试证人证言是案件审理中，法院认定事实准确，适用法律公正，裁判的重要证据之一，但在审判实践中，一些证人对出庭作证的严肃性认识不足、证言出现反复。\n矛盾作伪证假证等也有出现对此法庭一般采取的是排除证据效力，对行为人当庭。\n训诫话、批评、教育享有严厉制裁、测试结束。",
            "sample_rate": 8000,
            "sample_width": 2,
            "score_main_speaker": 0.0,
            "task_id": "cd0cdcbfeb1a11e9a8441d56e2de3ad6",
            "volume_dBFS": -25.906836938393255,
            "volume_rms": 1660
        }
    }

    add_score_by_col(wav_property, "volume_rms", 20)
    add_score_by_col(wav_property, "duration_seconds", 20)
    # return Success(msg=u'功能测试')
    return ResultSuccess(msg=u'功能测试', data={'diar_uuid': diar_uuid, 'diar_recog': wav_property})

# 开发测试用
@api.route('/inner-demo', methods=['POST'])
def spdiar_inner_demo():

    # print json.dumps(wav_property, ensure_ascii=False, indent=4)
    diar_uuid = '2074721c5984489082b16b07c18e61fb'

    wav_property = {
            "77151cb5a63b45dfb6afc3d34cb011f4": {
                "channels": 1,
                "duration_seconds": 38.23,
                "file_path": "/home/user/hezw/work_py/online_label_api_dev/tmp/speech_diarization/e7ac678107fd47618626befc8f3e7077-piece/77151cb5a63b45dfb6afc3d34cb011f4.wav",
                "is_main_speaker": True,
                "is_recognized": True,
                "recog_path": "/home/user/hezw/work_py/online_label_api_dev/tmp/speech_diarization/e7ac678107fd47618626befc8f3e7077-piece/77151cb5a63b45dfb6afc3d34cb011f4_16000.wav",
                "recog_text": "你好\n现在进行。\n录音测试开始测试证人证言是案件审理中，法院认定事实准确，适用法律公正，裁判的重要证据之一，但在审判实践中，一些证人对出庭作证的严肃性认识不足、证言出现反复。\n矛盾作伪证假证等也有出现对此法庭一般采取的是排除证据效力，对行为人当庭。\n训诫话、批评、教育享有严厉制裁、测试结束。",
                "sample_rate": 8000,
                "sample_width": 2,
                "score_main_speaker": 0.0,
                "task_id": "cd0cdcbfeb1a11e9a8441d56e2de3ad6",
                "volume_dBFS": -25.906836938393255,
                "volume_rms": 1660
            }
        }

    add_score_by_col(wav_property, "volume_rms", 20)
    add_score_by_col(wav_property, "duration_seconds", 20)
    # return Success(msg=u'功能测试')
    return ResultSuccess(msg=u'功能测试', data={'diar_uuid': diar_uuid, 'diar_recog': wav_property})


def allowed_file(filename):
    # ALLOW_FILE_EXT = ['wav', 'mp3']
    ALLOW_FILE_EXT = ['wav', ]
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOW_FILE_EXT


def do_diar_recog(diar_uuid, filepath):
    # 1、执行分离
    do_speech_diar(diar_uuid, filepath)

    # 2、获取分离后音频存放的路径
    diar_res_json = os.path.join(get_spdiar_tmp_dir(), '{}.json'.format(diar_uuid))
    if not os.path.exists(diar_res_json):
        raise APIException(u'人声分离结果丢失', 510, 5102)

    with codecs.open(diar_res_json, encoding='utf8') as f:
        diar_res = json.load(f)

    piece_file_path = os.path.abspath(diar_res['piece_file_path'])
    # print piece_file_path

    # ### 分离音频计算属性：音量，长度等
    # 1、音量
    # 2、frame数
    # 3、声纹score或其他
    # 4、根据识别音频的采样率，转换成对应的采样率，以便识别
    wav_property = defaultdict(dict)
    ng_sample_rate = get_ng_sample_rate(is_running=True)
    for root, dirs, files in os.walk(piece_file_path):
        for wav_file in files:
            wav_full_path = os.path.join(root, wav_file)
            sound = AudioSegment.from_file(wav_full_path, "wav")
            wav_key = os.path.splitext(wav_file)[0]
            wav_property[wav_key]['is_main_speaker'] = False
            wav_property[wav_key]['score_main_speaker'] = 0.0
            wav_property[wav_key]['is_recognized'] = False
            wav_property[wav_key]['file_path'] = wav_full_path
            wav_property[wav_key]['channels'] = sound.channels
            sample_rate = sound.frame_rate
            wav_property[wav_key]['sample_rate'] = sample_rate
            wav_property[wav_key]['volume_dBFS'] = sound.dBFS
            wav_property[wav_key]['volume_rms'] = sound.rms
            wav_property[wav_key]['sample_width'] = sound.sample_width
            wav_property[wav_key]['duration_seconds'] = sound.duration_seconds

            if sample_rate == ng_sample_rate:
                wav_property[wav_key]['recog_path'] = wav_property[wav_key]['file_path']
            else:
                # sample_rate transfer
                recog_path = os.path.join(root, '{}_{}.wav'.format(wav_key, ng_sample_rate))
                if not os.path.exists(recog_path):
                    is_transfer_succ = change_sample_rate(wav_full_path, recog_path, ng_sample_rate)
                    if not is_transfer_succ:
                        recog_path = wav_full_path  # 如果sample_rate转换失败，则用回源文件识别
                wav_property[wav_key]['recog_path'] = recog_path

    # ### 音频识别
    for wav_key, wav_info in wav_property.items():
        task_id = FileTransRestful(file_path=wav_info['recog_path'], protocol='file').register_file_flow()
        wav_property[wav_key]['task_id'] = task_id

    task_id_dict = defaultdict(str)
    for wav_key, wav_info in wav_property.items():
        task_id = wav_property[wav_key]['task_id']
        task_id_dict[task_id] = wav_key

    check_queue = task_id_dict.keys()
    succ_task, fail_task, non_valid_task = FileTransRestful.wait_for_finished(check_queue)

    logger.info("succ_task: {}".format(succ_task))
    logger.info("fail_task: {}".format(fail_task))
    logger.info("non_valid_task: {}".format(non_valid_task))

    for task_id in task_id_dict.keys():
        wav_key = task_id_dict[task_id]
        recog_path = wav_property[wav_key]['recog_path']
        tmp_path = FileTransRestful.get_tmp_file_path(task_id)
        if os.path.exists(tmp_path):
            shutil.move(tmp_path, recog_path)
            logger.info(u'文件复原：{} --> {}'.format(tmp_path, recog_path))

    for task_id in succ_task:
        wav_key = task_id_dict[task_id]
        recog_res = FileTransRestful.get_redis_result(task_id).get('sentences', [])
        recog_res_sorted = sorted(recog_res, key=lambda k: k['begin_time'])
        # wav_property[wav_key]['recog_res'] = recog_res_sorted
        wav_property[wav_key]['recog_text'] = '\n'.join([k['text'] for k in recog_res_sorted])
        wav_property[wav_key]['is_recognized'] = True
    # print json.dumps(wav_property, ensure_ascii=False, indent=4)

    # ### 根据上述属性，角色slot
    # 计算score
    if len(wav_property) > 0:
        add_score_by_col(wav_property, "volume_rms", 20)
        add_score_by_col(wav_property, "duration_seconds", 20)

    if len(wav_property) > 0:
        main_speaker = max({k: int(v['score_main_speaker']) for k, v in wav_property.items()}.items(),
                           key=lambda x: x[1])
        wav_key = main_speaker[0]
        wav_property[wav_key]['is_main_speaker'] = True

    counter_main_speaker = 0
    counter_other = 0
    for wav_key, wav_info in wav_property.items():
        if wav_property[wav_key]['is_main_speaker']:
            wav_property[wav_key]['out_file'] = 'main_speaker_{}.wav'.format(str(counter_main_speaker).zfill(2))
            counter_main_speaker += 1
        else:
            wav_property[wav_key]['out_file'] = 'other_speaker_{}.wav'.format(str(counter_other).zfill(2))
            counter_other += 1



    # ### 保存分离音频的识别结果，用于GET方法
    # 1、debug结果
    diar_recog_json = os.path.join(get_spdiar_tmp_dir(), '{}-recognition.json'.format(diar_uuid))
    # logger.debug(json.dumps(wav_property, ensure_ascii=False, indent=2))
    with codecs.open(diar_recog_json, mode='wb', encoding='utf8') as f:
        json.dump(wav_property, f, ensure_ascii=False, encoding='utf8', indent=2)

    # 2、短结果
    simple_key_list = ['recog_text', 'duration_seconds', 'is_main_speaker']
    wav_property_simple = defaultdict(dict)
    for wav_key, wav_info in wav_property.items():
        for simple_key in simple_key_list:
            wav_property_simple[wav_key][simple_key] = wav_info[simple_key]
        wav_property_simple[wav_key]['out_file'] = os.path.basename(wav_info['out_file'])

    diar_recog_simple_json = os.path.join(get_spdiar_tmp_dir(), '{}-recog.json'.format(diar_uuid))
    with codecs.open(diar_recog_simple_json, mode='wb', encoding='utf8') as f:
        json.dump(wav_property_simple, f, ensure_ascii=False, encoding='utf8', indent=2)

    zip_file_list = [(diar_recog_simple_json, os.path.basename(diar_recog_simple_json)), ]
    for wav_key, wav_info in wav_property.items():
        zip_file_list.append((wav_info['file_path'], wav_info['out_file']))

    zippath = os.path.join(get_spdiar_tmp_dir(), '{}.zip'.format(diar_uuid))

    with zipfile.ZipFile(zippath, 'w', zipfile.ZIP_DEFLATED) as fzip:
        for z_f, z_out_f in zip_file_list:
            fzip.write(z_f, z_out_f)

    return wav_property


def do_speech_diar(diar_uuid, wav_path):
    # 1。人声分离小工具执行配置
    plugins_cfg = os.path.join(get_cfg_dir(), 'plugins_diar.yaml')
    # print plugins_cfg
    with codecs.open(plugins_cfg, 'r', encoding='utf-8') as f:
        plugins_cfg_dict = yaml.safe_load(f.read())
    diar_cfg = plugins_cfg_dict.get('PLUGINS').get('SPEECH_DIARIZATION')
    diar_tool = os.path.join(diar_cfg['PLUGIN_PATH'], 'dia-client.jar')
    jre_exe = os.path.join(diar_cfg['JRE_HOME'], 'bin/java')

    sound = AudioSegment.from_file(wav_path, "wav")
    sample_rate = sound.frame_rate
    print 'sample_rate:', sample_rate
    if sample_rate == 16000:
        wav_filename = os.path.basename(wav_path)
        wav_filedir = os.path.dirname(wav_path)
        new_wav_path = os.path.join(wav_filedir, '_8000'.join(os.path.splitext(wav_filename)))
        print new_wav_path
        change_sample_rate(wav_path, new_wav_path, 8000)

        if os.path.exists(new_wav_path):
            wav_path = new_wav_path
            sample_rate = 8000


    # ../jre1.8.0_221/bin/java -Djavax.net.debug=all -Djava.ext.dirs=libs:$JAVA_HOME/jre/lib/ext -Ddia.uuid=ffff9 -Ddia.wavFile=./1300501-short.wav -jar dia-client.jar
    has_jre = check_jre(jre_exe)
    if not has_jre:
        raise APIException(u'jre配置有误', 510, 5100)

    java_libs = [
        '{}/libs'.format(diar_cfg['PLUGIN_PATH']),
        '{}/lib/ext'.format(diar_cfg['JRE_HOME']),
    ]

    parameters = []
    parameters.append('-Ddia.uuid={}'.format(diar_uuid))
    parameters.append('-Ddia.sampleRate={}'.format(sample_rate))
    parameters.append('-Ddia.wavFile={}'.format(wav_path))
    parameters.append('-Ddia.resDir={}'.format(get_spdiar_tmp_dir()))

    command = '{jre} -Djava.ext.dirs={java_libs} {parameters} -jar {diar_tool}'.format(
        jre=jre_exe,
        java_libs=':'.join(java_libs),
        parameters=' '.join(parameters),
        diar_tool=diar_tool
    )

    # print command


    import subprocess as sp
    child = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    streamdata = child.communicate()
    return_code = child.returncode
    if return_code != 0:
        logger.error(streamdata[1])
        # return False
        raise APIException(u'人声分离工具出错', 510, 5101)

    logger.info(u'人声分离成功')


def change_sample_rate(in_, out_, sample_rate):
    ffmpeg_tool = os.path.join(get_bin_dir(), 'ffmpeg')
    command = '{handle_tool} -i {input_file} -y -ar {sample_rate} {output_file}'.format(
        handle_tool=ffmpeg_tool,
        input_file=in_,
        sample_rate=sample_rate,
        output_file=out_
    )

    # print command

    import subprocess as sp
    child = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    streamdata = child.communicate()
    return_code = child.returncode
    if return_code != 0:
        logger.error(streamdata[1])
        return False
    return True


def add_score_by_col(data_dict, inner_key, max_score):
    # for k, v in data_dict.items():
    #     print k, v[inner_key]
    # w_compare = [k:v["volumn_rms"] ]
    score_input = sorted({k: int(v[inner_key]) for k, v in data_dict.items()}.items(), key=lambda x: x[1], reverse=True)

    cols = zip(*score_input)
    normal_cols = [cols[0]]
    for j in cols[1:]:
        max_j = max(j)
        min_j = min(j)
        if max_j == min_j:
            normal_cols.append(tuple(float(max_score) for k in j))
        else:
            normal_cols.append(tuple((k - min_j) * max_score / float(max_j - min_j) for k in j))

    score_normalize_list = zip(*normal_cols)
    # print score_normalize_list
    for wav_key, v in score_normalize_list:
        # print data_dict[wav_key]['score_main_speaker']
        data_dict[wav_key]['score_main_speaker'] += v


def get_spdiar_tmp_dir():
    return os.path.join(get_tmp_dir(), 'speech_diarization')


def check_jre(jre_exe):
    # ../jre1.8.0_221/bin/java -Djavax.net.debug=all -Djava.ext.dirs=libs:$JAVA_HOME/jre/lib/ext -Ddia.uuid=ffff9 -Ddia.wavFile=./1300501-short.wav -jar dia-client.jar
    command = '{jre} -version'.format(jre=jre_exe)
    # print command

    import subprocess as sp
    child = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    streamdata = child.communicate()
    return_code = child.returncode
    if return_code != 0:
        logger.error(streamdata[1])
        return False
        # raise APIException(u'jre配置有误', 510, 5100)

    # print streamdata[1]
    return True
