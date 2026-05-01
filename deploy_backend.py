import paramiko
import os

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)
sftp = ssh.open_sftp()

# Upload the fixed files to the production server
backend_dir = r'c:\Users\Jasur\.gemini\antigravity\scratch\findix\backend'
remote_dir = '/home/yaqingo/yaqin-production/backend'

files_to_upload = [
    'routers/orders.py',
    'routers/masters.py',
    'utils/regions.py',
]

for f in files_to_upload:
    local_path = os.path.join(backend_dir, f)
    remote_path = f'{remote_dir}/{f}'
    print(f"Uploading {f}...")
    sftp.put(local_path, remote_path)
    print(f"  Done: {f}")

sftp.close()

# Rebuild and restart the backend container
print("\n=== Rebuilding backend container ===")
stdin, stdout, stderr = ssh.exec_command('cd /home/yaqingo/yaqin-production && docker compose up -d --build backend')
out = stdout.read().decode()
err = stderr.read().decode()
print(out)
print(err)

ssh.close()
print("\nDone! Backend rebuilt.")
