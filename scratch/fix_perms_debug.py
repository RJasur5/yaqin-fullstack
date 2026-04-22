import paramiko

def fix_permissions_and_debug():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    print("Fixing file permissions...")
    ssh.exec_command(f"echo {password} | sudo -S chmod 777 ~/yaqin-production/backend/findix.db")
    
    print("Force restarting containers again...")
    ssh.exec_command(f'cd ~/yaqin-production && echo {password} | sudo -S docker compose restart')
    
    import time
    time.sleep(5)
    
    print("Checking backend logs for startup errors...")
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker logs findix-backend --tail 50")
    stdin.write(password + "\n")
    stdin.flush()
    print("BACKEND LOGS:")
    print(stdout.read().decode())
    
    print("Checking nginx logs for 502/504 errors...")
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker logs findix-nginx --tail 50")
    stdin.write(password + "\n")
    stdin.flush()
    print("NGINX LOGS:")
    print(stdout.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    fix_permissions_and_debug()
