# -*- coding: utf-8 -*-
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature

from app.libs.enums import ClientTypeEnum
from app.libs.error_code import AuthFailed, ResultSuccess, CreateSuccess
from app.libs.redprint import Redprint
from app.libs.token_auth import generate_auth_token
from app.models.v1.sysmng import User
from app.validators.forms_v1 import ClientForm, TokenForm, LoginForm

api = Redprint('token')


@api.route('', methods=['POST'])
def get_token():
    form = LoginForm().validate_for_api()
    identity = User.verify(form.account.data, form.secret.data)

    # gen Token
    expiration = current_app.config['TOKEN_EXPIRATION']
    token = generate_auth_token(identity['uid'], identity['ac_type'], identity['scope'], expiration)
    t = {
        'token': token.decode('ascii')
    }

    return CreateSuccess(msg=u'令牌生成', data=t)


def get_token_high_level():
    form = ClientForm().validate_for_api()
    promise = {
        ClientTypeEnum.USER_NICKNAME: User.verify
    }
    identity = promise[ClientTypeEnum(form.ac_type.data)](
        form.account.data,
        form.secret.data
    )

    # gen Token
    expiration = current_app.config['TOKEN_EXPIRATION']
    token = generate_auth_token(identity['uid'], form.ac_type.data, identity['scope'], expiration)
    t = {
        'token': token.decode('ascii'),
        'user_id': identity['uid']
    }

    return CreateSuccess(msg=u'令牌生成', data=t)


@api.route('/secret', methods=['POST'])
def get_token_info():
    form = TokenForm().validate_for_api()
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(form.token.data, return_header=True)
    except SignatureExpired:
        raise AuthFailed(msg=u'Token不合法', error_code=4011)
    except BadSignature:
        raise AuthFailed(msg=u'Token过期', error_code=4012)

    r = {
        'scope': data[0]['scope'],
        'create_at': data[1]['iat'],
        'expire_in': data[1]['exp'],
        'uid': data[0]['uid'],
    }

    return ResultSuccess(data=r)
