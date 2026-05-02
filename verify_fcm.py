import paramiko, time
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)
time.sleep(5)
stdin, stdout, stderr = ssh.exec_command('docker logs findix-backend 2>&1 | grep -i "FCM\|Firebase\|initialized"')
print(stdout.read().decode())
ssh.close()
