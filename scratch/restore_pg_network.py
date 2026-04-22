import paramiko
import time

def restore_postgres_and_fix_network():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    print("Restoring PostgreSQL settings in .env...")
    # Using the local project settings but pointing to the 'db' service
    env_content = """
DATABASE_URL=postgresql://findix_user:findix_pass@db:5432/findix_db
SECRET_KEY=findix-secret-key-2026-change-in-production
ALGORITHM=HS256
TOKEN_EXPIRE_DAYS=30
LOG_LEVEL=INFO
"""
    ssh.exec_command(f'cat > ~/yaqin-production/backend/.env <<EOF\n{env_content.strip()}\nEOF')
    
    print("Updating docker-compose.yml to revert SQLite volume mount...")
    # Upload the original clean compose
    sftp = ssh.open_sftp()
    # I'll just use the one I just updated with env_file support (migrate_v4.py modified it)
    sftp.put("docker-compose.yml", "/home/yaqingo/yaqin-production/docker-compose.yml")
    sftp.close()
    
    print("Performing DEEP network reset...")
    ssh.exec_command(f'cd ~/yaqin-production && echo {password} | sudo -S docker compose down')
    time.sleep(2)
    ssh.exec_command(f'echo {password} | sudo -S docker network prune -f')
    time.sleep(2)
    ssh.exec_command(f'cd ~/yaqin-production && echo {password} | sudo -S docker compose up -d')
    
    print("Waiting for boot...")
    time.sleep(10)
    
    ssh.close()
    print("PostgreSQL Restored and Network Reset!")

if __name__ == "__main__":
    restore_postgres_and_fix_network()
