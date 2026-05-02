import paramiko, time
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)
sftp = ssh.open_sftp()

# Upload updated requirements.txt
import os
sftp.put(os.path.join(os.getcwd(), 'backend', 'requirements.txt'), '/home/yaqingo/yaqin-production/backend/requirements.txt')
sftp.close()
print("Uploaded requirements.txt")

# Full rebuild with no cache
print("Rebuilding (no cache for pip)...")
stdin, stdout, stderr = ssh.exec_command('cd /home/yaqingo/yaqin-production && docker compose build --no-cache backend && docker compose up -d --force-recreate backend')
out = stdout.read().decode()
err = stderr.read().decode()
print(out[-500:] if len(out) > 500 else out)
print(err[-500:] if len(err) > 500 else err)

time.sleep(5)

# Test push
print("\n=== Testing push notification ===")
stdin, stdout, stderr = ssh.exec_command('docker exec findix-backend python3 /app/test_push.py')
print(stdout.read().decode())
print(stderr.read().decode())

ssh.close()
print("Done!")
