import paramiko
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

cmd = """docker exec findix-backend python3 -c "
from database import SessionLocal
from models import User, MasterProfile
db = SessionLocal()
# Check user 26 master profile
mp = db.query(MasterProfile).filter(MasterProfile.user_id == 26).first()
if mp:
    print(f'User 26 is master: subcat_id={mp.subcategory_id}, city={mp.city}, district={mp.district}')
else:
    print('User 26 is NOT a master')

# Check user 35
u35 = db.query(User).filter(User.id == 35).first()
if u35:
    print(f'User 35: name={u35.name}, fcm_token={u35.fcm_token}')

# Check latest order from user 35
from models import Order
latest = db.query(Order).filter(Order.client_id == 35).order_by(Order.created_at.desc()).first()
if latest:
    print(f'Latest order by user 35: id={latest.id}, subcat_id={latest.subcategory_id}, city={latest.city}, status={latest.status}')
db.close()
"
"""
stdin, stdout, stderr = ssh.exec_command(cmd)
print("STDOUT:", stdout.read().decode())
print("STDERR:", stderr.read().decode())
ssh.close()
