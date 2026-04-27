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
    target_user = db.query(User).filter(User.phone == '+998991234567').first()
    if target_user:
        plan, limit = 'month', 9999
        expires = datetime.now() + timedelta(days=365)
        
        # Find any existing subscriptions
        subs = db.query(Subscription).filter(Subscription.user_id == target_user.id).all()
        if subs:
            for sub in subs:
                sub.plan_name = plan
                sub.ads_limit = limit
                sub.expires_at = expires
                sub.is_active = True
                print(f"Updated existing sub for role {sub.user_role}")
        else:
            # Create just ONE to avoid the SQLite unique constraint
            sub = Subscription(
                user_id=target_user.id,
                user_role="master",
                plan_name=plan,
                ads_limit=limit,
                expires_at=expires,
                is_active=True
            )
            db.add(sub)
            print("Created new master sub")
            
        db.commit()
        print("VIP set successfully!")
    else:
        print("Target user not found")
finally:
    db.close()
"""

def fix_vip():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, username=user, password=password)
        print("--- Setting VIP ---")
        cmd = "cat << 'EOF' | docker exec -i findix-backend python\n" + vip_script + "\nEOF"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode())
        print(stderr.read().decode())
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    fix_vip()
