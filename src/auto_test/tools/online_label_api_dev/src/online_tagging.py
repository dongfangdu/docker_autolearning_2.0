# -*- coding: utf-8 -*-
import logging

import os
from werkzeug.exceptions import HTTPException

from app import create_app
from app.libs.error import APIException
from app.libs.error_code import ServerError
from app.libs.qpaginate.exceptions import PageNotAnInteger, EmptyPage

# 使用哪种配置环境
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
logger = logging.getLogger(__name__)


@app.errorhandler(Exception)
def framework_error(e):
    if isinstance(e, APIException):
        return e
    if isinstance(e, PageNotAnInteger):
        return APIException(u'分页参数错误，参数不是Integer类型', 400, 4001)
    if isinstance(e, EmptyPage):
        return APIException(u'分页参数错误，当前页没有数据', 400, 4001)
    if isinstance(e, HTTPException):
        code = e.code
        msg = u'未定义Http异常: ' + e.description
        error_code = 5008
        return APIException(msg, code, error_code)
    else:
        # TODO
        # Log处理
        if not app.config['DEBUG']:
            logger.error(e)
            return ServerError()
        else:
            raise e

if __name__ == '__main__':
    # app.run(host=app.config.get('HOST'), port=app.config.get('PORT'))
    app.run(host=app.config.get('HOST'), port=app.config.get('PORT'))
