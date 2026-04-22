import paramiko

def hard_rebuild():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {host}...")
        client.connect(host, username=user, password=password, timeout=60)
        
        print("1. Verifying file content on host host...")
        stdin, stdout, stderr = client.exec_command("cat yaqin-production/backend/routers/orders.py | grep 'admin'")
        content = stdout.read().decode()
        if "admin" in content:
            print("Host file is correct (new code exists).")
        else:
            print("WARNING: Host file seems OLD! Re-uploading...")
            return

        print("2. FORCING NO-CACHE REBUILD...")
        # We stop, remove image, and rebuild without cache
        cmd = """
        cd yaqin-production && 
        echo 'nEQvV9Pi8e' | sudo -S docker compose stop backend && 
        echo 'nEQvV9Pi8e' | sudo -S docker compose rm -f backend && 
        echo 'nEQvV9Pi8e' | sudo -S docker compose build --no-cache backend && 
        echo 'nEQvV9Pi8e' | sudo -S docker compose up -d backend
        """
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        import time
        print("3. Waiting for container to start...")
        time.sleep(15)
        
        print("4. FINAL VERIFICATION INSIDE CONTAINER...")
        stdin, stdout, stderr = client.exec_command("docker exec findix-backend grep 'admin' /app/routers/orders.py")
        final_evidence = stdout.read().decode()
        if "admin" in final_evidence:
            print("SUCCESS: New code is finally INSIDE the container!")
        else:
            print("FAILURE: Docker is still using old code. Investigate Dockerfile/Context.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    hard_rebuild()
