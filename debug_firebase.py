import paramiko
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

# Check if the file is accessible inside the container
print("=== Checking file inside container ===")
stdin, stdout, stderr = ssh.exec_command('docker exec findix-backend ls -la /app/serviceAccountKey.json')
print(stdout.read().decode())
print(stderr.read().decode())

# Check if firebase_admin can read it
print("=== Testing Firebase init inside container ===")
stdin, stdout, stderr = ssh.exec_command('''docker exec findix-backend python3 -c "
import firebase_admin
from firebase_admin import credentials
import os
key_path = '/app/serviceAccountKey.json'
print('File exists:', os.path.exists(key_path))
print('File size:', os.path.getsize(key_path))
try:
    cred = credentials.Certificate(key_path)
    # Check if already initialized
    try:
        app = firebase_admin.get_app()
        print('Firebase already initialized')
    except ValueError:
        app = firebase_admin.initialize_app(cred)
        print('Firebase initialized successfully!')
except Exception as e:
    print(f'Error: {e}')
"''')
print(stdout.read().decode())
print(stderr.read().decode())

ssh.close()
