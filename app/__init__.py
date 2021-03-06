#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@文件        :app.py
@说明        :
@时间        :2020/08/05 20:08:36
@作者        :Leo
@版本        :1.0
"""

import os

from flask import Flask as _Flask
from flask_cors import CORS
from .libs.decimal_encoder import JSONEncoder
from app.libs.helper import Helper
from app.register.executor import register_Executor
from app.register.wsIO import register_SocketIO

from .config.setting import config
from .register.authInterceptor import TokenFilter, register_error_headers
from .register.blueprints import register_blueprints
from .register.database import register_plugin
from .register.header import register_headers
from .register.logger import register_configure_logging

from app.register.scheduler import scheduler


class Flask(_Flask):
    # 替换Flask中原有的json_encoder方法。
    json_encoder = JSONEncoder


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")
    app = Flask("app", template_folder="templates")
    # jinja模版中添加convert_timestamp过滤器
    # app.jinja_env = Environment(extensions=["jinja2.ext.loopcontrols"])
    app.jinja_env.filters["convert_timestamp"] = Helper.convert_timestamp
    app.jinja_env.filters["convert_json"] = Helper.convert_json
    # 查询时会显示原始SQL语句
    # app.config['SQLALCHEMY_ECHO'] = True
    # 支持跨域
    CORS(app, supports_credentials=True)
    app.config.from_object(config[config_name])
    app.secret_key = app.config["SESSION_KEY"]
    # 本地加载
    # app.config['API_DOC_CDN'] = False
    # 禁用文档页面
    # app.config['API_DOC_ENABLE'] = False
    # 需要显示文档的 Api
    app.config["API_DOC_MEMBER"] = ["api", "platform"]
    # 需要排除的 RESTful Api 文档
    app.config["RESTFUL_API_DOC_EXCLUDE"] = []
    register_blueprints(app)
    register_headers(app)
    register_plugin(app)
    register_error_headers(app)
    TokenFilter(app)
    register_Executor(app)
    register_SocketIO(app)
    register_configure_logging(app)
    # 启动apscheduler服务
    scheduler.init_app(app)
    scheduler.start()
    return app
