import paramiko
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

print("Checking backend files...")
stdin, stdout, stderr = ssh.exec_command('ls -la /home/yaqingo/yaqin-production/backend')
print("STDOUT logs:")
print(stdout.read().decode())

ssh.close()
