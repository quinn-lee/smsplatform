# coding:utf-8


from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from main import app, db, scheduler
from flask_script import Shell
from main.models import User, UserLog, MessageLog, MessageTask, TaskQueue
from main.libs.smsapi import SmsApi
from getpass import getpass
import json


# 初始化管理器
manager = Manager(app)

migrate = Migrate(app, db)
# 添加 db 命令，并与 MigrateCommand 绑定
manager.add_command('db', MigrateCommand)


def make_shell_context():
    return dict(app=app, db=db, User=User, UserLog=UserLog, SmsApi=SmsApi, MessageTask=MessageTask,
                MessageLog=MessageLog, TaskQueue=TaskQueue, scheduler=scheduler)


manager.add_command('shell', Shell(make_context=make_shell_context))


@manager.command
def adduser():
    name = input('Username> ')
    email = input('Email> ')
    phone = input('Phone> ')
    input_password = getpass('Password> ')
    new = User(name=name, email=email, phone=phone, password=input_password)
    db.session.add(new)
    db.session.commit()
    print("new user <%s> created" % name)


@manager.command
def test_api():
    apply_no = input('Apply_no> ')
    data = {
        "apply_no": apply_no,
        "org_code": "tzyy",
        "org_name": "汀州医院",
        "send_class": "产前检查",
        "send_name": "钟",
        "msgcontent": "【汀州医院】哈哈哈",
        "send_date": "2020-04-09 12:45:06",
        "receivers": [
            {
                "patient_id": "111111111111111111111111",
                "org_form_no": "1111111111111111111111111111111111111",
                "name": "test{}".format(i),
                "age": 30,
                "id_no": "35082119860409045X",
                "mobile": "13305915399"
            } for i in range(2)
        ]
    }
    from main.utils.commons import token_post
    res = token_post("127.0.0.1", "8100", "/api/v1.0/sms/send", json.dumps(data))
    print(res)

@manager.command
def test_captcha():
    apply_no = input('Apply_no> ')
    data = {
        "apply_no": apply_no,
        "org_code": "tzyy",
        "org_name": "汀州医院",
        "msg_content": "【无限云】验证码4444",
        "phone_num": "13917050484",

    }
    from main.utils.commons import token_post
    res = token_post("127.0.0.1", "8081", "/api/v1.0/sms/captcha", json.dumps(data))
    print(res)


if __name__ == "__main__":
    manager.run()
