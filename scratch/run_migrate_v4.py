import paramiko

def final_migrate_v4():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    print("Uploading migrate_v4.py...")
    sftp = ssh.open_sftp()
    sftp.put("scratch/migrate_v4.py", "/home/yaqingo/migrate.py")
    sftp.close()
    
    ssh.exec_command(f'echo {password} | sudo -S docker cp /home/yaqingo/migrate.py findix-backend:/app/migrate.py')
    
    print("Running migration v4...")
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker exec findix-backend python3 migrate.py")
    stdin.write(password + "\n")
    stdin.flush()
    
    print(stdout.read().decode())
    print(stderr.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    final_migrate_v4()
