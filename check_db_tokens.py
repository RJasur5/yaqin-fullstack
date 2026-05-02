import paramiko
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)
stdin, stdout, stderr = ssh.exec_command("docker exec findix-db psql -U yaqin_user -d yaqin_db -c 'SELECT id, phone, fcm_token FROM users WHERE fcm_token IS NOT NULL LIMIT 5;'")
print(stdout.read().decode())
print(stderr.read().decode())
ssh.close()
