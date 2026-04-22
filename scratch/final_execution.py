import paramiko

def execute():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {host}...")
        client.connect(host, username=user, password=password, timeout=60)
        
        # 1. Upload the restored compose file
        sftp = client.open_sftp()
        print("Uploading restored docker-compose.yml...")
        sftp.put('scratch/docker-compose-restore.yml', 'yaqin-production/docker-compose.yml')
        sftp.close()
        
        # 2. Run commands one by one to avoid shell parsing issues
        commands = [
            "cd yaqin-production && echo 'nEQvV9Pi8e' | sudo -S docker compose down",
            "cd yaqin-production && echo 'nEQvV9Pi8e' | sudo -S docker compose up -d --build backend"
        ]
        
        for cmd in commands:
            print(f"Executing: {cmd}")
            stdin, stdout, stderr = client.exec_command(cmd)
            print(stdout.read().decode())
            print(stderr.read().decode())
            
        import time
        print("Waiting for backend to stabilize...")
        time.sleep(20)
        
        # 3. Final Code Verification
        print("VERIFYING CODE INSIDE CONTAINER...")
        stdin, stdout, stderr = client.exec_command("docker exec findix-backend grep 'admin' /app/routers/orders.py")
        result = stdout.read().decode()
        if "admin" in result:
            print("SUCCESS: Logic fix is LIVE inside the container!")
        else:
            print("FAILURE: Code did not update for some reason.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    execute()
