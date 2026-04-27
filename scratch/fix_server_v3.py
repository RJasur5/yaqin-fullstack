import paramiko

def fix_server():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        
        # 1. More aggressive cleanup
        print("Stopping and removing all related containers...")
        cmds = [
            "docker stop findix-nginx findix-backend findix-db || true",
            "docker rm findix-nginx findix-backend findix-db || true",
            "cd yaqin-production && docker compose up -d --build"
        ]
        
        for cmd in cmds:
            print(f"--- Running: {cmd} ---")
            stdin, stdout, stderr = client.exec_command(cmd)
            print(stdout.read().decode())
            print(stderr.read().decode())
            
        # 2. Check APK visibility
        print("Checking APK visibility in Nginx container...")
        stdin, stdout, stderr = client.exec_command("docker exec findix-nginx ls -la /app/downloads")
        print(stdout.read().decode())
        
        # 3. Check if backend is using Postgres
        print("Checking backend logs for DB connection...")
        stdin, stdout, stderr = client.exec_command("docker logs findix-backend --tail 50")
        print(stdout.read().decode())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    fix_server()
