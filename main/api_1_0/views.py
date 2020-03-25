# coding:utf-8
from . import api
from main import models
from flask import current_app
import time


@api.route("/")
def index():
    current_app.logger.error("error")
    current_app.logger.warning("warning")
    current_app.logger.info("info")
    current_app.logger.debug("debug")
    return "<h1>this api_1_0</h1>"


@api.route('/test')
def maintest():
    return 'hello world'


@api.route('/sleep')
def mainsleep():
    time.sleep(10)
    return 'wake up'
