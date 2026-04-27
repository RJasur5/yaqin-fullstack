import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password)

print("Listing ~:")
stdin, stdout, stderr = ssh.exec_command('ls -la ~')
print(stdout.read().decode())

print("Listing /root:")
stdin, stdout, stderr = ssh.exec_command('ls -la /root')
print(stdout.read().decode())
print(stderr.read().decode())
