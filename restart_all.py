import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password)

print("Checking local curl to 443:")
stdin, stdout, stderr = ssh.exec_command('curl -v -k https://localhost/download/app-release.apk')
print(stdout.read().decode())
print(stderr.read().decode())

print("Restarting ALL docker-compose containers to ensure port bindings are correct:")
stdin, stdout, stderr = ssh.exec_command('cd /home/yaqingo/yaqin-production && docker compose down && docker compose up -d')
print(stdout.read().decode())
print(stderr.read().decode())
