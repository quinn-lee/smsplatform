# coding:utf-8
from . import api
from main import models, auth, db
from flask import current_app, request, jsonify, g
from main.utils.response_code import RET
from main.models import MessageTask, TaskQueue, MessageLog
from main.exceptions import ValidationException
from main.libs.smsv2api import Smsv2Api
import datetime
import xmltodict
import json
from sqlalchemy import Sequence
import time


@api.route("/report", methods=["POST"])
def report():
    try:
        current_app.logger.info(str(request.headers))
        current_app.logger.info("request_data: {}".format(request.get_data()))
        try:
            req_json = json.loads(json.dumps(xmltodict.parse(request.get_data())))
            current_app.logger.info("request_json: {}".format(req_json))
        except Exception as e:
            current_app.logger.info(e)
            raise ValidationException(code=RET.NOTXML, msg="参数非Xml格式")
        sequence = Sequence('some_no_seq')
        seq = db.session.execute(sequence)
        callback_id = "C{}{}".format(str(int(round(time.time() * 1000))), seq)
        new_tq = TaskQueue(queue_no=callback_id, task_type='callback', status='init', try_amount=20,
                           tried_amount=0)
        db.session.add(new_tq)
        mobiles_arr = []
        if type(req_json.get('Response').get('Report')) == dict:
            mobiles_arr = [req_json.get('Response').get('Report')]
        elif type(req_json.get('Response').get('Report')) == list:
            mobiles_arr = req_json.get('Response').get('Report')
        for message in mobiles_arr:
            mls = MessageLog.query.filter_by(mt_taskid=message.get('MsgID'), mobile=message.get('Mobile'))
            for ml in mls:
                curr_time = datetime.datetime.now()
                if message.get('Status') == 'DELIVRD':
                    ml.msg_status = 'success'
                else:
                    ml.msg_status = 'failure'
                ml.mtq_code = message.get('Status')
                ml.mtq_msg = message.get('Status')
                ml.mtq_time = curr_time
                ml.mtq_stime = curr_time.strftime("%Y%m%d%H%M%S")
                ml.callback_id = callback_id
                db.session.add(ml)

        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            raise ValidationException(code=RET.DBERR, msg="数据库异常")
        return RET.OK
    except ValidationException as e:
        return e.code
    except Exception as e:
        return RET.UNKOWNERR


@api.route("/sms/send", methods=["GET", "POST"])
@auth.login_required
def send():
    try:
        current_app.logger.info(str(request.headers))
        current_app.logger.info("request_data: {}".format(request.get_data()))
        try:
            req_dict = request.get_json()
            current_app.logger.info("request_json: {}".format(req_dict))
        except Exception as e:
            current_app.logger.info(e)
            raise ValidationException(code=RET.NOTJSON, msg="参数非Json格式")
        if req_dict is None:
            raise ValidationException(code=RET.NOTJSON, msg="参数非Json格式")
        # 参数验证
        if (req_dict.get('apply_no') is None or req_dict.get('org_code') is None or req_dict.get('org_name') is None
                or req_dict.get('send_class') is None or req_dict.get('send_name') is None
                or req_dict.get('msgcontent') is None or req_dict.get('receivers') is None):
            raise ValidationException(code=RET.PARAMERR, msg="参数错误，请检查必填项")
        if (req_dict.get('apply_no') == "" or req_dict.get('org_code') == "" or req_dict.get('org_name') == ""
                or req_dict.get('send_class') == "" or req_dict.get('send_name') == ""
                or req_dict.get('msgcontent') == "" or req_dict.get('receivers') == []):
            raise ValidationException(code=RET.PARAMERR, msg="参数错误，请检查必填项")
        if (str(req_dict.get('apply_no')).isspace() or str(req_dict.get('org_code')).isspace()
                or str(req_dict.get('org_name')).isspace() or str(req_dict.get('send_class')).isspace()
                or str(req_dict.get('send_name')).isspace() or str(req_dict.get('msgcontent')).isspace()):
            raise ValidationException(code=RET.PARAMERR, msg="参数错误，请检查必填项")
        if type(req_dict.get('receivers')) != list:
            raise ValidationException(code=RET.PARAMERR, msg="参数错误，receivers必须是一个数组")
        if len(req_dict.get('receivers')) > 12000:
            raise ValidationException(code=RET.PARAMERR, msg="参数错误，receivers个数不能超过12000个")
        r_names = list(map(lambda x: x.get('name'), req_dict.get('receivers')))
        r_mobiles = list(map(lambda x: x.get('mobile'), req_dict.get('receivers')))
        if r_names.count(None) > 0:
            current_app.logger.info('接收人姓名不能为空')
            raise ValidationException(code=RET.PARAMERR, msg="接收人姓名不能为空")
        if r_mobiles.count(None) > 0:
            current_app.logger.info('接收人手机号不能为空')
            raise ValidationException(code=RET.PARAMERR, msg="接收人手机号不能为空")
        s_names = [str(name).strip() for name in r_names]
        s_mobiles = [str(mobile).strip() for mobile in r_mobiles]
        if s_names.count('') > 0:
            current_app.logger.info('接收人姓名不能为空')
            raise ValidationException(code=RET.PARAMERR, msg="接收人姓名不能为空")
        if s_mobiles.count('') > 0:
            current_app.logger.info('接收人手机号不能为空')
            raise ValidationException(code=RET.PARAMERR, msg="接收人手机号不能为空")
        current_app.logger.info(g.current_user.name)
        if req_dict.get('send_date') is None:
            send_date = None
        else:
            try:
                send_date = datetime.datetime.strptime(req_dict.get('send_date'), "%Y-%m-%d %H:%M:%S")
            except Exception as e:
                send_date = None
        mt = MessageTask(user_id=g.current_user.id, apply_no=req_dict.get('apply_no'),
                         org_code=req_dict.get('org_code'), org_name=req_dict.get('org_name'),
                         send_class=req_dict.get('send_class'), send_name=req_dict.get('send_name'),
                         msgcontent=req_dict.get('msgcontent'), send_date=send_date,
                         receivers=req_dict.get('receivers'))

        tq = TaskQueue(queue_no=mt.task_no, task_type='apply', status='init', try_amount=20, tried_amount=0)
        db.session.add(mt)
        db.session.add(tq)

        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            raise ValidationException(code=RET.DBERR, msg="数据库异常")
        return jsonify(code=RET.OK, msg="成功", taskid=mt.task_no)
    except ValidationException as e:
        return jsonify(code=e.code, msg=e.msg)
    except Exception as e:
        return jsonify(code=RET.UNKOWNERR, msg=str(e))

@api.route("/sms/captcha", methods=["GET", "POST"])
@auth.login_required
def sms_captcha():
    try:
        current_app.logger.info(str(request.headers))
        current_app.logger.info("request_data: {}".format(request.get_data()))
        try:
            req_dict = request.get_json()
            current_app.logger.info("request_json: {}".format(req_dict))
        except Exception as e:
            current_app.logger.info(e)
            raise ValidationException(code=RET.NOTJSON, msg="参数非Json格式")
        if req_dict is None:
            raise ValidationException(code=RET.NOTJSON, msg="参数非Json格式")
        # 参数验证
        if (req_dict.get('apply_no') is None or req_dict.get('org_code') is None
                or req_dict.get('org_name') is None or req_dict.get('msg_content') is None
                or req_dict.get('phone_num') is None):
            raise ValidationException(code=RET.PARAMERR, msg="参数错误，请检查必填项")
        if (req_dict.get('apply_no') == "" or req_dict.get('org_code') == ""
                or req_dict.get('org_name') == "" or req_dict.get('msg_content') == ""
                or req_dict.get('phone_num') == ""):
            raise ValidationException(code=RET.PARAMERR, msg="参数错误，请检查必填项")
        if (str(req_dict.get('apply_no')).isspace() or str(req_dict.get('org_code')).isspace()
                or str(req_dict.get('org_name')).isspace() or str(req_dict.get('msg_content')).isspace()
                or str(req_dict.get('phone_num')).isspace()):
            raise ValidationException(code=RET.PARAMERR, msg="参数错误，请检查必填项")

        sequence = Sequence('some_no_seq')
        seq = db.session.execute(sequence)
        message_id = "M{}{}".format(str(int(round(time.time() * 1000))), seq)
        ml = MessageLog(message_id=message_id,
                        user_id=g.current_user.id,
                        apply_no=req_dict.get('apply_no'),
                        org_code=req_dict.get('org_code'),
                        org_name=req_dict.get('org_name'),
                        send_class="验证码",
                        msgcontent=req_dict.get('msg_content'),
                        mobile=req_dict.get('phone_num'))
        smsv2api = Smsv2Api("47.99.242.143", "7862", "222492", "$x_Gn8U", "10690")
        result = json.loads(smsv2api.send(ml.mobile, ml.msgcontent, ml.message_id))
        ml.mt_code = result['status']
        db.session.add(ml)
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            raise ValidationException(code=RET.DBERR, msg="数据库异常")

        return jsonify(code=RET.OK, msg="成功")
    except ValidationException as e:
        return jsonify(code=e.code, msg=e.msg)
    except Exception as e:
        return jsonify(code=RET.UNKOWNERR, msg=str(e))

@auth.error_handler
def auth_error():
    return jsonify(code=RET.AUTHERROR, msg=g.auth_msg)
