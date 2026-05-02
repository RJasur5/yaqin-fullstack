import paramiko, time, os
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)
sftp = ssh.open_sftp()

cwd = os.getcwd()

sftp.put(os.path.join(cwd, 'backend', 'models.py'), '/home/yaqingo/yaqin-production/backend/models.py')
sftp.put(os.path.join(cwd, 'backend', 'schemas.py'), '/home/yaqingo/yaqin-production/backend/schemas.py')
sftp.put(os.path.join(cwd, 'backend', 'routers', 'auth.py'), '/home/yaqingo/yaqin-production/backend/routers/auth.py')
sftp.put(os.path.join(cwd, 'backend', 'notification_manager.py'), '/home/yaqingo/yaqin-production/backend/notification_manager.py')
sftp.put(os.path.join(cwd, 'backend', 'services', 'fcm_service.py'), '/home/yaqingo/yaqin-production/backend/services/fcm_service.py')
sftp.put(os.path.join(cwd, 'backend', 'requirements.txt'), '/home/yaqingo/yaqin-production/backend/requirements.txt')
sftp.close()

# Rebuild container
stdin, stdout, stderr = ssh.exec_command('cd /home/yaqingo/yaqin-production && docker compose up -d --build backend')
print("Rebuilding backend:", stdout.read().decode())
print("STDERR:", stderr.read().decode())

ssh.close()
