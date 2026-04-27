import paramiko

def finalize_persistence():
    hostname = "95.182.118.245"
    username = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        print("Connected. Finalizing persistence...")
        
        project_dir = "/home/yaqingo/project"
        
        # 1. Pull the new docker-compose.yml
        print("Pulling latest config from GitHub...")
        stdin, stdout, stderr = client.exec_command(f"cd {project_dir} && git pull origin main")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        # 2. Restart everything to apply the volume mapping
        print("Executing docker compose down && docker compose up -d...")
        # Note: We use -d to run in background. We already backed up findix.db to the host.
        # Now volume mapping (- ./backend/findix.db:/app/findix.db) will use that host file.
        stdin, stdout, stderr = client.exec_command(f"cd {project_dir} && docker compose down && docker compose up -d")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("\nFinal status check:")
        stdin, stdout, stderr = client.exec_command("docker ps")
        print(stdout.read().decode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    finalize_persistence()
