url = 'http://qconfig.ctripcorp.com'
token = '22C2BDC695B474C74F3DB521FAB88562'
groupid = '100022791'
targetgroupid = '100032337'
dataid = 'application.properties'
env = 'pro'
subenv = '' 

import requests
import datetime

def get_version():
    params = {'token': token,'groupid': groupid,'targetgroupid':targetgroupid, 'env':env,"subenv":subenv,'dataid': dataid}
    resp = requests.get(f"{url}/restapi/configs", params=params).json()['data']['editVersion']
    return resp

def update_keys(updates):
    v = get_version()
    params = {'token': token,"operator":"zyxing_gateway","serverenv":env,"groupid": groupid}
    body = {
        "version": v,
        "data": updates
    }
    requests.post(f"{url}/restapi/properties/{targetgroupid}/envs/{env}/configs/{dataid}",json=body,params=params)

update_keys({"artnova.weight": "60,40","adhoc.weight":"100,0"})
