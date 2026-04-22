import paramiko
from datetime import datetime, timedelta

def grant_vip():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password, timeout=30)
        
        phones = ["+998998426574", "+998991234567"]
        expiry = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d %H:%M:%S')
        
        for phone in phones:
            print(f"\n--- Granting VIP to {phone} ---")
            
            # First, ensure role is master (id 26 is admin, which is fine, but id 35 should be master)
            # We'll grant 'Pro' plan which works for both.
            
            sql = f"""
            INSERT INTO subscriptions (user_id, plan_name, expires_at, is_active, ads_limit, ads_used, user_role)
            SELECT id, 'Pro', '{expiry}', true, 9999, 0, role FROM users WHERE phone = '{phone}'
            ON CONFLICT (user_id) DO UPDATE SET 
                plan_name = 'Pro', 
                expires_at = '{expiry}', 
                is_active = true, 
                ads_limit = 9999,
                ads_used = 0,
                user_role = EXCLUDED.user_role;
            """
            
            # Escaping for shell
            cmd = f"docker exec findix-db psql -U findix_user -d findix_db -c \"{sql}\""
            
            stdin, stdout, stderr = client.exec_command(cmd)
            print(stdout.read().decode())
            print(stderr.read().decode())
            
        print("VIP GRANT COMPLETE!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    grant_vip()
