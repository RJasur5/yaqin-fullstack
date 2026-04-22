import paramiko

def final_build():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {host}...")
        client.connect(host, username=user, password=password, timeout=30)
        
        print("Rebuilding backend to apply logic fixes...")
        cmd = "cd yaqin-production && echo 'nEQvV9Pi8e' | sudo -S docker compose up -d --build backend"
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        import time
        print("Waiting for stability...")
        time.sleep(10)
        
        print("Checking logs for success...")
        stdin, stdout, stderr = client.exec_command("docker logs --tail 20 findix-backend")
        logs = stdout.read().decode()
        print("Backend Logs:\n", logs)
        
        if "Application startup complete" in logs:
            print("SUCCESS: Logic fixes applied and backend is UP!")
        else:
            print("Check logs manually.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    final_build()
