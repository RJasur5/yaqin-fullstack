import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password)

print("Running docker compose:")
stdin, stdout, stderr = ssh.exec_command('cd /home/yaqingo/yaqin-production && docker compose restart backend')
print(stdout.read().decode())
print(stderr.read().decode())

print("Running migrations:")
stdin, stdout, stderr = ssh.exec_command('docker exec findix-backend python /app/migrate_job_applications.py')
print(stdout.read().decode())
print(stderr.read().decode())
