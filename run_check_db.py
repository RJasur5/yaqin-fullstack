import paramiko
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

python_script = """
import sqlite3
conn = sqlite3.connect('/app/findix.db')
c = conn.cursor()
c.execute("SELECT id, phone, fcm_token, apns_token FROM users WHERE id=26")
print(c.fetchone())
conn.close()
"""

sftp = ssh.open_sftp()
with sftp.file('/home/yaqingo/check_db.py', 'w') as f:
    f.write(python_script)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('docker exec findix-backend python /app/../check_db.py')
print("STDOUT:", stdout.read().decode())
print("STDERR:", stderr.read().decode())

ssh.close()
