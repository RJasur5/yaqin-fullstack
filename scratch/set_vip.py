import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

def set_vip_subscription():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, username=user, password=password)
        
        # Python script to run inside container to update subscription
        py_script = """
from database import SessionLocal
from models import User, Subscription
from datetime import datetime, timedelta

db = SessionLocal()
try:
    # Get VIP plan from reference user
    ref_user = db.query(User).filter(User.phone == '+998998426574').first()
    if not ref_user:
        print("Reference user +998998426574 not found")
        # Default VIP values
        plan = 'month'
        limit = 9999
        expires = datetime.now() + timedelta(days=365)
    else:
        ref_sub = db.query(Subscription).filter(Subscription.user_id == ref_user.id).order_by(Subscription.expires_at.desc()).first()
        if ref_sub:
            plan = ref_sub.plan_name
            limit = ref_sub.ads_limit
            expires = ref_sub.expires_at
            print(f"Using reference sub: {plan}, limit {limit}, expires {expires}")
        else:
            plan = 'month'
            limit = 9999
            expires = datetime.now() + timedelta(days=365)

    # Target user
    target_user = db.query(User).filter(User.phone == '+998991234567').first()
    if not target_user:
        print("Target user +998991234567 not found")
    else:
        # Update or create subscription
        # For both master and client roles
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
                sub.ads_used = 0
                print(f"Updated {role} sub for +998991234567")
            else:
                sub = Subscription(
                    user_id=target_user.id,
                    user_role=role,
                    plan_name=plan,
                    ads_limit=limit,
                    expires_at=expires,
                    is_active=True,
                    ads_used=0
                )
                db.add(sub)
                print(f"Created {role} sub for +998991234567")
        
        db.commit()
        print("Done.")
finally:
    db.close()
"""
        # Save script on server and run
        ssh.exec_command("echo '''" + py_script + "''' > /home/yaqingo/yaqin-production/backend/set_vip.py")
        stdin, stdout, stderr = ssh.exec_command("docker exec findix-backend python /app/set_vip.py")
        print("Output:")
        print(stdout.read().decode())
        print(stderr.read().decode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    set_vip_subscription()
