# -*- coding: utf-8 -*-
from flask import request, current_app
from wtforms import Form, IntegerField, StringField
from wtforms.meta import DefaultMeta

from app.libs.error_code import ParameterException


class BindNameMeta(DefaultMeta):
    def bind_field(self, form, unbound_field, options):
        if 'custom_name' in unbound_field.kwargs:
            options['name'] = unbound_field.kwargs.pop('custom_name')
        return unbound_field.bind(form=form, **options)


class BaseForm(Form):
    Meta = BindNameMeta

    def __init__(self):
        data = request.json

        super(BaseForm, self).__init__(data=data)

    def validate_for_api(self):
        valid = super(BaseForm, self).validate()
        if not valid:
            raise ParameterException(msg=self.errors.values())
        return self


class SearchOrderForm(BaseForm):
    order_col = StringField()
    order_type = IntegerField()


class PageForm(BaseForm):
    page = IntegerField()
    limit = IntegerField()

    @staticmethod
    def fetch_page_param(page_form):
        cur_page = 1
        per_page = current_app.config['DEFAULT_LISTNUM_PER_PAGE']

        if page_form.page:
            cur_page = page_form.page.data

        if page_form.limit:
            per_page = page_form.limit.data

        return cur_page, per_page


class ColumnSortForm(BaseForm):
    column_name = StringField()
    column_order = StringField()

    @staticmethod
    def fetch_column_param(column_form):
        column_name = 'id'
        column_order = 'descending'

        if column_form.column_name.data:
            column_name = column_form.column_name.data

        if column_form.column_order.data:
            column_order = column_form.column_order.data

        return column_name, column_order
