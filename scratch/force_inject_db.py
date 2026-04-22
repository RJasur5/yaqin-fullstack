import paramiko

def force_inject_db_final():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    print("Uploading local findix.db to exact production path...")
    sftp = ssh.open_sftp()
    # Close any potential open handle by uploading to a tmp file first
    sftp.put("backend/findix.db", "/home/yaqingo/final_inject.db")
    sftp.close()
    
    # Move to the correct place and set permissions
    print("Applying file to backend folder...")
    ssh.exec_command(f"cp /home/yaqingo/final_inject.db ~/yaqin-production/backend/findix.db")
    ssh.exec_command(f"chmod 777 ~/yaqin-production/backend/findix.db")
    
    print("Restarting backend to refresh connection...")
    ssh.exec_command(f"cd ~/yaqin-production && echo {password} | sudo -S docker restart findix-backend")
    
    ssh.close()
    print("Data Injected and Backend Restarted!")

if __name__ == "__main__":
    force_inject_db_final()
