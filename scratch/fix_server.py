import paramiko

def fix_server():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        
        # 1. Update the host's .env to use Postgres (double check)
        env_content = """# Database configuration
DATABASE_URL=postgresql://findix_user:findix_pass@db:5432/findix_db

# Security
SECRET_KEY=findix-secret-key-2026-change-in-production
ALGORITHM=HS256
TOKEN_EXPIRE_DAYS=30

# Logging
LOG_LEVEL=INFO
"""
        # Write .env to host
        print("Updating .env on host...")
        stdin, stdout, stderr = client.exec_command(f"echo '{env_content}' > yaqin-production/backend/.env")
        stdout.read(); stderr.read()
        
        # 2. Check for host Nginx
        print("Checking for host Nginx...")
        stdin, stdout, stderr = client.exec_command("ps aux | grep nginx")
        print(stdout.read().decode())
        
        # 3. Restart Docker containers with rebuild
        print("Restarting Docker containers...")
        stdin, stdout, stderr = client.exec_command("cd yaqin-production && docker-compose down && docker-compose up -d --build")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        # 4. Check APK visibility again
        print("Checking APK visibility in Nginx container...")
        stdin, stdout, stderr = client.exec_command("docker exec findix-nginx ls -la /app/downloads")
        print(stdout.read().decode())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    fix_server()
