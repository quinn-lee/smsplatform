# coding:utf-8
from . import api
from main import models, auth, db
from flask import current_app, request, jsonify, g
from main.utils.response_code import RET
from main.models import MessageTask, TaskQueue
import datetime


@api.route("/sms/send", methods=["GET", "POST"])
@auth.login_required
def send():
    current_app.logger.info(str(request.headers))
    # current_app.logger.info(request.get_data())
    try:
        req_dict = request.get_json()
        current_app.logger.info("request_json: {}".format(req_dict))
    except Exception as e:
        current_app.logger.info(e)
        return jsonify(code=RET.NOTJSON, msg="参数非Json格式")
    if req_dict is None:
        return jsonify(code=RET.NOTJSON, msg="参数非Json格式")
    # 参数验证
    if (req_dict.get('apply_no') is None or req_dict.get('org_code') is None or req_dict.get('org_name') is None
            or req_dict.get('send_class') is None or req_dict.get('send_name') is None
            or req_dict.get('msgcontent') is None or req_dict.get('receivers') is None):
        return jsonify(code=RET.PARAMERR, msg="参数错误，请检查必填项")
    if (req_dict.get('apply_no') == "" or req_dict.get('org_code') == "" or req_dict.get('org_name') == ""
            or req_dict.get('send_class') == "" or req_dict.get('send_name') == ""
            or req_dict.get('msgcontent') == "" or req_dict.get('receivers') == []):
        return jsonify(code=RET.PARAMERR, msg="参数错误，请检查必填项")
    if type(req_dict.get('receivers')) != list:
        return jsonify(code=RET.PARAMERR, msg="参数错误，receivers必须是一个数组")
    if len(req_dict.get('receivers')) > 12000:
        return jsonify(code=RET.PARAMERR, msg="参数错误，receivers个数不能超过12000个")
    current_app.logger.info(g.current_user.name)
    if req_dict.get('send_date') is None:
        send_date = None
    else:
        try:
            send_date = datetime.datetime.strptime(req_dict.get('send_date'), "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            send_date = None
    mt = MessageTask(user_id=g.current_user.id, apply_no=req_dict.get('apply_no'), org_code=req_dict.get('org_code'),
                     org_name=req_dict.get('org_name'), send_class=req_dict.get('send_class'),
                     send_name=req_dict.get('send_name'), msgcontent=req_dict.get('msgcontent'),
                     send_date=send_date, receivers=req_dict.get('receivers'))
    try:
        db.session.add(mt)
        db.session.commit()
        tq = TaskQueue(queue_no=mt.task_no, task_type='apply', status='init', try_amount=20, tried_amount=0)
        db.session.add(tq)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmag="数据库异常")

    return jsonify(code=RET.OK, msg="成功", taskid=mt.task_no)


@auth.error_handler
def auth_error():
    return jsonify(code="1", msg="权限验证失败"), 403
