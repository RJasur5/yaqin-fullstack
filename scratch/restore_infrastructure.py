import paramiko

def restore():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {host}...")
        client.connect(host, username=user, password=password, timeout=60)
        
        print("STARTING ALL SERVICES (Nginx, DB, Backend)...")
        # Full restart of all services to ensure Nginx is up
        cmd = "cd yaqin-production && echo 'nEQvV9Pi8e' | sudo -S docker compose up -d"
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("CHECKING CONTAINER STATUS...")
        stdin, stdout, stderr = client.exec_command("docker ps")
        print(stdout.read().decode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    restore()
