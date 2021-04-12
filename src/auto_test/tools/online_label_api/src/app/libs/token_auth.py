# -*- coding: utf-8 -*-
from collections import namedtuple

from flask import current_app, g, request
from flask_httpauth import HTTPBasicAuth
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired

from app.libs.error_code import AuthFailed, Forbidden
from app.libs.scope import is_in_scope

auth = HTTPBasicAuth()
UserInToken = namedtuple('UserInToken', ['uid', 'ac_type', 'scope'])
UserInSession = namedtuple('UserInSession', ['uid', 'ac_type', 'scope', 'is_logout'])


@auth.verify_password
def verify_password(token, password):
    # token
    user_info = verify_auth_token(token)
    if not user_info:
        return False
    else:
        g.user = user_info
        return True


def verify_auth_token(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except BadSignature:
        raise AuthFailed(msg=u'Token不合法', error_code=4011)
    except SignatureExpired:
        raise AuthFailed(msg=u'Token过期', error_code=4012)

    uid = data['uid']
    ac_type = data['ac_type']
    scope = data['scope']
    allow = is_in_scope(scope, request.endpoint)
    if not allow:
        raise Forbidden()
    return UserInSession(uid, ac_type, scope, False)


def generate_auth_token(uid, ac_type, scope=None, expiration=7200):
    s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
    return s.dumps(UserInToken(uid, ac_type, scope)._asdict())
