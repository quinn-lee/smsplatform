# coding: utf-8

from main import celery, app
from main.libs.smsapi import SmsApi
from main import db
from main.models import User


@celery.task
def handle_apply(user):
    """发送短信的异步任务"""
    """测试"""
    print("tasksaaaaaaaaaaaaaaaaaaaaa")
    with app.app_context():
        user.password = "1qaz2wsx"
        db.session.add(user)
        db.session.commit()
        print(user.pwd)
