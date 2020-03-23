# coding: utf-8


class Config(object):
    """配置信息"""
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = "postgresql://smsp:fuyuan@localhost:5432/smsp_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

