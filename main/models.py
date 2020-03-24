# coding:utf-8
import datetime
from main import db
from werkzeug.security import generate_password_hash, check_password_hash


# 用户
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 昵称
    pwd = db.Column(db.String(100))  # 密码，加密
    email = db.Column(db.String(100), unique=True)  # 邮箱
    phone = db.Column(db.String(11), unique=True)  # 手机号码
    info = db.Column(db.Text)  # 个性简介
    face = db.Column(db.String(255), unique=True)  # 头像
    add_time = db.Column(db.DateTime, index=True, default=datetime.datetime.now)  # 添加时间
    uuid = db.Column(db.String(255), unique=True)  # 唯一标识符
    userlogs = db.relationship('UserLog', backref='user')  # 会员日志外键关系关联，backref互相绑定user表

    def __repr__(self):  # 查询的时候返回
        return "<User %r>" % self.name

    # 加上property装饰器后，会把函数变为属性，户属性名即为函数名
    @property
    def password(self):
        """读取属性的函数行为"""
        # print(user.password)  读取属性时被调用
        # 函数的返回值会作为属性值
        # return "xxx"
        raise AttributeError("这个属性只能设置,不能读取")

    # 使用这个装饰器,对应设置属性操作
    @password.setter
    def password(self, value):
        """
        设置属性  user.password = "xxx"
        :param value: 设置属性时候的数据 value就是"xxxx", 原始明文密码
        :return:
        """
        self.pwd = generate_password_hash(value)

    # def generate_password_hash(self, origin_password):
    #     """对密码进行加密"""
    #     self.password_hash = generate_password_hash(origin_password)

    def check_password(self, passwd):
        """
        检验密码正确性
        :param passwd:  用户登录时填写的原始密码
        :return:  如果正确返回True 否则返回 False
        """
        return check_password_hash(self.pwd, passwd)


# 登录日志
class UserLog(db.Model):
    __tablename__ = "userlog"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属会员
    ip = db.Column(db.String(100))  # 登录IP
    add_time = db.Column(db.DateTime, index=True, default=datetime.datetime.now)  # 登录时间

    def __repr__(self):
        return "<Userlog %r>" % self.id