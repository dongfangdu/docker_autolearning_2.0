# -*- coding: utf-8 -*-
from wtforms import StringField, IntegerField, FieldList, DateTimeField, DecimalField
from wtforms import ValidationError
from wtforms.validators import DataRequired, length, Email, Regexp

from app.libs.enums import ClientTypeEnum, LabelTaskStatusEnum
from app.models.v2.web.label import LabelProject, LabelTask
from app.models.v1.sysmng import User, Role, Permission
from app.validators.base import BaseForm as Form


# 公共Form
class IDForm(Form):
    """ 用于id检查 """
    id = IntegerField(validators=[DataRequired()])


# Token相关
class TokenForm(Form):
    token = StringField(validators=[DataRequired()])


# 角色相关
class RoleForm(Form):
    rname = StringField(validators=[DataRequired(), length(max=24)])
    rcode = StringField(validators=[DataRequired(), length(max=24)])
    rdesc = StringField(validators=[length(max=200)])

    def validate_rname(self, value):
        if Role.query.filter_by(rname=value.data).first():
            raise ValidationError(message=u'角色名称必须唯一')

    def validate_rcode(self, value):
        if Role.query.filter_by(rcode=value.data).first():
            raise ValidationError(message=u'角色编码必须唯一')


class RoleEditForm(Form):
    rname = StringField(validators=[length(max=24)])
    rcode = StringField(validators=[length(max=24)])
    rdesc = StringField(validators=[length(max=200)])


class UserEditForm(Form):
    nickname = StringField(validators=[length(max=24)])
    telephone = StringField(validators=[length(max=15)])


class UserMapEditForm(Form):
    uid = IntegerField(validators=[DataRequired()])
    proj_ids = FieldList(StringField())


class RolePermissionMapForm(Form):
    rid = IntegerField(validators=[DataRequired()])
    pid_list = FieldList(IntegerField())

    def validate_rid(self, value):
        if not Role.query.filter_by(id=value.data).first():
            raise ValidationError(message=u"非法角色ID")

    # def validate_pid_list(self, value):
    #     id_list = list(value.data)
    #     id_list_q = Permission.query.with_entities(Permission.id).filter(Permission.id.in_(id_list)).all()
    #
    #     # 验证阻拦
    #     id_list_error = [id for id in id_list if id not in [id_q for id_q, in id_list_q]]
    #     if len(id_list_error) != 0:
    #         raise ValidationError(message="含有非法权限ID：{}".format(', '.join(str(v) for v in id_list_error)))


class LabelResultEditForm(Form):
    task_id = StringField()
    request_id = StringField(validators=[DataRequired()])

    label_text = StringField()
    label_tag_person = StringField()
    label_tag_accent = StringField()
    label_tag_gender = IntegerField()


class LabelResultSearchForm(Form):
    label_status = IntegerField()


class LabelTaskIDForm(Form):
    task_id = IntegerField(validators=[DataRequired()])

    def validate_task_id(self, value):
        if not LabelTask.query.filter_by(id=value.data).first():
            raise ValidationError(message=u"非法任务ID")


class LabelProjectIDForm(Form):
    proj_id = IntegerField(validators=[DataRequired()])

    def validate_proj_id(self, value):
        if not LabelProject.query.filter_by(id=value.data).first():
            raise ValidationError(message=u"非法项目ID")


class UtteranceCalcForm(Form):
    is_calc_all = IntegerField()
    req_id_list = FieldList(IntegerField())


class UtteranceCalcWERForm(Form):
    req_id_list = FieldList(IntegerField())


class LabelProjectUtteranceMapForm(Form):
    proj_id = IntegerField(validators=[DataRequired()])
    req_id_list = FieldList(IntegerField())

    def validate_proj_id(self, value):
        if not LabelProject.query.filter_by(id=value.data).first():
            raise ValidationError(message=u"非法项目ID")


class LabelTaskUtteranceMapForm(Form):
    task_id = IntegerField(validators=[DataRequired()])
    req_id_list = FieldList(IntegerField())

    def validate_task_id(self, value):
        if not LabelTask.query.filter_by(id=value.data).first():
            raise ValidationError(message=u"非法任务ID")


class PermissionForm(Form):
    pname = StringField(validators=[DataRequired(), length(max=24)])
    presource = StringField(validators=[DataRequired(), length(max=200)])

    def validate_pname(self, value):
        if Permission.query.filter_by(pname=value.data).first():
            raise ValidationError(message=u'权限名称必须唯一')


class PermissionEditForm(Form):
    pname = StringField(validators=[length(max=24)])
    presource = StringField(validators=[length(max=200)])


class LoginForm(Form):
    account = StringField(validators=[DataRequired(message=u'账号：不允许为空'), length(min=2, max=24)])
    secret = StringField(validators=[DataRequired(message=u'密码：不允许为空'),
                                     Regexp(r'^[A-Za-z0-9_*&$#@]{6,22}', message=u'密码：只允许6位至22位字母数字以及_*&$#@')])


class ClientForm(Form):
    account = StringField(validators=[DataRequired(message=u'不允许为空'), length(min=2, max=24)])
    secret = StringField()
    ac_type = IntegerField(validators=[DataRequired()])

    def validate_ac_type(self, value):
        try:
            client = ClientTypeEnum(value.data)
        except ValueError as e:
            raise e
        self.ac_type.data = client


class UserNicknameForm(Form):
    account = StringField(validators=[DataRequired(), length(min=2, max=24)])
    secret = StringField(validators=[DataRequired(), Regexp(r'^[A-Za-z0-9_*&$#@]{6,22}')])
    nickname = StringField(validators=[DataRequired(), length(max=24)])
    ac_type = 100
    rid = IntegerField(validators=[DataRequired()])
    proj_ids = FieldList(StringField())

    def validate_account(self, value):
        if User.query.filter_by(account=value.data, with_deleted=True).first():
            raise ValidationError(message=u"该用户已经存在")

    def validate_rid(self, value):
        if not Role.query.filter_by(id=value.data).first():
            raise ValidationError(message=u"非法角色ID")


class UserEmailForm(ClientForm):
    account = StringField(validators=[Email(message='invalidate email')])
    secret = StringField(validators=[DataRequired(), Regexp(r'^[A-Za-z0-9_*&$#@]{6,22}')])
    nickname = StringField(validators=[DataRequired(), length(min=2, max=22)])

    def validate_account(self, value):
        if User.query.filter_by(email=value.data).first():
            raise ValidationError()


class PasswordForm(Form):
    secret = StringField(validators=[DataRequired(message=u'密码：不允许为空'),
                                     Regexp(r'^[A-Za-z0-9_*&$#@]{6,22}', message=u'密码：只允许6位至22位字母数字以及_*&$#@')])


class UserSearchForm(Form):
    nickname = StringField()
    rid = IntegerField()
    proj_id = IntegerField()


class LabelProjectForm(Form):
    proj_name = StringField(validators=[DataRequired(message=u'项目名称：不允许为空')])
    region_ids = FieldList(IntegerField(), validators=[DataRequired(message=u'区域：不允许为空')])
    proj_desc = StringField()
    proj_difficulty = DecimalField()

    def validate_proj_name(self, value):
        if LabelProject.query.filter_by(proj_name=value.data).first():
            raise ValidationError(message=u"该项目名称已经存在")

    # def validate_region_id(self, value):
    #     if not Region.query.filter_by(id=value.data).first():
    #         raise ValidationError(message=u"非法区域ID")


class LabelProjectSearchForm(Form):
    proj_code = StringField()
    proj_name = StringField()
    region_ids = FieldList(StringField())


class LabelProjectEditForm(Form):
    proj_name = StringField()
    proj_desc = StringField()
    region_ids = FieldList(IntegerField())
    proj_difficulty = DecimalField()

    # def validate_region_id(self, value):
    #     if value.data and not Region.query.filter_by(id=value.data).first():
    #         raise ValidationError(message="非法地区ID")


class LabelTaskForm(Form):
    task_name = StringField(validators=[DataRequired(message=u'任务名称：不允许为空')])
    proj_id = IntegerField(validators=[DataRequired(message=u'项目：不允许为空')])
    tagger_uids = FieldList(IntegerField())

    def validate_proj_id(self, value):
        if not LabelProject.query.filter_by(id=value.data).first():
            raise ValidationError(message=u"非法项目ID")

    # def validate_tagger_uid(self, value):
    #     if value.data and not User.query.filter_by(id=value.data).first():
    #         raise ValidationError(message=u"非法用户ID")


class LabelTaskAddSVForm(Form):
    task_id = IntegerField()
    task_name = StringField()


class LabelTaskAuditForm(Form):
    audit_status = IntegerField()


class LabelTaskActiveForm(Form):
    active_status = IntegerField()


class LabelTaskEditForm(Form):
    task_name = StringField()
    # proj_id = IntegerField()
    finish_time = IntegerField()
    tagger_uids = FieldList(IntegerField())
    task_status = IntegerField()

    def validate_tagger_uid(self, value):
        if value.data and not User.query.filter_by(id=value.data).first():
            raise ValidationError(message=u"非法用户ID")

    def validate_task_status(self, value):
        if value.data and value.data not in [v.value for k, v in enumerate(LabelTaskStatusEnum)]:
            raise ValidationError(message=u"非法任务状态编码")


class LabelStatSearchForm(Form):
    proj_code = StringField()
    proj_name = StringField()
    tagger_account = StringField()
    label_time_left = IntegerField()
    label_time_right = IntegerField()
    task_status = IntegerField()
    label_status = IntegerField()


class LabelTaskSearchForm(Form):
    create_time_left = IntegerField()
    create_time_right = IntegerField()
    proj_code = StringField()
    task_code = StringField()
    tagger_name = StringField()
    task_status = IntegerField()

    # audit_status = IntegerField()

    # def validate_tagging_status(self, value):
    #     if value.data and value.data not in [0, 1, 2]:
    #         raise ValidationError(message="非法任务标注状态编码")
    #
    # def validate_audit_status(self, value):
    #     if value.data and value.data not in [0, 1, 2]:
    #         raise ValidationError(message="非法任务审核状态编码")

    def validate_task_status(self, value):
        if value.data and value.data not in [0, 1, 2, 3, 4]:
            raise ValidationError(message=u"非法任务状态编码")


class UtteranceSearchForm(Form):
    stt_time_left = DateTimeField()
    stt_time_right = DateTimeField()
    proj_code = StringField()
    task_code = StringField()
    label_status = IntegerField()
    ord_num_begin = IntegerField()
    ord_num_end = IntegerField()

    # def validate_tagging_status(self, value):
    #     if value.data and value.data not in [0, 1, 2]:
    #         raise ValidationError(message="非法任务标注状态编码")


class UtteranceRefSearchForm(Form):
    stt_time_left = IntegerField()
    stt_time_right = IntegerField()
    ord_num_begin = IntegerField()
    ord_num_end = IntegerField()


class UtteranceSetRefForm(Form):
    stt_time_left = IntegerField(validators=[DataRequired()])
    stt_time_right = IntegerField(validators=[DataRequired()])


class UtteranceIDListForm(Form):
    req_id_list = FieldList(StringField())

class UtteranceSVSearchForm(Form):
    task_code = StringField()
    court_id = StringField()
    case_id = StringField()
    role_id = StringField()
    label_time_left = IntegerField()
    label_time_right = IntegerField()
    label_status = IntegerField()


class StatisticSearchForm(Form):
    task_code = StringField()
    court_id = StringField()
    case_id = StringField()
    role_id = StringField()
    label_time_left = IntegerField()
    label_time_right = IntegerField()


class BgprocParseSearchForm(Form):
    req_status = IntegerField()
    label_time_left = IntegerField()
    label_time_right = IntegerField()
