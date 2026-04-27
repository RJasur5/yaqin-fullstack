import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password)

print("Checking curl to download URL:")
stdin, stdout, stderr = ssh.exec_command('curl -v -k -o /dev/null https://yaqingo.uz/download/app-release.apk')
print(stdout.read().decode())
print(stderr.read().decode())
