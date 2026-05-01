import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('95.182.118.245', username='yaqingo', password='nEQvV9Pi8e', timeout=10)
stdin, stdout, stderr = ssh.exec_command('docker exec findix-backend python -c "import sqlite3; db=sqlite3.connect(\'findix.db\'); print(db.execute(\\"SELECT phone, password_hash FROM users WHERE phone LIKE \'%123%45%67%\'\\").fetchall())"')
print(stdout.read().decode())
err = stderr.read().decode()
if err: print("ERR:", err)
ssh.close()
