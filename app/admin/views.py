#coding:utf-8

from . import admin

@admin.route("/")
def index():
    return "<h1>this admin</h1>"
