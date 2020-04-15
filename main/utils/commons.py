# coding: utf-8

from werkzeug.routing import BaseConverter
import time
import hashlib
import http.client


# 定义正则转换器
class ReConverter(BaseConverter):
    """"""
    def __init__(self, url_map, regex):
        # 调用父类的初始化方法
        super(ReConverter, self).__init__(url_map)
        # 保存正则表达式
        self.regex = regex


# 带token认证的post
def token_post(method, data):
    conn = None
    try:
        from main.models import User
        user = User.query.first()
        ts = str(int(round(time.time() * 1000)))
        md5_code = hashlib.md5((str(user.uuid) + str(ts) + str(user.api_key)).encode("utf-8")).hexdigest()
        print(md5_code)
        headers = {"Content-type": "application/json",
                   "Authorization": "Token {}&{}&{}".format(user.uuid, ts, md5_code)}
        conn = http.client.HTTPConnection("127.0.0.1", "5000", timeout=200)
        conn.request("POST", method, data, headers)
        response = conn.getresponse()
        retmsg = response.read().decode("utf8")
        conn.close()
        return retmsg
    except Exception as e:
        print(e)
    finally:
        if conn:
            conn.close()


# 普通post
def common_post(ip, port, method, data):
    conn = None
    try:
        headers = {"Content-type": "application/json"}
        conn = http.client.HTTPConnection(ip, port, timeout=200)
        conn.request("POST", method, data, headers)
        response = conn.getresponse()
        retmsg = response.read().decode("utf8")
        conn.close()
        return retmsg
    except Exception as e:
        print(e)
    finally:
        if conn:
            conn.close()
