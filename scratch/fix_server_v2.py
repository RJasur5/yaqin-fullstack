import paramiko

def fix_server():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        
        # 1. Update the host's .env to use Postgres (ensure it's clean)
        env_content = """DATABASE_URL=postgresql://findix_user:findix_pass@db:5432/findix_db
SECRET_KEY=findix-secret-key-2026-change-in-production
ALGORITHM=HS256
TOKEN_EXPIRE_DAYS=30
LOG_LEVEL=INFO
"""
        client.exec_command(f"echo '{env_content}' > yaqin-production/backend/.env")
        
        # 2. Restart Docker containers using 'docker compose'
        print("Restarting Docker containers with 'docker compose'...")
        # We use -f to specify the file and avoid path issues
        cmd = "cd yaqin-production && docker compose down && docker compose up -d --build"
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        # 3. Verify APK visibility
        print("Checking APK visibility...")
        stdin, stdout, stderr = client.exec_command("docker exec findix-nginx ls -la /app/downloads")
        print(stdout.read().decode())
        
        # 4. Check backend logs for Postgres connection
        print("Checking backend logs...")
        stdin, stdout, stderr = client.exec_command("docker logs findix-backend --tail 20")
        print(stdout.read().decode())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    fix_server()
