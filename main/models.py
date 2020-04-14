# coding:utf-8
import datetime
import time
import hashlib
from main import db, auth
from flask import current_app, g
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy import Sequence


# 用户
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(100), unique=True)  # 昵称
    pwd = db.Column(db.String(100))  # 密码，加密
    email = db.Column(db.String(100), unique=True)  # 邮箱
    phone = db.Column(db.String(11), unique=True)  # 手机号码
    info = db.Column(db.Text)  # 个性简介
    face = db.Column(db.String(255), unique=True)  # 头像
    add_time = db.Column(db.DateTime, index=True, default=datetime.datetime.now)  # 添加时间
    uuid = db.Column(db.String(255), unique=True)  # 唯一标识符
    userlogs = db.relationship('UserLog', backref='user')  # 用户日志外键关系关联，backref互相绑定user表
    api_key = db.Column(db.String(255), unique=True)  # 接口认证私钥
    messagetasks = db.relationship('MessageTask', backref='user')  # 用户短信批量申请外键关系关联，backref互相绑定user表
    messagelogs = db.relationship('MessageLog', backref='user')  # 用户短信日志外键关系关联，backref互相绑定user表

    def __init__(self, name, password, email, phone):
        res = db.session.query(func.max(User.uuid).label('uuid')).one()
        self.uuid = '20001' if res.uuid is None else str(int(res.uuid) + 1)  # 用户编码
        self.api_key = hashlib.md5((str(int(round(time.time() * 1000))) + self.uuid).encode("utf-8")).hexdigest()  # 私钥
        self.name = name
        self.password = password
        self.email = email
        self.phone = phone

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

    def check_password(self, passwd):
        """
        检验密码正确性
        :param passwd:  用户登录时填写的原始密码
        :return:  如果正确返回True 否则返回 False
        """
        return check_password_hash(self.pwd, passwd)

    # 回调函数，验证 token 是否合法
    @staticmethod
    @auth.verify_token
    def verify_token(token):
        uuid, timestamp, md5_code = token.split("&")
        print(uuid)
        print(timestamp)
        print(md5_code)
        if int((time.time() * 1000 - int(timestamp)) / 1000 / 60) > 5:
            g.auth_msg = "权限验证失败，时间戳与当前时间差大于5分钟"
            return False
        user = User.query.filter_by(uuid=uuid).first()
        if user is not None:
            print(hashlib.md5((str(uuid) + str(timestamp) + user.api_key).encode("utf-8")).hexdigest())
            if hashlib.md5((str(uuid) + str(timestamp) + user.api_key).encode("utf-8")).hexdigest() == md5_code:
                g.current_user = user
                return True
            else:
                g.auth_msg = "权限验证失败，私钥错误"
                return False
        g.auth_msg = "权限验证失败，用户编码错误"
        return False


# 登录日志
class UserLog(db.Model):
    __tablename__ = "userlog"
    id = db.Column(db.Integer, primary_key=True)  # 主键
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属用户
    ip = db.Column(db.String(100))  # 登录IP
    add_time = db.Column(db.DateTime, index=True, default=datetime.datetime.now)  # 登录时间

    def __repr__(self):
        return "<Userlog %r>" % self.id


# 短信批量发送申请任务
class MessageTask(db.Model):
    __tablename__ = "messagetask"
    id = db.Column(db.Integer, primary_key=True)  # 主键
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属用户
    task_no = db.Column(db.String(32), index=True)  # 任务号
    apply_no = db.Column(db.String(256))  # 请求编号
    org_code = db.Column(db.String(256))  # 医院代码
    org_name = db.Column(db.String(256))  # 医院名称
    send_class = db.Column(db.String(128))  # 短信类别
    send_name = db.Column(db.String(256))  # 发送人
    msgcontent = db.Column(db.Text)  # 短信内容
    send_date = db.Column(db.DateTime)  # 发送日期
    receivers = db.Column(JSONB)  # 短信接收人
    status = db.Column(db.String(128))  # 任务状态
    messagelogs = db.relationship('MessageLog', backref='messagetask')  # 用户短信日志外键关系关联，backref互相绑定messagetask表
    created_at = db.Column(db.DateTime, index=True, default=datetime.datetime.now)  # 创建时间
    updated_at = db.Column(db.DateTime, index=True, default=datetime.datetime.now)  # 修改时间

    def __init__(self, user_id, apply_no, org_code, org_name, send_class, send_name, msgcontent, send_date, receivers):
        self.user_id = user_id
        self.apply_no = apply_no
        self.org_code = org_code
        self.org_name = org_name
        self.send_class = send_class
        self.send_name = send_name
        self.msgcontent = msgcontent
        self.send_date = send_date
        self.receivers = receivers
        sequence = Sequence('some_no_seq')
        seq = db.session.execute(sequence)
        self.task_no = "T{}{}".format(str(int(round(time.time() * 1000))), seq)
        self.status = "已申请，等待发送处理"


# 短信日志
class MessageLog(db.Model):
    __tablename__ = "messagelog"
    id = db.Column(db.Integer, primary_key=True)  # 主键
    message_id = db.Column(db.String(50))  # 短信唯一码，用于短信发送请求
    callback_id = db.Column(db.String(50))  # 短信回调唯一码，用于短信回调请求
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属用户
    messagetask_id = db.Column(db.Integer, db.ForeignKey('messagetask.id'))  # 所属任务
    task_no = db.Column(db.String(32), index=True)  # 任务号
    apply_no = db.Column(db.String(256))  # 请求编号
    org_code = db.Column(db.String(256), index=True)  # 医院代码
    org_name = db.Column(db.String(256))  # 医院名称
    send_class = db.Column(db.String(128), index=True)  # 短信类别
    send_name = db.Column(db.String(256))  # 发送人
    msgcontent = db.Column(db.Text)  # 短信内容
    send_date = db.Column(db.DateTime)  # 发送日期
    patient_id = db.Column(db.String(256))  # 病人唯一标识
    org_form_no = db.Column(db.String(256))  # 记录表单编号
    name = db.Column(db.String(256))  # 姓名
    age = db.Column(db.Integer)  # 年龄
    id_no = db.Column(db.String(128))  # 身份证号
    mobile = db.Column(db.String(128))  # 手机号码
    mt_code = db.Column(db.String(30))  # 电信返回的状态码
    mt_msg = db.Column(db.String(256))  # 电信返回的状态描述
    mt_taskid = db.Column(db.String(50))  # 电信返回的任务ID
    mtq_code = db.Column(db.String(128))  # 查询接口返回的状态码
    mtq_msg = db.Column(db.String(256))  # 查询接口返回的状态描述
    mtq_time = db.Column(db.DateTime)  # 查询接口返回的接收时间
    created_at = db.Column(db.DateTime, index=True, default=datetime.datetime.now)  # 创建时间
    updated_at = db.Column(db.DateTime, index=True, default=datetime.datetime.now)  # 修改时间


# 批处理任务表
class TaskQueue(db.Model):
    __tablename__ = "taskqueue"
    id = db.Column(db.Integer, primary_key=True)  # 主键
    queue_no = db.Column(db.String(32), index=True)  # 任务号 or 短信请求唯一号 or 短信回调唯一号
    task_type = db.Column(db.String(32))  # 任务类型 apply|send|callback
    status = db.Column(db.String(32))  # 任务状态
    run_batch = db.Column(db.String(32))  # 处理批次
    last_handle_time = db.Column(db.DateTime)  # 最近一次处理时间
    last_handle_result = db.Column(db.String(256))  # 最近一次处理结果
    try_amount = db.Column(db.Integer, default=20)  # 可重试次数
    tried_amount = db.Column(db.Integer)  # 已重试次数
    start_handle_time = db.Column(db.DateTime)  # 第一次处理时间
    created_at = db.Column(db.DateTime, index=True, default=datetime.datetime.now)  # 创建时间
    updated_at = db.Column(db.DateTime, index=True, default=datetime.datetime.now)  # 修改时间
