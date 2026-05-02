import paramiko
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

print("Installing h2 package...")
stdin, stdout, stderr = ssh.exec_command('docker exec findix-backend pip install httpx[http2] h2')
print("STDOUT:", stdout.read().decode())
print("STDERR:", stderr.read().decode())

print("Restarting backend...")
stdin, stdout, stderr = ssh.exec_command('docker restart findix-backend')
print("STDOUT:", stdout.read().decode())

ssh.close()
