import paramiko

def fix_backend():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {host}...")
        client.connect(host, username=user, password=password, timeout=60)
        
        sftp = client.open_sftp()
        print("Uploading requirements.txt...")
        sftp.put('backend/requirements.txt', 'yaqin-production/backend/requirements.txt')
        sftp.close()
        
        # Use many tiny steps to avoid quoting issues
        print("Step 1: Building new image (this takes ~1 min)...")
        # Note: We build with a new tag to be absolutely sure
        cmd_build = "cd yaqin-production/backend && echo 'nEQvV9Pi8e' | sudo -S docker build --no-cache -t findix-backend:v-final ."
        stdin, stdout, stderr = client.exec_command(cmd_build)
        out = stdout.read().decode()
        err = stderr.read().decode()
        print("Build output processed.")
        
        print("Step 2: Updating docker-compose.yml to use the new image...")
        # We'll just sed the image name in docker-compose.yml
        cmd_sed = "cd yaqin-production && sed -i 's/build: ./image: findix-backend:v-final/g' docker-compose.yml"
        client.exec_command(cmd_sed)
        
        print("Step 3: Starting the container with the new image...")
        cmd_up = "cd yaqin-production && echo 'nEQvV9Pi8e' | sudo -S docker compose up -d backend"
        stdin, stdout, stderr = client.exec_command(cmd_up)
        print("Backend restarted.")
        
        print("--- VERIFICATION ---")
        import time
        time.sleep(5)
        stdin, stdout, stderr = client.exec_command("docker ps")
        print(stdout.read().decode())
        
        stdin, stdout, stderr = client.exec_command("docker logs --tail 20 findix-backend")
        print("Final Logs:\n", stdout.read().decode())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    fix_backend()
