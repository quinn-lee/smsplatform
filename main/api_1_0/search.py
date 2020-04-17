# coding:utf-8
from . import api
from main import db
from main.models import MsgClass, MsgOrg, MessageLog
from flask import jsonify, request, current_app
from main.utils.response_code import RET
from sqlalchemy.sql import func
from main.utils.commons import Excel
import time


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
    if req_dict['action'] == 'search':  # 搜索
        return jsonify(errno="0", data=data, query=[req_dict])
    else:  # 导出
        file_name = 'statistics{}.xlsx'.format(str(int(round(time.time() * 1000))))
        file_path = 'main/static/excels/{}'.format(file_name)
        colums_name = ['医院代码', '医院名称', '短信类别', '短信状态', '数量']

        book = Excel(file_path)
        book.write_colume_name(colums_name)
        i = 1
        for row in res:
            book.write_content(i, row)
            i += 1
        book.close()
        return jsonify(errno="0", data=[{'filename': file_name}])


