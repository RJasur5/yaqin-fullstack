import paramiko, time
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

# Stop and remove the container completely, then recreate
print("Stopping container...")
stdin, stdout, stderr = ssh.exec_command('cd /home/yaqingo/yaqin-production && docker compose stop backend && docker compose rm -f backend')
print(stdout.read().decode())
print(stderr.read().decode())

time.sleep(2)

print("Starting fresh container...")
stdin, stdout, stderr = ssh.exec_command('cd /home/yaqingo/yaqin-production && docker compose up -d backend')
print(stdout.read().decode())
print(stderr.read().decode())

time.sleep(5)

# Check logs
print("Checking logs...")
stdin, stdout, stderr = ssh.exec_command('docker logs findix-backend 2>&1 | head -20')
print(stdout.read().decode())

ssh.close()
print("Done!")
