import paramiko

def force_update():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {host}...")
        client.connect(host, username=user, password=password, timeout=60)
        
        print("STOPPING AND FORCE REBUILDING BACKEND...")
        # Force recreate to ensure fresh files are used
        cmd = "cd yaqin-production && echo 'nEQvV9Pi8e' | sudo -S docker compose down && echo 'nEQvV9Pi8e' | sudo -S docker compose up -d --build --force-recreate backend"
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        import time
        print("Waiting for backend to start up...")
        time.sleep(15)
        
        print("VERIFYING LOGS...")
        stdin, stdout, stderr = client.exec_command("docker logs --tail 20 findix-backend")
        logs = stdout.read().decode()
        print("Backend Logs:\n", logs)
        
        if "Application startup complete" in logs:
            print("SUCCESS: Logic fixes are LIVE!")
        else:
            # Second check just in case it took longer
            time.sleep(10)
            stdin, stdout, stderr = client.exec_command("docker logs --tail 20 findix-backend")
            logs = stdout.read().decode()
            if "Application startup complete" in logs:
                 print("SUCCESS: Logic fixes are LIVE!")
            else:
                 print("Backend is up but check logs for details.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    force_update()
