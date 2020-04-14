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
import time
from flask_httpauth import HTTPTokenAuth
import asyncio
from sqlalchemy import Sequence
import datetime
import os


db = SQLAlchemy()

celery = Celery("main", broker="redis://127.0.0.1:6379", include=['main.tasks.task_his'])

auth = HTTPTokenAuth(scheme='Token')

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
        if os.path.exists('shutdown.txt'):
            scheduler.shutdown()
        current_app.logger.info("aaaaaaaa")
        smsapi = SmsApi("47.111.38.50", 8081, "350122", "736b8235fc654cdd979dd0865972b700")
        result = smsapi.query()
        current_app.logger.info(result)


def handle_apply():
    """HIS短信批量请求处理定时任务"""
    with app.app_context():
        if os.path.exists('shutdown.txt'):
            scheduler.shutdown()
        from main.models import TaskQueue, MessageLog, MessageTask
        ts = time.strftime("%Y%m%d%H%M%S", time.localtime())
        tqs = TaskQueue.query.filter(TaskQueue.status.in_(['init', 'fail']), TaskQueue.run_batch == None,
                                     TaskQueue.task_type == 'apply').limit(5)
        if tqs.count() == 0:
            current_app.logger.info("no tqs to handle!!!")
            return
        for tq in tqs:
            tq.run_batch = ts
            tq.start_handle_time = datetime.datetime.now()
            tq.last_handle_time = datetime.datetime.now()
            db.session.add(tq)
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            return

        async def process_tq(tq):
            try:
                mt = MessageTask.query.filter_by(task_no=tq.queue_no).first()
                for i in range(0, len(mt.receivers), 1000):
                    mobiles = mt.receivers[i: i + 1000]
                    sequence = Sequence('some_no_seq')
                    seq = db.session.execute(sequence)
                    message_id = "M{}{}".format(str(int(round(time.time() * 1000))), seq)
                    new_tq = TaskQueue(queue_no=message_id, task_type='send', status='init', try_amount=20,
                                       tried_amount=0)
                    db.session.add(new_tq)
                    for mobile in mobiles:
                        age = None
                        try:
                            age = int(mobile.get('age'))
                        except:
                            age = None

                        ml = MessageLog(message_id=message_id, user_id=mt.user_id, messagetask_id=mt.id,
                                        task_no=mt.task_no, apply_no=mt.apply_no, org_code=mt.org_code,
                                        org_name=mt.org_name, send_class=mt.send_class, send_name=mt.send_name,
                                        msgcontent=mt.msgcontent, send_date=mt.send_date,
                                        patient_id=mobile.get('patient_id'), org_form_no=mobile.get('org_form_no'),
                                        name=mobile.get('name'), age=age, id_no=mobile.get('id_no'),
                                        mobile=mobile.get('mobile'))
                        db.session.add(ml)
                tq.status = 'succ'
                tq.last_handle_result = None
                db.session.add(tq)
                try:
                    db.session.commit()
                except Exception as exp:
                    print("rollback1")
                    db.session.rollback()
                    raise exp
                return "{} success".format(tq.queue_no)
            except Exception as error:
                tq.tried_amount = tq.tried_amount + 1
                if tq.tried_amount > tq.try_amount:
                    tq.status = 'fail_limited'
                else:
                    tq.status = 'fail'
                tq.run_batch = None
                tq.last_handle_result = str(error)[0:100]
                tq.last_handle_time = datetime.datetime.now()
                db.session.add(tq)
                try:
                    db.session.commit()
                except Exception:
                    db.session.rollback()
                # current_app.logger.info(error)
                # print("{} error-{}".format(tq.queue_no, error))
                return "{} error-{}".format(tq.queue_no, error)
        tqs = TaskQueue.query.filter(TaskQueue.status.in_(['init', 'fail']), TaskQueue.run_batch == ts,
                                     TaskQueue.task_type == 'apply')
        print(tqs.count())
        if tqs.count() == 0:
            current_app.logger.info("no tqs to handle!!!")
            return
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        loop = asyncio.get_event_loop()
        try:
            tasks = [asyncio.ensure_future(process_tq(tq)) for tq in tqs]
            print(len(tasks))

            loop.run_until_complete(asyncio.wait(tasks))

            for task in tasks:
                print('Task ret: ', task.result())
        except Exception as e:
            for tq in tqs:
                tq.run_batch = None
                tq.last_handle_result = str(e)[0:100]
                tq.last_handle_time = datetime.datetime.now()
                db.session.add(tq)
            try:
                db.session.commit()
            except Exception as e:
                print(e)
                db.session.rollback()


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

    # 定时任务相关配置
    app.config.update(
        {
            'JOBS': [
                {
                    'id': 'handle_apply',
                    'func': handle_apply,
                    "trigger": "interval",
                    "seconds": 5
                },
                {
                    'id': 'report_query',
                    'func': report_query,
                    "trigger": "interval",
                    "seconds": 10
                }
            ],
            'SCHEDULER_TIMEZONE': 'Asia/Shanghai',
            'SCHEDULER_API_ENABLED': True,
            'SCHEDULER_JOB_DEFAULTS': {'max_instances': 3}
        }
    )

    scheduler.init_app(app)

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

