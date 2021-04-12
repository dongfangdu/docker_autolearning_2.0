# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, SmallInteger
from werkzeug.security import generate_password_hash, check_password_hash

from app.libs.error_code import AuthFailed
from app.models.base import BaseV1, db_v1


class User(BaseV1):
    id = Column(Integer, primary_key=True)
    account = Column(String(24), unique=True, nullable=False)
    _password = Column('password', String(100))

    nickname = Column(String(24), unique=True)
    telephone = Column(String(15))
    ac_type = Column(SmallInteger, default=100)
    ac_status = Column(SmallInteger, default=11)
    rid = Column(Integer)
    proj_id = Column(Integer)

    def keys(self):
        return ['id', 'account', 'nickname', 'telephone', 'ac_type', 'ac_status', 'rid', 'proj_id', 'create_time']

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw):
        self._password = generate_password_hash(raw)

    # @staticmethod
    # def register_by_email(nickname, account, secret):
    #     with db.auto_commit():
    #         user = User()
    #         user.account = nickname
    #         user.email = account
    #         user.password = secret
    #         db.session.add(user)

    @staticmethod
    def verify(account, password):
        user, role = db_v1.session.query(User, Role).filter_by(account=account, rid=Role.id).first_or_4010(msg='认证用户不存在',
                                                                                                           error_code=4011)
        if not user.check_password(password):
            raise AuthFailed(msg='认证密码不正确', error_code=4012)
        return {'uid': user.id, 'nickname': user.nickname, 'ac_type': user.ac_type, 'scope': role.rcode}

    def check_password(self, raw):
        if not self._password:
            return False
        return check_password_hash(self._password, raw)


class Role(BaseV1):
    id = Column(Integer, primary_key=True)
    rname = Column(String(24), unique=True, nullable=False)
    rcode = Column(String(24), unique=True, nullable=False)
    rdesc = Column(String(24), default='')

    def keys(self):
        return ['id', 'rname', 'rcode', 'rdesc']


class RolePermissionMap(BaseV1):
    id = Column(Integer, primary_key=True)
    rid = Column(Integer, nullable=False)
    pid = Column(Integer, nullable=False)

    def keys(self):
        return ['id', 'rid', 'pid']


class Permission(BaseV1):
    id = Column(Integer, primary_key=True)
    pname = Column(String(24), unique=True, nullable=False)
    pcategory = Column(SmallInteger, default=1)
    presource = Column(String(200))

    def keys(self):
        return ['id', 'pname', 'pcategory', 'presource', 'create_time']


class Region(BaseV1):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    parent_id = Column(Integer, nullable=False)

    def keys(self):
        return ['id', 'name', 'parent_id']
