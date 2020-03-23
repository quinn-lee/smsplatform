# coding:utf8
from flask import Blueprint

api = Blueprint("api_1_0", __name__)

import main.api_1_0.views
