import paramiko
import time

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password)

print("Checking nginx logs after restart:")
stdin, stdout, stderr = ssh.exec_command('docker logs findix-nginx --tail 20')
print(stdout.read().decode())
print(stderr.read().decode())
