# coding:utf-8
from . import api
from main import models
from flask import current_app, request
import time


@api.route("/")
def index():
    current_app.logger.error("error")
    current_app.logger.warning("warning")
    current_app.logger.info("info")
    current_app.logger.debug("debug")
    from main.models import User
    user = User.query.filter_by(email="lifuyuan33@hotmail.com").first()
    from main.tasks.task_his import handle_apply
    handle_apply.delay(user)
    return "<h1>this api_1_0</h1>"


@api.route('/test')
def maintest():
    return 'hello world'


@api.route('/sleep')
def mainsleep():
    time.sleep(10)
    return 'wake up'


@api.route('/report/push', methods=["POST"])
def report_push():
    try:
        req_dict = request.get_json()
        print("len: ", len(req_dict))
    except Exception as e:
        current_app.logger.info(e)
        return "ERROR"
    return "SUCCESS"

