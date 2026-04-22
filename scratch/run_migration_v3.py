import paramiko

def migrate_v3():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    print("Copying findix.db into container...")
    # Make sure we use absolute paths
    cmd = f"echo {password} | sudo -S docker cp /home/yaqingo/yaqin-production/backend/findix.db findix-backend:/app/old_findix.db"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    # Verify size
    print("Verifying size...")
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker exec findix-backend ls -s old_findix.db")
    stdin.write(password + "\n")
    stdin.flush()
    print("Size in container:", stdout.read().decode())
    
    print("Running migration...")
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker exec findix-backend python3 migrate.py")
    stdin.write(password + "\n")
    stdin.flush()
    print(stdout.read().decode())
    print(stderr.read().decode())
    
    ssh.close()
    print("Done!")

if __name__ == "__main__":
    migrate_v3()
