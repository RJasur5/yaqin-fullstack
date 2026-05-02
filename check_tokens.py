import paramiko
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

# Check if user 26 has FCM token in the database
cmd = """docker exec findix-backend python3 -c "
from database import SessionLocal
from models import User
db = SessionLocal()
users = db.query(User).filter(User.fcm_token != None, User.fcm_token != '').all()
for u in users:
    print(f'User {u.id} ({u.name}): token={u.fcm_token[:30]}...')
db.close()
"
"""
stdin, stdout, stderr = ssh.exec_command(cmd)
print("STDOUT:", stdout.read().decode())
print("STDERR:", stderr.read().decode())
ssh.close()
