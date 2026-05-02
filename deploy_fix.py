import paramiko
import os

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)
sftp = ssh.open_sftp()

local_path = os.path.join(os.getcwd(), 'backend', 'routers', 'orders.py')
remote_path = '/home/yaqingo/yaqin-production/backend/routers/orders.py'

print("Uploading fixed orders.py...")
sftp.put(local_path, remote_path)
sftp.close()
print("Uploaded!")

print("Restarting backend...")
stdin, stdout, stderr = ssh.exec_command('cd /home/yaqingo/yaqin-production && docker compose restart backend')
print(stdout.read().decode())
print(stderr.read().decode())

ssh.close()
print("Done!")
