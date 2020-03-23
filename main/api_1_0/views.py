# coding:utf-8
from . import api
from main import models


@api.route("/")
def index():
    return "<h1>this api_1_0</h1>"