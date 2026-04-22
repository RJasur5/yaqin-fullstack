import paramiko

def rollback_to_sqlite():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    # 1. Update .env to use SQLite
    ssh.exec_command("echo 'DATABASE_URL=sqlite:///findix.db\nSECRET_KEY=findix-secret-key-2026-change-in-production\nALGORITHM=HS256\nTOKEN_EXPIRE_DAYS=30\nLOG_LEVEL=INFO' > ~/yaqin-production/backend/.env")
    
    # 2. Update docker-compose.yml locally then upload
    with open("docker-compose.yml", "r") as f:
        lines = f.readlines()
    
    # Add volume mount for findix.db
    new_compose = []
    for line in lines:
        new_compose.append(line)
        if "- ./backend/uploads:/app/uploads" in line:
            new_compose.append("      - ./backend/findix.db:/app/findix.db\n")
            
    with open("scratch/docker-compose-rollback.yml", "w") as f:
        f.writelines(new_compose)
    
    sftp = ssh.open_sftp()
    sftp.put("scratch/docker-compose-rollback.yml", "/home/yaqingo/yaqin-production/docker-compose.yml")
    sftp.close()
    
    print("Restarting with SQLite...")
    ssh.exec_command(f'cd ~/yaqin-production && echo {password} | sudo -S docker compose down')
    ssh.exec_command(f'cd ~/yaqin-production && echo {password} | sudo -S docker compose up -d')
    
    ssh.close()
    print("Rollback Complete!")

if __name__ == "__main__":
    rollback_to_sqlite()
