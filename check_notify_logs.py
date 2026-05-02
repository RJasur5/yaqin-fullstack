import paramiko
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)
stdin, stdout, stderr = ssh.exec_command('docker logs --tail 100 findix-backend 2>&1 | grep -i "NOTIFY\|FCM\|push\|new_order\|error\|token"')
print(stdout.read().decode())
ssh.close()
