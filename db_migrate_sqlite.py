import paramiko
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

python_script = """
import sqlite3
try:
    conn = sqlite3.connect('/app/findix.db')
    c = conn.cursor()
    c.execute('ALTER TABLE users ADD COLUMN apns_token VARCHAR(255);')
    conn.commit()
    conn.close()
    print('SUCCESS')
except Exception as e:
    print('ERROR:', str(e))
"""

print("Adding apns_token to SQLite via Python...")
stdin, stdout, stderr = ssh.exec_command(f'docker exec findix-backend python -c "{python_script}"')
print("STDOUT:", stdout.read().decode())
print("STDERR:", stderr.read().decode())

ssh.close()
