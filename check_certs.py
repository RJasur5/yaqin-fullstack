import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password)

print("Checking certs:")
stdin, stdout, stderr = ssh.exec_command('sudo -S ls -la /home/yaqingo/yaqin-production/deploy/certbot/conf/live/yaqingo.uz/', get_pty=True)
stdin.write(password + '\n')
stdin.flush()
print(stdout.read().decode())
