import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

vip_script = """
import sys
from database import SessionLocal
from models import User, Subscription
from datetime import datetime, timedelta

db = SessionLocal()
try:
    ref_user = db.query(User).filter(User.phone == '+998998426574').first()
    plan, limit = 'month', 9999
    expires = datetime.now() + timedelta(days=365)
    
    if ref_user:
        ref_sub = db.query(Subscription).filter(Subscription.user_id == ref_user.id).order_by(Subscription.expires_at.desc()).first()
        if ref_sub:
            plan = ref_sub.plan_name
            limit = ref_sub.ads_limit
            expires = ref_sub.expires_at
            print(f"Using reference sub: {plan}, limit {limit}")
            
    target_user = db.query(User).filter(User.phone == '+998991234567').first()
    if target_user:
        for role in ['master', 'client']:
            sub = db.query(Subscription).filter(
                Subscription.user_id == target_user.id,
                Subscription.user_role == role
            ).first()
            if sub:
                sub.plan_name = plan
                sub.ads_limit = limit
                sub.expires_at = expires
                sub.is_active = True
                print(f"Updated {role} sub")
            else:
                sub = Subscription(
                    user_id=target_user.id,
                    user_role=role,
                    plan_name=plan,
                    ads_limit=limit,
                    expires_at=expires,
                    is_active=True
                )
                db.add(sub)
                print(f"Created {role} sub")
        db.commit()
        print("VIP set successfully!")
    else:
        print("Target user not found")
finally:
    db.close()
"""

def fix_vip_and_logs():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, username=user, password=password)
        
        # 1. VIP Fix
        print("--- Setting VIP ---")
        cmd = f'''docker exec findix-backend python -c "{vip_script}"'''
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err: print(f"Err: {err}")
        
        # 2. Check Logs
        print("--- Backend Logs ---")
        stdin, stdout, stderr = ssh.exec_command("cd /home/yaqingo/yaqin-production && docker compose logs backend --tail 50")
        print(stdout.read().decode())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    fix_vip_and_logs()
