# coding: utf-8

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import environment_mapping
from flask_wtf import CSRFProtect
import logging
from logging.handlers import RotatingFileHandler
from main.utils.commons import ReConverter
from celery import Celery
from main.libs.smsapi import SmsApi
from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from flask import current_app


db = SQLAlchemy()

celery = Celery("main", broker="redis://127.0.0.1:6379", include=['main.tasks.task_his'])

scheduler = APScheduler(BackgroundScheduler(timezone="Asia/Shanghai"))

# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG)  # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式               日志等级     文件名        行数        日志信息
formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s', "%Y%m%d-%H:%M:%S")
# 为日志记录器设置格式
file_log_handler.setFormatter(formatter)
# 为全局日志工具对象添加日志记录器
logging.getLogger().addHandler(file_log_handler)


def report_query():
    """发送短信的定时查询任务"""
    """测试"""
    with app.app_context():
        current_app.logger.info("aaaaaaaa")
        smsapi = SmsApi("47.111.38.50", 8081, "350122", "736b8235fc654cdd979dd0865972b700")
        result = smsapi.query()
        current_app.logger.info(result)
        from main.models import User
        user = User.query.filter_by(email="lifuyuan33@hotmail.com").first()
        current_app.logger.info(user.pwd)


# 工厂方法
def create_app(environment):
    """
    创建flask的应用对象
    #param environment: string 配置环境名称 ("development", "production")
    #return:
    """
    app = Flask(__name__)
    app.config.from_object(environment_mapping.get(environment))

    db.init_app(app)

    app.config.update(
        {
            'JOBS': [
                {
                    'id': 'job1',
                    'func': report_query,
                    "trigger": "interval",
                    "seconds": 30
                }
            ],
            'SCHEDULER_TIMEZONE': 'Asia/Shanghai',
            'SCHEDULER_API_ENABLED': True,
        }
    )
    scheduler.init_app(app)
    scheduler.start()


    # csrf保护
    # CSRFProtect(app)

    # 为flask添加自定义的转换器
    app.url_map.converters["re"] = ReConverter

    # 注册蓝图
    from main.api_1_0 import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix="/api/v1.0")

    # 注册提供静态文件的蓝图
    from main import web_html
    app.register_blueprint(web_html.html)

    return app


app = create_app("development")

