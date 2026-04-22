import paramiko
import base64

def grant_vip():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    phones = ["+998998426574", "+998991234567"]
    
    inner_script_final = """
from database import SessionLocal
from models import User, Subscription
from datetime import datetime, timedelta
import logging

db = SessionLocal()
try:
    phones = %PHONES%
    for phone in phones:
        user = db.query(User).filter(User.phone == phone).first()
        if user:
            # Check for existing sub
            sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
            if not sub:
                # Use user's role if available, default to 'client' or 'master'
                role = user.role if hasattr(user, 'role') else 'client'
                sub = Subscription(user_id=user.id, user_role=role)
                db.add(sub)
            
            sub.plan_name = "pro"
            sub.is_active = True
            sub.expires_at = datetime.now() + timedelta(days=3650) # 10 years
            sub.ads_used = 0
            sub.ads_limit = 9999
            
            # Additional check for role if sub existed but role was null
            if hasattr(sub, 'user_role') and not sub.user_role:
                sub.user_role = user.role if hasattr(user, 'role') else 'client'
                
            print(f'GRANTED: {phone} (ID: {user.id})')
        else:
            print(f'NOT FOUND: {phone}')
    db.commit()
    print("SUCCESS: Database updated.")
except Exception as e:
    import traceback
    print(f'ERROR: {e}')
    traceback.print_exc()
finally:
    db.close()
""".replace("%PHONES%", str(phones))

    b64_script = base64.b64encode(inner_script_final.encode()).decode()

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password, timeout=15)
        
        # 1. Force reload docker-compose to pick up Postgres .env
        print("Ensuring backend uses PostgreSQL...")
        cmd_up = f"cd yaqin-production && echo '{password}' | sudo -S docker-compose up -d backend"
        client.exec_command(cmd_up)
        
        # 2. Upload and run the VIP script
        client.exec_command(f"echo '{b64_script}' | base64 -d > /tmp/vip.py")
        client.exec_command(f"echo '{password}' | sudo -S docker cp /tmp/vip.py findix-backend:/app/vip_script.py")
        
        cmd_run = f"echo '{password}' | sudo -S docker exec -i findix-backend python3 /app/vip_script.py"
        stdin, stdout, stderr = client.exec_command(cmd_run)
        
        print(stdout.read().decode())
        print(stderr.read().decode())
        
    except Exception as e:
        print(f"SSH Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    grant_vip()
