import paramiko

def check_schema():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password, timeout=30)
        
        # Use a simple SELECT to get column names
        cmd = "docker exec findix-db psql -U findix_user -d findix_db -c \"SELECT column_name FROM information_schema.columns WHERE table_name = 'subscriptions';\""
        stdin, stdout, stderr = client.exec_command(cmd)
        print("Columns in subscriptions table:\n", stdout.read().decode())
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_schema()
