import paramiko

def fix_inode_issue():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    print("Uploading local db to a temporary file on the host...")
    sftp = ssh.open_sftp()
    sftp.put("backend/findix.db", "/home/yaqingo/real_db.sqlite")
    sftp.close()
    
    print("Injecting db cleanly (preserving inode)...")
    # Using 'cat' to rewrite file contents without changing the file inode
    ssh.exec_command(f"echo {password} | sudo -S sh -c 'cat /home/yaqingo/real_db.sqlite > /home/yaqingo/yaqin-production/backend/findix.db'")
    
    print("Verifying in container...")
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker exec findix-backend python3 -c 'from database import SessionLocal; from models import Order; db=SessionLocal(); print(f\"Orders inside container: {db.query(Order).count()}\"); db.close()'")
    stdin.write(password + "\n")
    stdin.flush()
    print("Check output from container:", stdout.read().decode())
    
    print("Restarting backend for safety...")
    ssh.exec_command(f"cd ~/yaqin-production && echo {password} | sudo -S docker restart findix-backend")
    
    ssh.close()
    print("DB fully restored and active!")

if __name__ == "__main__":
    fix_inode_issue()
