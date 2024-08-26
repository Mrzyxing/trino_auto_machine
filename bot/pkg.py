url = 'http://webapi.soa.ctripcorp.com/api/23349'

import requests
headers = {"appid": "100023771"}
def imPublicSendTextMessage(msg):
    body = {
        "accountId": "account-25b5a462",
        "corpId": "ctrip",
        "receiversType": 1,
        "receivers": [
            "S57187"
        ],
        "text": msg,
        "enText": None
    }
    requests.post(f"{url}/imPublicSendTextMessage",
                   headers = headers,
                  json = body
                )
