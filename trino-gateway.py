import requests

artnova_url = 'http://presto-rb-artnova.ops.ctripcorp.com/ui/api/stats'
adhoc_url = 'http://presto-rb-adhoc.ops.ctripcorp.com/ui/api/stats'
debug = False
load_low = 10
load_high = 88 

def blocked_num():
    artnova = requests.get(artnova_url).json()['queuedQueries']
    adhoc = requests.get(adhoc_url).json()['queuedQueries']
    return {'artnova': artnova, 'adhoc': adhoc}

qconfig_url = 'http://qconfig.ctripcorp.com'
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
    resp = requests.get(f"{qconfig_url}/restapi/configs", params=params).json()['data']['editVersion']
    return resp

def update_keys(updates):
    v = get_version()
    params = {'token': token,"operator":"zyxing_gateway","serverenv":env,"groupid": groupid}
    body = {
        "version": v,
        "data": updates
    }
    requests.post(f"{qconfig_url}/restapi/properties/{targetgroupid}/envs/{env}/configs/{dataid}",json=body,params=params)



bot_url = 'http://webapi.soa.ctripcorp.com/api/23349'
 
import requests
headers = {"appid": "100023771"}
def imPublicSendTextMessage(msg):
    if debug:
        print(msg)
        return 
    body = {
        "accountId": "account-25b5a462",
        "corpId": "ctrip",
        "receiversType": 1,
        "receivers": [
            "S57187",
            "S46059"
        ],
        "text": msg,
        "enText": None
    }
    requests.post(f"{bot_url}/imPublicSendTextMessage",
                 headers = headers,
                json = body
                 )
 


from enum import Enum
class ClusterState(Enum):
    NORMAL = 0
    # 0b01
    ADHOC = 1
    # 0b10
    ARTNOVA = 2
    # 0b11
    BOTH = ADHOC|ARTNOVA

class ClusterAction(Enum):
    NO_THING = 0
    ON_FREE = 1
    ON_RESET = 2

def detect_state(threshold):
    blocks = blocked_num()
    """ 
    gt thredhold is 1 otherwise is 0
    artnova adhoc
        0     0  --   both less than threshold
        0     1  --
        1     0     > some/both greather than threshold
        1     1  --
    """
    state_code = ClusterState.NORMAL.value
    if blocks['artnova'] > threshold:
        state_code = state_code | 0b10
    if blocks['adhoc'] > threshold:
        state_code = state_code | 0b01

    print(f"State code is {state_code}")
    return ClusterState(state_code)

clusters = ['adhoc', 'artnova']
def free_side_cluster(state:ClusterState):
    imPublicSendTextMessage(f"Got state {state} with code {state.value}")
    cluster_idx = f"{state.value:02b}"[::-1].find('1')
    imPublicSendTextMessage(f"Means {clusters[cluster_idx]} blocked")
    if debug:
        return
    if cluster_idx == 0:
        update_keys({"artnova.weight": "100,0","adhoc.weight":"0,100"})
    else:
        update_keys({"artnova.weight": "0,100","adhoc.weight":"100,0"})    

def free_reset():
    imPublicSendTextMessage(f"Reset cluster to origin flow.")
    update_keys({"artnova.weight": "60,40","adhoc.weight":"100,0"})

def do_nothing(state:ClusterState):
    print(f"Do nothing with state:{state}")
    pass


import time
def state_machine(pre_state, pre_action):
    if pre_action == ClusterAction.ON_FREE:
        # free some cluster need set to normal utils one cluster blocked queries below a threshold
        state:ClusterState = detect_state(load_low)
        if state.value & pre_state.value == 0:
            """
             state_machine make pre_state only block one cluster if both bolcked,so value is 01 or 10
             we want 1 change to 0 so make 'and' with current state
             only both free or target cluster is free may return 0 otherwise >0
            """
            return (state, ClusterAction.ON_RESET)
        # during ON_FREE: keep origin state and action
        return (pre_state, pre_action)
    elif pre_action == ClusterAction.ON_RESET:
        free_reset()
        return (ClusterState.NORMAL, ClusterAction.NO_THING)
    else:
        state:ClusterState = detect_state(load_high)
        if state == ClusterState.NORMAL:
            do_nothing(state)
            return (state, ClusterAction.NO_THING)
        if state == ClusterState.BOTH:
            # choose only one cluster blocked
            imPublicSendTextMessage(f"{state} so force mark artnova as blocked.")
            state = ClusterState.ARTNOVA
            free_side_cluster(state)
            return (state, ClusterAction.ON_FREE)
        if state.value > 0:
            free_side_cluster(state)
            return (state, ClusterAction.ON_FREE)
    
    print(f"Should not run at here, it is a bug!")
    return (ClusterState.NORMAL, ClusterAction.NO_THING)


import datetime

def main():
    state = ClusterState.NORMAL
    action = ClusterAction.NO_THING
    while(True):
        (state,action) = state_machine(state,action)
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%m:%S')}: Current cluster state is {state} and will {action}")
        time.sleep(10)

main()
