import paramiko
import time

def upload_secure_db():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    # 1. SFTP directly to the mounted uploads folder (since it is already mapped)
    # or just to the host then move.
    print("Uploading to host...")
    sftp = ssh.open_sftp()
    sftp.put("backend/findix.db", "/home/yaqingo/stable_old.db")
    sftp.close()
    
    # 2. Use a more robust docker cp
    print("Moving into container (Robustly)...")
    stdin, stdout, stderr = ssh.exec_command(f'sudo -S docker cp /home/yaqingo/stable_old.db findix-backend:/app/old_findix.db')
    stdin.write(password + "\n")
    stdin.flush()
    # Wait for completion
    stdout.channel.recv_exit_status()
    
    # 3. Verify size in container via python
    print("Verifying final size...")
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker exec findix-backend python3 -c 'import os; print(os.path.getsize(\"old_findix.db\"))'")
    stdin.write(password + "\n")
    stdin.flush()
    print("Final Size in Container:", stdout.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    upload_secure_db()
