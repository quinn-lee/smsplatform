# coding:utf-8
from . import api
from main import models, auth
from flask import current_app, request, jsonify


@api.route("/sms/send", methods=["GET", "POST"])
@auth.login_required
def send():
    current_app.logger.info(str(request.headers))
    current_app.logger.info(request.get_data())
    current_app.logger.info(request.get_json())
    return jsonify(code="0", msg="成功", taskid="aaaaaa")


@auth.error_handler
def auth_error():
    return jsonify(code="1", msg="权限验证失败"), 403
