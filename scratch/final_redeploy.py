import paramiko

def redeploy():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {host}...")
        client.connect(host, username=user, password=password, timeout=30)
        
        sftp = client.open_sftp()
        print("Uploading final docker-compose.yml...")
        sftp.put('scratch/docker-compose.yml', 'yaqin-production/docker-compose.yml')
        sftp.close()
        
        print("Applying configuration...")
        cmd = "cd yaqin-production && echo 'nEQvV9Pi8e' | sudo -S docker compose up -d"
        stdin, stdout, stderr = client.exec_command(cmd)
        print("Output:\n", stdout.read().decode())
        
        import time
        print("Waiting for backend to stabilize...")
        time.sleep(10)
        
        print("Checking backend logs...")
        stdin, stdout, stderr = client.exec_command("docker logs --tail 20 findix-backend")
        logs = stdout.read().decode()
        print("Final Logs:\n", logs)
        
        if "Uvicorn running" in logs or "Application startup complete" in logs:
            print("SUCCESS: Backend is UP!")
        else:
            print("WARNING: Check logs manually, could be issues.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    redeploy()
