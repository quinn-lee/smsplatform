#coding:utf8
from flask import Blueprint

interface = Blueprint("interface", __name__)

import app.interface.views
