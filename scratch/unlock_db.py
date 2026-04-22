import paramiko

def unlock_and_fix():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    print("Removing SQLite journals and temporary files...")
    # These often cause locks if a process dies
    ssh.exec_command("rm -f ~/yaqin-production/backend/findix.db-journal")
    ssh.exec_command("rm -f ~/yaqin-production/backend/findix.db-shm")
    ssh.exec_command("rm -f ~/yaqin-production/backend/findix.db-wal")
    
    print("Hard-restarting Docker containers to kill any hanging connections...")
    ssh.exec_command(f'cd ~/yaqin-production && echo {password} | sudo -S docker compose down')
    ssh.exec_command(f'cd ~/yaqin-production && echo {password} | sudo -S docker compose up -d')
    
    ssh.close()
    print("Database Unlocked!")

if __name__ == "__main__":
    unlock_and_fix()
