#coding:utf-8
from . import interface

@interface.route("/")
def index():
    return "<h1>this interface</h1>"