import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

debug_script = """
import json, traceback
from database import SessionLocal
from models import User, MasterProfile, JobApplication, Order
from sqlalchemy.orm import joinedload

db = SessionLocal()
try:
    # Check ALL applications with status pending/viewed
    pending_apps = db.query(JobApplication).filter(
        JobApplication.status.in_(['pending', 'viewed'])
    ).all()
    print(f"Total pending/viewed applications: {len(pending_apps)}")
    for a in pending_apps:
        employer = db.query(User).filter(User.id == a.employer_id).first()
        master_profile = db.query(MasterProfile).filter(MasterProfile.id == a.master_id).first()
        master_user = db.query(User).filter(User.id == master_profile.user_id).first() if master_profile else None
        print(f"App {a.id}: employer={employer.phone if employer else 'NONE'} -> master={master_user.phone if master_user else 'NONE'}, status={a.status}")
    
    # Now check what My Orders returns for each user
    print()
    print("--- Testing get_my_orders logic for each user ---")
    users = db.query(User).filter(User.phone.in_(['+998998426574', '+998991234567'])).all()
    for u in users:
        profile = db.query(MasterProfile).filter(MasterProfile.user_id == u.id).first()
        master_id = profile.id if profile else -1
        
        # Orders
        orders = db.query(Order).filter(
            (Order.client_id == u.id) | (Order.master_id == master_id)
        ).all()
        
        # Sent apps (pending/viewed/rejected)
        apps_sent = db.query(JobApplication).filter(
            JobApplication.employer_id == u.id,
            JobApplication.status.in_(['pending', 'viewed', 'rejected'])
        ).all()
        
        # Received rejected apps
        apps_rejected = []
        if profile:
            apps_rejected = db.query(JobApplication).filter(
                JobApplication.master_id == profile.id,
                JobApplication.status == 'rejected'
            ).all()
        
        print(f"User {u.phone}: {len(orders)} orders, {len(apps_sent)} sent apps, {len(apps_rejected)} rejected apps received")
finally:
    db.close()
"""

def debug():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, username=user, password=password)
        cmd = "cat << 'EOF' | docker exec -i findix-backend python\n" + debug_script + "\nEOF"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print("ERRORS:", err[:3000])
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    debug()
