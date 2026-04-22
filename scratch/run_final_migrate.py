import paramiko
import time

def final_migrate():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    with open("scratch/migrate_v3.py", "r", encoding='utf-8') as f:
        code = f.read()
    
    print("Uploading migrate_v3.py...")
    ssh.exec_command(f'sudo -S docker exec -i findix-backend sh -c "cat > migrate.py"')
    stdin, stdout, stderr = ssh.exec_command(f'sudo -S docker exec -i findix-backend sh -c "cat > migrate.py"')
    stdin.write(password + "\n")
    stdin.write(code)
    stdin.close()
    
    print("Running final migration...")
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker exec findix-backend python3 migrate.py")
    stdin.write(password + "\n")
    stdin.flush()
    
    print(stdout.read().decode())
    print(stderr.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    final_migrate()
