import paramiko

def check_backend_crash():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    print("Checking backend logs for errors...")
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker logs findix-backend")
    stdin.write(password + "\n")
    stdin.flush()
    
    logs = stdout.read().decode()
    print("LOGS:")
    print(logs[-2000:]) # Last 2000 chars
    
    ssh.close()

if __name__ == "__main__":
    check_backend_crash()
