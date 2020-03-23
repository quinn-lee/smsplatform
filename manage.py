# coding:utf-8


from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from main import create_app, db

app = create_app("development")
# 初始化管理器
manager = Manager(app)

migrate = Migrate(app, db)
# 添加 db 命令，并与 MigrateCommand 绑定
manager.add_command('db', MigrateCommand)
if __name__ == "__main__":
    manager.run()
