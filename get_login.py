### This script checks which users are logged into the Seaglider server
### and generates a small JSON with active users

import os
import sys
import urllib.request
import paramiko
import datetime
import json

# Open SSH
host = "seaglider.socco.org.za"
port = 22
transport = paramiko.Transport((host, port))
auth_file = "/root/sg_auth"
f = open(auth_file, "r")
username = f.readline().strip("\n")
password = f.readline().strip("\n")
f.close()

ssh = paramiko.SSHClient()
ssh.load_system_host_keys()
ssh.connect(host, username=username, password=password)
ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('w')
output_w = ssh_stdout.readlines()

ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('last | grep "sg542" | head -n 1')
output_lastLogin_sg542 = ssh_stdout.readlines()
ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('last | grep "sg574" | head -n 1')
output_lastLogin_sg574 = ssh_stdout.readlines()
ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('last | grep "sg573" | head -n 1')
output_lastLogin_sg573 = ssh_stdout.readlines()

print(output_lastLogin_sg574[0])
sg542_lastlogin = output_lastLogin_sg542[0].split('/')[1][4:].strip()
sg573_lastlogin = output_lastLogin_sg573[0].split('/')[1][4:].strip()
sg574_lastlogin = output_lastLogin_sg574[0].split('/')[1][4:].strip()

sg542_online = False
sg573_online = False
sg574_online = False

users_online = []
for i in range(2,len(output_w)):
    #print(output[i].split('    ')[0])
    if(output_w[i].split('    ')[0] == 'sg542'):
        sg542_online = True
    if(output_w[i].split('    ')[0] == 'sg573'):
        sg573_online = True
    if(output_w[i].split('    ')[0] == 'sg574'):
        sg574_online = True



data = {}
data['user'] = []
data['user'].append({
    'name': 'sg573',
    'last_login': sg573_lastlogin,
    'currently_loggedIn': sg573_online
})

data['user'].append({
    'name': 'sg574',
    'last_login': sg574_lastlogin,
    'currently_loggedIn': sg574_online
})

data['user'].append({
    'name': 'sg542',
    'last_login': sg542_lastlogin,
    'currently_loggedIn': sg542_online
})
with open('users.json', 'w') as outfile:
    json.dump(data, outfile)

print("updating git...")
print("Syncing users.json")
cmd  = "git commit -m 'updated login info' users.json"
print(cmd)
os.system(cmd)
os.system("git push")
