import paramiko
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

print("Checking container status...")
stdin, stdout, stderr = ssh.exec_command('docker ps -a | grep findix-backend')
print("STDOUT:", stdout.read().decode())

print("Fetching logs...")
stdin, stdout, stderr = ssh.exec_command('docker logs findix-backend')
print("STDOUT logs:")
print(stdout.read().decode()[-2000:])

ssh.close()
