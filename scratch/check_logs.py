import paramiko

def check_nginx_logs():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    # Show last 20 access logs
    print("Nginx Access Logs:")
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker logs findix-nginx --tail 20")
    stdin.write(password + "\n")
    stdin.flush()
    print(stdout.read().decode())
    
    # Show backend logs for login attempt
    print("Backend Logs:")
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker logs findix-backend --tail 20")
    stdin.write(password + "\n")
    stdin.flush()
    print(stdout.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    check_nginx_logs()
