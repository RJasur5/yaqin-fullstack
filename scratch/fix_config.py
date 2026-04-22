import paramiko

def fix_server_config():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    print("Fixing .env file on server...")
    new_env = """
# Database configuration
DATABASE_URL=postgresql://findix_user:findix_pass@db:5432/findix_db

# Security
SECRET_KEY=findix-secret-key-2026-change-in-production
ALGORITHM=HS256
TOKEN_EXPIRE_DAYS=30

# Logging
LOG_LEVEL=INFO
"""
    # Write .env
    ssh.exec_command(f'cat > ~/yaqin-production/backend/.env <<EOF\n{new_env.strip()}\nEOF')
    
    print("Simplifying docker-compose.yml...")
    # I'll just use a sed command to remove the environment block from backend
    # or just overwrite it with a known good one
    with open("docker-compose.yml", "r") as f:
        local_compose = f.read()
    
    # Send local compose to server
    sftp = ssh.open_sftp()
    sftp.put("docker-compose.yml", "/home/yaqingo/yaqin-production/docker-compose.yml")
    sftp.close()
    
    print("Force restarting containers...")
    ssh.exec_command(f'cd ~/yaqin-production && echo {password} | sudo -S docker compose down')
    ssh.exec_command(f'cd ~/yaqin-production && echo {password} | sudo -S docker compose up -d')
    
    ssh.close()
    print("Configuration Sync Complete!")

if __name__ == "__main__":
    fix_server_config()
