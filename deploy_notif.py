import paramiko
import os
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

sftp = ssh.open_sftp()
cwd = os.getcwd()
sftp.put(os.path.join(cwd, 'backend', 'notification_manager.py'), '/home/yaqingo/yaqin-production/backend/notification_manager.py')
sftp.close()

# Restart container
stdin, stdout, stderr = ssh.exec_command('cd /home/yaqingo/yaqin-production && docker compose restart backend')
print("Restarting backend:", stdout.read().decode())

ssh.close()
