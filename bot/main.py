from flask import Flask, request

app = Flask(__name__)

import subprocess
import cachetools

cache = cachetools.TTLCache(maxsize=1000,ttl=30)

def skip_self_msg(body):
    msg_type = body['msgType']
    if msg_type != 0:
        print('skip msg type')
        return True
    chat_type = body['chatType']
    sender = body['sender']
    owner = body['owner']
    partner_jid = None
    if chat_type in ['group_chat','sys_muc']:
        partner_jid = body['gid']
    elif chat_type in ['chat','sys_mam']:
        partner_jid = body['chatPartner']
    print(f"partner_jid is {partner_jid} and ower is {owner} sender {sender} content:{body['xmppJson']['body']}")
    if partner_jid is None or owner == partner_jid or owner == sender:
        print("skip this")
        return True
    pk = body['msgId']
    if cache.get(pk,False):
        print(f"skip cached pk {pk}")
        cache[pk] = True
        return True
    cache[pk] = True
    print("process this")
    return False 

@app.route("/", methods=['POST'])
def on_msg():
    body = request.json['bodyV2']
    print(request.json) 
    if skip_self_msg(body):
        return 'ok' 
    from_user = body['chatPartnerInfo']['openId']
    content = body['xmppJson']['body']
    
    if from_user == 'S57187':
        if content == 'trino-gateway start':
            subprocess.Popen('sh /home/dpadmin/workspace/dpbot/svc-trino-gateway.sh start', shell=True)
            imPublicSendTextMessage('start trino-gateway')
        elif content == 'trino-gateway stop':
            subprocess.Popen('sh /home/dpadmin/workspace/dpbot/svc-trino-gateway.sh stop', shell=True)
            imPublicSendTextMessage('stop trino-gateway')
        elif 'diskclean' == content[:9]:
            from disk_clean import disk_clean
            import re

            matchers = re.findall(r"SVR\w+", content)
            for i in matchers:
                ip = disk_clean(i)
                imPublicSendTextMessage(f"Finish clean {i}({ip}) disk.")
        else:
            imPublicSendTextMessage('Wrong! trino-gateway start/stop.')
    import time
    print(request.json)
    time.sleep(10)
    return "ok"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7788)

