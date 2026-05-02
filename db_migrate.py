import paramiko
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

# Add column to DB
print("Adding apns_token column to users table...")
stdin, stdout, stderr = ssh.exec_command('docker exec findix-db psql -U findix_user -d findix_db -c "ALTER TABLE users ADD COLUMN apns_token VARCHAR(255);"')
print("STDOUT:", stdout.read().decode())
print("STDERR:", stderr.read().decode())

ssh.close()
