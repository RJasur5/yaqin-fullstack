import paramiko

def debug():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password, timeout=30)
        
        print("--- ORDERS DATABASE CHECK ---")
        # Count all vs open orders
        cmds = [
            "docker exec findix-db psql -U findix_user -d findix_db -c \"SELECT count(*) FROM orders;\"",
            "docker exec findix-db psql -U findix_user -d findix_db -c \"SELECT count(*) FROM orders WHERE status = 'open';\"",
            "docker exec findix-db psql -U findix_user -d findix_db -c \"SELECT id, title, status, created_at FROM orders ORDER BY created_at DESC LIMIT 5;\""
        ]
        for cmd in cmds:
            print(f"Executing: {cmd}")
            stdin, stdout, stderr = client.exec_command(cmd)
            print(stdout.read().decode())

        print("--- LATEST BACKEND LOGS (Check for subscription errors) ---")
        stdin, stdout, stderr = client.exec_command("docker logs --tail 50 findix-backend")
        print(stdout.read().decode())
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    debug()
