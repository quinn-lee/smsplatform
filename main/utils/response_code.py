# coding:utf-8


class RET:
    OK = "0"
    AUTHERROR = "2001"
    DBERR = "4001"
    NODATA = "4002"
    DATAEXIST = "4003"
    DATAERR = "4004"
    SESSIONERR = "4101"
    LOGINERR = "4102"
    PARAMERR = "4103"
    USERERR = "4104"
    ROLEERR = "4105"
    PWDERR = "4106"
    REQERR = "4201"
    IPERR = "4202"
    THIRDERR = "4301"
    IOERR = "4302"
    SERVERERR = "4500"
    UNKOWNERR = "4501"
    NOTJSON = "4600"
    NOTXML = "4601"

    ret_map = {
        "0": u"成功",
        "2": u"IP鉴权错误",
        "3": u"账号密码不正确",
        "5": u"其它错误",
        "6": u"接入点错误",
        "7": u"账号状态异常",
        "11": u"系统内部错误，请联系管理员",
        "30": u"结束时间不能小于开始时间",
        "32": u"condition错，只能为APMID或MOBILE",
        "33": u"值列表过多，最多只能1000",
        "34": u"请求参数有误",
        "100": u"系统内部错误，请联系管理员",
        "102": u"单次提交的号码数过多",
        "10": u"原发号码错误，即extno错误",
        "15": u"余额不足",
    }


error_map = {
    RET.OK: u"成功",
    RET.AUTHERROR: u"权限验证失败",
    RET.DBERR: u"数据库查询错误",
    RET.NODATA: u"无数据",
    RET.DATAEXIST: u"数据已存在",
    RET.DATAERR: u"数据错误",
    RET.SESSIONERR: u"用户未登录",
    RET.LOGINERR: u"用户登录失败",
    RET.PARAMERR: u"参数错误",
    RET.USERERR: u"用户不存在或未激活",
    RET.ROLEERR: u"用户身份错误",
    RET.PWDERR: u"密码错误",
    RET.REQERR: u"非法请求或请求次数受限",
    RET.IPERR: u"IP受限",
    RET.THIRDERR: u"第三方系统错误",
    RET.IOERR: u"文件读写错误",
    RET.SERVERERR: u"内部错误",
    RET.UNKOWNERR: u"未知错误",
    RET.NOTJSON: u"请求非Json格式"
}


