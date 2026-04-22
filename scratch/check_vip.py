import paramiko

def check_vip():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password, timeout=30)
        
        phones = ["+998998426574", "+998991234567"]
        
        for phone in phones:
            print(f"\n--- Checking {phone} ---")
            # Check user role
            cmd_user = f"docker exec findix-db psql -U findix_user -d findix_db -c \"SELECT id, phone, role FROM users WHERE phone = '{phone}';\""
            stdin, stdout, stderr = client.exec_command(cmd_user)
            print("User:", stdout.read().decode())
            
            # Check subscription
            cmd_sub = f"docker exec findix-db psql -U findix_user -d findix_db -c \"SELECT plan_name, is_active, expires_at FROM subscriptions WHERE user_id = (SELECT id FROM users WHERE phone = '{phone}');\""
            stdin, stdout, stderr = client.exec_command(cmd_sub)
            print("Subscription:", stdout.read().decode())
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_vip()
