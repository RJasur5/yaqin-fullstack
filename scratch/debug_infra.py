import paramiko

def check_server_status():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    # 1. Check docker containers
    stdin, stdout, stderr = ssh.exec_command("docker ps")
    print("Docker PS:")
    print(stdout.read().decode())
    
    # 2. Check if anything is listening on port 80
    stdin, stdout, stderr = ssh.exec_command("sudo -S netstat -tuln | grep :80")
    stdin.write(password + "\n")
    stdin.flush()
    print("Netstat :80:")
    print(stdout.read().decode())
    
    # 3. Check logs of nginx
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker logs findix-nginx --tail 10")
    stdin.write(password + "\n")
    stdin.flush()
    print("Nginx logs:")
    print(stdout.read().decode())
    
    # 4. Try to access api internally
    stdin, stdout, stderr = ssh.exec_command("curl -I http://localhost/api/categories")
    print("Local curl check:")
    print(stdout.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    check_server_status()
