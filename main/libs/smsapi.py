# coding: UTF-8
import http.client
import hashlib
import time
import urllib
from flask import current_app


class SmsApi:
    def __init__(self, apihost, apiport, userid, apikey):
        self.ApiHost = apihost
        self.ApiPort = apiport
        self.UserID = userid
        self.ApiKey = apikey

    def send(self, mobile, msg):
        params = {'userid': self.UserID, 'passwordMd5': self.ApiKey, 'msg_fmt': 8, 'mobile': mobile, 'message': msg,
                  'Ext': '', 'tc_id': '0'}
        return self._post("/sendsms.php", urllib.parse.urlencode(params))

    """
    def _signdigest(self, ts):
        m = hashlib.md5()
        m.update((self.UserID + ts + self.ApiKey).encode("utf-8"))
        hashstr = m.hexdigest()
        return hashstr
    """

    def _post(self, method, data):
        conn = None
        try:
            headers = {"Content-type": "application/x-www-form-urlencoded;charset=utf8"}
            conn = http.client.HTTPConnection(self.ApiHost, self.ApiPort, timeout=200)
            conn.request("POST", method, data, headers)
            response = conn.getresponse()
            retmsg = response.read().decode("utf8")
            current_app.logger.info(retmsg)
            conn.close()
            return retmsg
        except Exception as e:
            print(e)
            current_app.logger.error(e)
        finally:
            if conn:
                conn.close()

    def _get(self, method):
        conn = None
        try:
            headers = {"Content-type": "application/x-www-form-urlencoded;charset=utf8"}
            conn = http.client.HTTPConnection(self.ApiHost, self.ApiPort, timeout=200)
            conn.request("GET", method, "", headers)
            response = conn.getresponse()
            retmsg = response.read().decode("utf8")
            current_app.logger.info(retmsg)
            conn.close()
            return retmsg
        except Exception as e:
            print(e)
            current_app.logger.error(e)
        finally:
            if conn:
                conn.close()

    def balance(self):
        url = urllib.parse.quote("/getBalance.php?userid={}&passwordMd5={}".format(self.UserID, self.ApiKey), safe=':/?=&')  # 进行url编码
        return self._get(url)

    """
    def query(self):
        ts = self._getTimeStamp()
        sign = self._signdigest(ts)
        params = {'userid': self.UserID, 'ts': ts, 'sign': sign}
        print(params)
        current_app.logger.info(params)
        return self._post("/api/v2/sms/query", urllib.parse.urlencode(params))

    def _getTimeStamp(self):
        return str(int(round(time.time() * 1000)))
    """
