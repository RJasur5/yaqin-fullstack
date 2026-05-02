import paramiko
import json
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

print("Fetching APNs logs...")
stdin, stdout, stderr = ssh.exec_command('docker logs findix-backend 2>&1 | grep -E -i "apns|fcm|push|notification"')
print("STDOUT logs:")
lines = stdout.read().decode().splitlines()
for line in lines[-50:]:
    print(line)

print("\nChecking user's tokens...")
# Get the most recently created order to find the relevant user or just query db for all tokens
db_script = '''
import sqlite3
conn = sqlite3.connect('/app/findix.db')
c = conn.cursor()
c.execute("SELECT id, phone, fcm_token, apns_token FROM users WHERE fcm_token IS NOT NULL OR apns_token IS NOT NULL ORDER BY id DESC LIMIT 5")
for row in c.fetchall():
    print(row)
conn.close()
'''
stdin, stdout, stderr = ssh.exec_command(f'docker exec findix-backend python -c "{db_script}"')
print("DB TOKENS:", stdout.read().decode())

ssh.close()
