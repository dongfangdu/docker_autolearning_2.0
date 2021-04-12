# -*- coding: utf-8 -*-
import logging

from app.libs.error_code import ResultSuccess
from app.libs.redprint import Redprint
from app.models.base import db_v2
from app.models.v2.web.sysmgr import User
from app.models.v1.sysmng import User as OldUser

api = Redprint('demo')
logger = logging.getLogger(__name__)


@api.route('/log-test')
def log_test():
    logger.info("this is info")
    logger.debug("this is debug")
    logger.warning("this is warning")
    logger.error("this is error")
    logger.critical("this is critical")

    return ResultSuccess(msg='用户列表', data={})


@api.route('/test', methods=['POST'])
def user_test():
    q = db_v2.session.query(User).order_by(User.insert_time.desc()).filter_by().all()
    q2 = db_v2.session.query(OldUser).order_by(OldUser.create_time.desc()).filter_by().all()

    return ResultSuccess(msg='用户列表', data={'len': len(q), 'len2': len(q2)})


# @socketio.on('request_for_response',namespace='/api/testnamespace')
# def give_response(data):
#     value = data.get('param')
#     print value
#
#
# @socketio.on('connect', namespace='/mytest')
# def test_connect():
#     print('mytest Client connected')
#
#
# @socketio.on('disconnect', namespace='/mytest')
# def test_disconnect():
#     print('mytest Client disconnected')
#
#
# @socketio.on('start', namespace='/mytest')
# def start():
#     # print val
#     for i in xrange(1, 10):
#         emit('recv', i)
#         time.sleep(1)
#
#     emit('call_disconnect')
#
# @socketio.on('connect', namespace='/mytest2')
# def test_connect():
#     print('mytest2 Client connected')
#
#
# @socketio.on('disconnect', namespace='/mytest2')
# def test_disconnect():
#     print('mytest2 Client disconnected')
#
#
# @socketio.on('start', namespace='/mytest2')
# def start():
#     # print val
#     for i in xrange(20, 30):
#         emit('recv', i)
#         time.sleep(1)

# thread = None
# thread_lock = Lock()
#
# def background_thread(user_cnt):
#     """Example of how to send server generated events to clients."""
#     while True:
#         socketio.sleep(5)
#
#         socketio.emit('user_response', {'data_length': user_cnt}, namespace='/websocket/user_refresh')
#
#
# @socketio.on('connect', namespace='/websocket/user_refresh')
# def connect():
#     """ 服务端自动发送通信请求 """
#     global thread
#     with thread_lock:
#         users = User.query.all()
#         user_cnt = len(users)
#
#         if thread is None:
#             thread = socketio.start_background_task(background_thread, (user_cnt, ))
#     emit('server_response', {'data': '试图连接客户端！'})
#
#
# @socketio.on('connect_event', namespace='/websocket/user_refresh')
# def refresh_message(message):
#     """ 服务端接受客户端发送的通信请求 """
#
#     emit('server_response', {'data': message['data']})
#
# @socketio.on('connection')
# def refresh_message(message):
#     """ 服务端接受客户端发送的通信请求 """
#
#     emit('news', {'data': message['data']})
#
# @socketio.on('my event')
# def handle_my_custom_namespace_event():
#     print('received json: ')
