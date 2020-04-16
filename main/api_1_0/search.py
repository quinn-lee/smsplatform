# coding:utf-8
from . import api
from main import db
from main.models import MsgClass, MsgOrg, MessageLog
from flask import jsonify, request, current_app
from main.utils.response_code import RET
from sqlalchemy.sql import func


@api.route("/msg_orgs", methods=["GET"])
def msg_orgs():
    mos = MsgOrg.query.all()
    data = [{'org_value': mo.org_code, 'org_name': mo.org_name} for mo in mos]
    data.insert(0, {'org_value': '', 'org_name': ''})
    return jsonify(errno='0', data=data)


@api.route("/msg_classes", methods=["GET"])
def msg_classes():
    mcs = MsgClass.query.all()
    data = [{'class_name': mc.send_class} for mc in mcs]
    data.insert(0, {'class_name': ''})
    return jsonify(errno='0', data=data)


@api.route("/msg_statistics", methods=["POST"])
def msg_statistics():
    try:
        current_app.logger.info("request_json: {}".format(request.get_json()))
        req_dict = request.get_json()
    except Exception as e:
        current_app.logger.info(e)
        return jsonify(errno=RET.NOTJSON, errmsg="参数非Json格式")

    res = db.session.query(MessageLog.org_code, MessageLog.org_name, MessageLog.send_class, MessageLog.msg_status,
                           func.count(MessageLog.id))
    res = res.group_by(MessageLog.org_code, MessageLog.org_name, MessageLog.send_class, MessageLog.msg_status)
    data = [{'org_code': r[0], 'org_name': r[1], 'send_class': r[2], 'msg_status': r[3], 'count': r[4]} for r in res]
    print(data)
    return jsonify(errno="0", data=data)
