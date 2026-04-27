import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

def fix_and_deploy():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, username=user, password=password)
        sftp = ssh.open_sftp()
        
        # Upload fixed files
        print("Uploading subscriptions.py...")
        sftp.put(r'c:\Users\Jasur\.gemini\antigravity\scratch\findix\backend\routers\subscriptions.py', '/home/yaqingo/yaqin-production/backend/routers/subscriptions.py')
        
        print("Uploading click_service.py...")
        sftp.put(r'c:\Users\Jasur\.gemini\antigravity\scratch\findix\backend\services\click_service.py', '/home/yaqingo/yaqin-production/backend/services/click_service.py')
        
        sftp.close()
        
        # Activate subscription for user 40 directly in DB
        print("Activating subscription for user 40...")
        activate_cmd = """docker exec findix-backend python3 -c "
from database import SessionLocal
from models import Subscription
from datetime import datetime, timedelta, timezone

db = SessionLocal()
now = datetime.now(timezone.utc).replace(tzinfo=None)
expires = now + timedelta(days=1)

sub = db.query(Subscription).filter(Subscription.user_id == 40).first()
if sub:
    sub.plan_name = 'day'
    sub.user_role = 'master'
    sub.ads_limit = 1
    sub.ads_used = 0
    sub.expires_at = expires
    sub.is_active = True
    print(f'UPDATED subscription for user 40: expires {expires}')
else:
    sub = Subscription(user_id=40, user_role='master', plan_name='day', ads_limit=1, ads_used=0, expires_at=expires, is_active=True)
    db.add(sub)
    print(f'CREATED subscription for user 40: expires {expires}')

db.commit()
print('SUCCESS')
"
"""
        stdin, stdout, stderr = ssh.exec_command(activate_cmd)
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"stderr: {err}")
        
        # Rebuild backend
        print("Rebuilding backend...")
        stdin, stdout, stderr = ssh.exec_command("cd /home/yaqingo/yaqin-production && docker compose up -d --build backend")
        for line in stdout:
            print(line.strip())
        for line in stderr:
            print(line.strip())
        
        print("Done!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    fix_and_deploy()
