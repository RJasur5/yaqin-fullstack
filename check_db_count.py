import paramiko
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

db_script = '''
import sqlite3
conn = sqlite3.connect('/app/findix.db')
c = conn.cursor()
c.execute("SELECT count(*) FROM users")
print("User count:", c.fetchone()[0])
conn.close()
'''
stdin, stdout, stderr = ssh.exec_command(f'docker exec findix-backend python -c "{db_script}"')
print("DB TOKENS:", stdout.read().decode())

ssh.close()
