url = 'http://osg.ops.ctripcorp.com/api/11100'

req_sample = {
    "access_token": "5e9ba1b202f92cd6d5f7ac63abbd0881",
    "request_body": {
        "action": "BMC.CORE:CI_Computer",
        "query": {
            "CI_Code@=": "SVR13366HW1288"
        },
        "fieldNames": ["CI_ProductIP" ],
        "order": "RequestId",
        "start": 0,
        "limit": 1
    }
}

import requests
def get_ip(hostname):
    req = req_sample.copy()
    req['request_body']['query']['CI_Code@='] = hostname
    resp = requests.post(url=url,json=req).json()
    return resp['data'][0]['CI_ProductIP']

import paramiko
def ssh(hostname,username,cmd,port=22):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        # 连接到远程服务器
        client.connect(hostname, port, username)
        stdin, stdout, stderr = client.exec_command(cmd)

        # 获取命令执行结果
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        return {'stdout': output.strip(),'stderr':error.strip()}
    finally:
        # 关闭 SSH 连接
        client.close()

def disk_clean(host):
    cmds = [
        'find /opt/app/ -name java_pid*.hprof -type f -exec sudo rm -rf {} \;'
    ]
    host = get_ip(host)
    for cmd in cmds:
        ssh(host,'dpadmin',cmd)
    return host
