# -*- coding: utf-8 -*-
from flask import request, json
from werkzeug.exceptions import HTTPException

JSON_MIME_TYPE = 'application/json'


class APIException(HTTPException):
    code = 500
    msg = 'the default api server error, '
    error_code = 5008

    def __init__(self, msg=None, code=None, error_code=None, headers=None):
        if code:
            self.code = code
        if error_code:
            self.error_code = error_code
        if msg:
            self.msg = msg

        super(APIException, self).__init__(msg, None)

    def get_headers(self, environ=None):
        return [('Content-Type', JSON_MIME_TYPE)]

    def get_body(self, environ=None):
        body = dict(
            msg=self.msg,
            error_code=self.error_code,
            request=request.method + ' ' + self.get_url_no_param()
        )
        text = json.dumps(body)
        return text

    @staticmethod
    def get_url_no_param():
        full_path = str(request.full_path)
        main_path = full_path.split('?')
        return main_path[0]
