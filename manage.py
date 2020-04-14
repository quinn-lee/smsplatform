# coding:utf-8


from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from main import app, db
from flask_script import Shell
from main.models import User, UserLog, MessageLog, MessageTask, TaskQueue
from main.libs.smsapi import SmsApi
from getpass import getpass
import http.client
import time
import hashlib
import json


# 初始化管理器
manager = Manager(app)

migrate = Migrate(app, db)
# 添加 db 命令，并与 MigrateCommand 绑定
manager.add_command('db', MigrateCommand)


def make_shell_context():
    return dict(app=app, db=db, User=User, UserLog=UserLog, SmsApi=SmsApi, MessageTask=MessageTask,
                MessageLog=MessageLog, TaskQueue=TaskQueue)


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


def _post(method, data):
    conn = None
    try:
        user = User.query.first()
        ts = str(int(round(time.time() * 1000)))
        md5_code = hashlib.md5((str(user.uuid) + str(ts) + str(user.api_key)).encode("utf-8")).hexdigest()
        print(md5_code)
        headers = {"Content-type": "application/json",
                   "Authorization": "Token {}&{}&{}".format(user.uuid, ts, md5_code)}
        conn = http.client.HTTPConnection("127.0.0.1", "5000", timeout=200)
        conn.request("POST", method, data, headers)
        response = conn.getresponse()
        retmsg = response.read().decode("utf8")
        conn.close()
        return retmsg
    except Exception as e:
        print(e)
    finally:
        if conn:
            conn.close()


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
        "send_date": "",
        "receivers": [
            {
                "patient_id": "",
                "org_form_no": "",
                "name": "test{}".format(i),
                "age": "",
                "id_no": "",
                "mobile": "13917050484"
            } for i in range(11111)
        ]
    }
    res = _post("/api/v1.0/sms/send", json.dumps(data))
    print(res)


if __name__ == "__main__":
    manager.run()
