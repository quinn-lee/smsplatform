import http.client
import json
from flask import current_app

class Smsv2Api:
    def __init__(self, apihost, apiport, account, password, extno):
        self.ApiHost = apihost
        self.ApiPort = apiport
        self.account = account
        self.password = password
        self.extno = extno

    def _post(self, path, data):
        conn = None
        try:
            headers = {"Content-type": "application/json;charset=utf-8"}
            conn = http.client.HTTPConnection(self.ApiHost, self.ApiPort, timeout=200)
            conn.request("POST", path, data, headers)
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

    def _get(self, path):
        conn = None
        try:
            headers = {"Content-type": "application/json;charset=utf-8"}
            conn = http.client.HTTPConnection(self.ApiHost, self.ApiPort, timeout=200)
            conn.request("GET", path, "", headers)
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
        params = {'action': "balance", 'account': self.account, 'password': self.password}
        current_app.logger.info(params)
        current_app.logger.info(json.dumps(params))
        return self._post("/smsv2", json.dumps(params))

    def send(self, mobile, content, label):
        params = {'action': "send", 'account': self.account, 'password': self.password, 'mobile': mobile, 'content': content, 'extno': self.extno, 'label': label}
        current_app.logger.info(params)
        current_app.logger.info(json.dumps(params))
        return self._post("/smsv2", json.dumps(params))

    def report(self):
        params = {'action': "report", 'account': self.account, 'password': self.password}
        return self._post("/smsv2", json.dumps(params))