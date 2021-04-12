# -*- coding: utf-8 -*-
from datetime import date
from decimal import Decimal

from flask import Flask as _Flask
from flask.json import JSONEncoder as _JSONEncoder

from .libs.error_code import ServerError


class JSONEncoder(_JSONEncoder):
    def default(self, o):
        if hasattr(o, 'keys') and hasattr(o, '__getitem__'):
            return dict(o)
        if isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        if isinstance(o, Decimal):
            return float(o)
        raise ServerError()


class Flask(_Flask):
    json_encoder = JSONEncoder



