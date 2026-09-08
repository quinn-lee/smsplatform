import http.client
import json
import base64
import hashlib
from flask import current_app

class MasApi:
    def __init__(self, apihost, apiport, ecname, apid, secretkey, sign):
        self.ApiHost = apihost
        self.ApiPort = apiport
        self.ecName = ecname
        self.apId = apid
        self.secretKey = secretkey
        self.sign = sign

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

    def send(self, mobiles, content):
        params = {'ecName': self.ecName,
                  'apId': self.apId,
                  #'secretKey': self.secretKey,
                  'mobiles': mobiles,
                  'content': content,
                  'sign': self.sign,
                  'addSerial': ''}
        m_mac = hashlib.md5()
        m_mac_cont = params['ecName']+params['apId']+self.secretKey+params['mobiles']+params['content']+params['sign']+params['addSerial']
        m_mac.update(m_mac_cont.encode("utf8"))
        params['mac'] = m_mac.hexdigest().lower()
        current_app.logger.info(params)
        current_app.logger.info(json.dumps(params))
        encoding_params = base64.b64encode(json.dumps(params).encode())
        strs = str(encoding_params, "utf8")
        current_app.logger.info(strs)
        return self._post("/sms/norsubmit", strs)