import paramiko
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

# Check what happens when fcm_service loads
stdin, stdout, stderr = ssh.exec_command('''docker exec findix-backend python3 -c "
import os
print('CWD:', os.getcwd())
key_path = os.path.join(os.getcwd(), 'serviceAccountKey.json')
print('Key path:', key_path)
print('Exists:', os.path.exists(key_path))
print('All files in /app:', [f for f in os.listdir('/app') if 'service' in f.lower() or 'key' in f.lower()])

# Now test the actual FCM service
import firebase_admin
print('Apps before:', firebase_admin._apps)
from services.fcm_service import fcm_service
print('FCM initialized:', fcm_service._initialized)
print('Apps after:', firebase_admin._apps)
"''')
print("STDOUT:", stdout.read().decode())
print("STDERR:", stderr.read().decode())

ssh.close()
