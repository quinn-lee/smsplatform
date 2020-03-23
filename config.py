# coding: utf-8


class Config(object):
    """配置信息"""
    SQLALCHEMY_DATABASE_URI = "postgresql://smsp:fuyuan@localhost:5432/smsp_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class DevelopmentConfig(Config):
    """开发环境配置信息"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置信息"""
    pass


environment_mapping = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}

