import paramiko
import os

def migrate_v2():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    print("Reading migration script...")
    with open("scratch/migrate.py", "r", encoding='utf-8') as f:
        code = f.read()
    
    # 1. Write migration script into container via stdin redirection
    print("Injecting migrate.py into container...")
    ssh.exec_command(f'sudo -S docker exec -i findix-backend sh -c "cat > migrate.py"')
    stdin, stdout, stderr = ssh.exec_command(f'sudo -S docker exec -i findix-backend sh -c "cat > migrate.py"')
    stdin.write(password + "\n") # sudo pass
    stdin.write(code)
    stdin.close()
    
    # 2. Inject SQLite file into container
    print("Injecting findix.db into container...")
    # Read local bytes of the SQLite file via SSH from the remote host
    # Or just use docker cp correctly
    ssh.exec_command(f'echo {password} | sudo -S docker cp /home/yaqingo/yaqin-production/backend/findix.db findix-backend:/app/old_findix.db')
    
    print("Verifying files in container...")
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker exec findix-backend ls -la migrate.py old_findix.db")
    stdin.write(password + "\n")
    stdin.flush()
    print(stdout.read().decode())
    
    print("Running migration...")
    cmd = "sudo -S docker exec findix-backend python3 migrate.py"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdin.write(password + "\n")
    stdin.flush()
    
    print(stdout.read().decode())
    print(stderr.read().decode())
    
    ssh.close()
    print("Done!")

if __name__ == "__main__":
    migrate_v2()
