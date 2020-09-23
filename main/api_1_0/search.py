# coding:utf-8
from . import api
from main import db
from main.models import MsgClass, MsgOrg, MessageLog
from flask import jsonify, request, current_app
from main.utils.response_code import RET
from sqlalchemy.sql import func
from main.utils.commons import Excel
import time
from main.libs.smsapi import SmsApi
import json


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

    try:
        res = db.session.query(MessageLog.org_code, MessageLog.org_name, MessageLog.send_class, MessageLog.msg_status,
                               func.count(MessageLog.id))
        if req_dict.get('start_date') != '':
            res = res.filter(MessageLog.created_at >= "{} 00:00:00".format(req_dict.get('start_date')))
        if req_dict.get('end_date') != '':
            res = res.filter(MessageLog.created_at <= "{} 23:59:59".format(req_dict.get('end_date')))
        if req_dict.get('msg_org') != '':
            res = res.filter(MessageLog.org_code == req_dict.get('msg_org'))
        if req_dict.get('msg_class') != '':
            res = res.filter(MessageLog.send_class == req_dict.get('msg_class'))
        if req_dict.get('msg_status') != '':
            res = res.filter(MessageLog.msg_status == req_dict.get('msg_status'))
        res = res.group_by(MessageLog.org_code, MessageLog.org_name, MessageLog.send_class, MessageLog.msg_status)
        data = [{'org_code': r[0], 'org_name': r[1], 'send_class': r[2], 'msg_status': r[3], 'count': r[4],
                 'start_date': req_dict.get('start_date'), 'end_date': req_dict.get('end_date')} for r in res]
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
    except Exception as e:
        current_app.logger.error(e)
        if req_dict['action'] == 'search':
            errmsg = '数据查询错误'
        else:
            errmsg = '文件生成错误'
        return jsonify(errno="1", errmsg=errmsg)


@api.route("/org_details")
def org_details():
    try:
        mls = MessageLog.query
        if request.args.get('start_date') != '':
            mls = mls.filter(MessageLog.created_at >= "{} 00:00:00".format(request.args.get('start_date')))
        if request.args.get('end_date') != '':
            mls = mls.filter(MessageLog.created_at <= "{} 23:59:59".format(request.args.get('end_date')))
        if request.args.get('org_code') != '':
            mls = mls.filter(MessageLog.org_code == request.args.get('org_code'))
        if request.args.get('org_name') != '':
            mls = mls.filter(MessageLog.org_name == request.args.get('org_name'))
        if request.args.get('action') == 'search':  # 搜索
            pagination = mls.paginate(int(request.args.get('currentPage')), per_page=int(request.args.get('pageSize')))
            data = [ml.to_json() for ml in pagination.items]
            return jsonify(errno="0", data=data, totalRows=len(mls.all()))
        else:  # 导出
            file_name = 'details{}.xlsx'.format(str(int(round(time.time() * 1000))))
            file_path = 'main/static/excels/{}'.format(file_name)
            colums_name = ['姓名', '证件号码', '手机号', '接收时间', '接收状态', '短信类别', '发送人', '短信内容', '发送日期']

            book = Excel(file_path)
            book.write_colume_name(colums_name)
            i = 1
            for row in mls.all():
                book.write_content(i, row.to_arr())
                i += 1
            book.close()
            return jsonify(errno="0", data=[{'filename': file_name}])
    except Exception as e:
        current_app.logger.error(e)
        if request.args.get('action') == 'search':
            errmsg = '数据查询错误'
        else:
            errmsg = '文件生成错误'
        return jsonify(errno="1", errmsg=errmsg)


@api.route("/fare_details")
def fare_details():
    try:
        mls = MessageLog.query
        if request.args.get('start_date') != '':
            mls = mls.filter(MessageLog.created_at >= "{} 00:00:00".format(request.args.get('start_date')))
        if request.args.get('end_date') != '':
            mls = mls.filter(MessageLog.created_at <= "{} 23:59:59".format(request.args.get('end_date')))
        if request.args.get('msg_status') != '':
            mls = mls.filter(MessageLog.msg_status == request.args.get('msg_status'))
        if request.args.get('action') == 'search':  # 搜索
            pagination = mls.paginate(int(request.args.get('currentPage')), per_page=int(request.args.get('pageSize')))
            data = [ml.to_json() for ml in pagination.items]
            return jsonify(errno="0", data=data, totalRows=len(mls.all()))
        else:  # 导出
            file_name = 'fares{}.xlsx'.format(str(int(round(time.time() * 1000))))
            file_path = 'main/static/excels/{}'.format(file_name)
            colums_name = ['姓名', '手机号', '接收时间', '接收状态']

            book = Excel(file_path)
            book.write_colume_name(colums_name)
            i = 1
            for row in mls.all():
                book.write_content(i, row.to_arr2())
                i += 1
            book.close()
            return jsonify(errno="0", data=[{'filename': file_name}])
    except Exception as e:
        current_app.logger.error(e)
        if request.args.get('action') == 'search':
            errmsg = '数据查询错误'
        else:
            errmsg = '文件生成错误'
        return jsonify(errno="1", errmsg=errmsg)


@api.route("/balance", methods=["GET"])
def balance():
    try:
        #smsapi = SmsApi("47.111.38.50", 8081, "350122", "736b8235fc654cdd979dd0865972b700")
        smsapi = SmsApi("139.129.107.160", 8085, "126631", "ac87f26fed1f5907482ef7ea984ead6f")
        result = smsapi.balance()
        return jsonify(errno="0", data=[{'balance': result}])
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno="0", errmsg=str(e))


@api.route("/message", methods=["GET"])
def message():
    try:
        smsapi = SmsApi("47.111.38.50", 8081, "350122", "736b8235fc654cdd979dd0865972b700")
        result = json.loads(smsapi.balance())
        if result.get('code') != "0":
            raise Exception(result.get('msg'))
        num = result.get('data').get('balance')
        if int(num) >= 10000:
            raise Exception("短信剩余条数不用提示")
        return jsonify(errno="0", data=[{'mtitle': '余额预警',
                                         'mcontent': "当前短信剩余条数为{}".format(num)}])
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno="1", errmsg=str(e))
