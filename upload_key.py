import paramiko
import os
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

sftp = ssh.open_sftp()
local_key = '/Users/alisherkholdorov/Downloads/AuthKey_XFX3836M5A.p8'
remote_key = '/home/yaqingo/yaqin-production/backend/AuthKey_XFX3836M5A.p8'
sftp.put(local_key, remote_key)
sftp.close()

# Copy it directly into the running container
print("Copying key to container...")
ssh.exec_command('docker cp /home/yaqingo/yaqin-production/backend/AuthKey_XFX3836M5A.p8 findix-backend:/app/AuthKey_XFX3836M5A.p8')

# Restart the backend to initialize the key
stdin, stdout, stderr = ssh.exec_command('docker restart findix-backend')
print("Restarting:", stdout.read().decode())

ssh.close()
