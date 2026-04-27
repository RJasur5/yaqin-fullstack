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
    # Check all users and their sent applications
    users = db.query(User).all()
    for u in users:
        apps_sent = db.query(JobApplication).filter(JobApplication.employer_id == u.id).all()
        if apps_sent:
            print(f"User {u.id} ({u.phone}) sent {len(apps_sent)} applications:")
            for a in apps_sent:
                try:
                    master_user = a.master.user
                    subcat = a.master.subcategory
                    print(f"  -> App {a.id}: to master {master_user.name}, status={a.status}, subcat={subcat.name_ru if subcat else 'NONE'}")
                except Exception as e:
                    print(f"  -> App {a.id}: ERROR loading relations: {e}")
finally:
    db.close()
"""

def check_apps():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, username=user, password=password)
        print("--- Checking all sent applications ---")
        cmd = "cat << 'EOF' | docker exec -i findix-backend python\n" + debug_script + "\nEOF"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print("ERRORS:", err[:2000])
            
        # Also get recent backend logs
        print("--- Recent backend logs (errors only) ---")
        stdin2, stdout2, stderr2 = ssh.exec_command(
            "cd /home/yaqingo/yaqin-production && docker compose logs backend --tail 30 2>&1 | grep -i 'error\\|traceback\\|exception\\|orders/my' "
        )
        print(stdout2.read().decode())
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check_apps()
