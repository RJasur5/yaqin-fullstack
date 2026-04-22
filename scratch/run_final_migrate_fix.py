import paramiko
import os

def final_migrate_fix():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    # 1. Upload to host
    print("Uploading migrate_v3.py to host...")
    sftp = ssh.open_sftp()
    sftp.put("scratch/migrate_v3.py", "/home/yaqingo/migrate.py")
    sftp.close()
    
    # 2. Docker cp
    print("Copying to container...")
    ssh.exec_command(f'echo {password} | sudo -S docker cp /home/yaqingo/migrate.py findix-backend:/app/migrate.py')
    
    # 3. Double check content via python (safer than cat)
    print("Running migration v3...")
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker exec findix-backend python3 migrate.py")
    stdin.write(password + "\n")
    stdin.flush()
    
    print(stdout.read().decode())
    print(stderr.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    final_migrate_fix()
