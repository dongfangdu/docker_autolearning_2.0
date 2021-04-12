# -*- coding: utf-8 -*-
import os

from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired

from app.libs.error_code import ParameterException
from app.validators.base import BaseForm as Form


# 公共Form
class IDForm(Form):
    """ 用于id检查 """
    id = IntegerField(validators=[DataRequired()])



class PathForm(Form):
    filepath = StringField()

    def validate_filepath(self, value):
        if not os.path.exists(value.data):
            raise ParameterException(msg=u'该路径的文件不存在')


class SentenceForm(Form):
    sentence = StringField()

