# coding:utf-8


from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from main import app, db
from flask_script import Shell
from main.models import User, UserLog
from main.libs.smsapi import SmsApi


# 初始化管理器
manager = Manager(app)

migrate = Migrate(app, db)
# 添加 db 命令，并与 MigrateCommand 绑定
manager.add_command('db', MigrateCommand)


def make_shell_context():
    return dict(app=app, db=db, User=User, UserLog=UserLog, SmsApi=SmsApi)


manager.add_command('shell', Shell(make_context=make_shell_context))


if __name__ == "__main__":
    manager.run()
