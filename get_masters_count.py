import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

stdin, stdout, stderr = ssh.exec_command(
    "docker exec findix-backend python -c \"import sqlite3; conn = sqlite3.connect('findix.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM users WHERE role=\\'master\\''); print(cursor.fetchone()[0]); conn.close()\""
)
print(stdout.read().decode().strip())
err = stderr.read().decode().strip()
if err: print("Error:", err)
ssh.close()
