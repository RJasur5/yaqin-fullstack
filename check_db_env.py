import paramiko
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

# Check .env for DB credentials
print("Checking .env...")
stdin, stdout, stderr = ssh.exec_command('cat /home/yaqingo/yaqin-production/backend/.env | grep POSTGRES')
print("STDOUT:", stdout.read().decode())

ssh.close()
