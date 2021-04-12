# -*- coding: utf-8 -*-
from flask import json

from app.libs.error import APIException


class Success(APIException):
    code = 200
    msg = u'请求成功'
    error_code = 2000


class CreateSuccess(Success):
    code = 201
    error_code = 2010
    msg = u'资源创建成功'

    def __init__(self, msg=None, data=None):
        if msg:
            self.msg = msg
        if data:
            self.data = data
        super(CreateSuccess, self).__init__(msg, code=200)

    def get_body(self, environ=None):
        body = dict(
            msg=self.msg,
            data=self.data,
            error_code=self.error_code

        )
        text = json.dumps(body)
        return text


class DeleteSuccess(Success):
    code = 200
    error_code = 2001
    msg = u'删除成功'


class EditSuccess(Success):
    code = 200
    error_code = 2002
    msg = u'修改成功'


class ResultSuccess(Success):
    code = 200
    error_code = 2000
    msg = u'资源说明'

    def __init__(self, msg=None, data=None):
        if msg:
            self.msg = msg
        self.data = data
        super(ResultSuccess, self).__init__(msg, code=200)

    def get_body(self, environ=None):
        body = dict(
            msg=self.msg,
            data=self.data,
            error_code=self.error_code

        )
        text = json.dumps(body)
        return text


class PageResultSuccess(Success):
    code = 200
    error_code = 2000
    msg = u'分页资源说明'

    def __init__(self, msg=None, data=None, page=None):
        if msg:
            self.msg = msg
        self.data = data
        self.page = page
        super(PageResultSuccess, self).__init__(msg, code=200)

    def get_body(self, environ=None):
        body = dict(
            msg=self.msg,
            data=self.data,
            page=self.page,
            error_code=self.error_code

        )
        text = json.dumps(body)
        return text


class ServerError(APIException):
    code = 500
    msg = u'服务器出现未知错误，请联系运维人员'
    error_code = 5009


class ClientTypeError(APIException):
    code = 400
    msg = (
        u'非法登录方式'
    )
    error_code = 4009


class ParameterException(APIException):
    code = 400
    msg = u'非法请求参数'
    error_code = 4000


class NotFound(APIException):
    code = 404
    msg = u'服务资源未找到'
    error_code = 4040


class AuthFailed(APIException):
    code = 401
    msg = u'权限认证失败'
    error_code = 4010


class Forbidden(APIException):
    code = 403
    error_code = 4030
    msg = u'没有权限访问该资源'


class ParserSuccess(Success):
    code = 201
    error_code = 2010
    msg = u'解析成功'

    def __init__(self, msg=None, data=None):
        if msg:
            self.msg = msg
        if data:
            self.data = data
        super(ParserSuccess, self).__init__(msg, code=200)

    def get_body(self, environ=None):
        body = dict(
            msg=self.msg,
            data=self.data,
            error_code=self.error_code

        )
        text = json.dumps(body)
        return text


class DownloadSuccess(Success):
        code = 201
        error_code = 2010
        msg = u'数据下载成功'

        def __init__(self, msg=None, data=None):
            if msg:
                self.msg = msg
            if data:
                self.data = data
            super(DownloadSuccess, self).__init__(msg, code=200)

        def get_body(self, environ=None):
            body = dict(
                msg=self.msg,
                data=self.data,
                error_code=self.error_code

            )
            text = json.dumps(body)
            return text
