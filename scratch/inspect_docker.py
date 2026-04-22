import paramiko

def check_docker():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker ps")
    stdin.write(password + "\n")
    stdin.flush()
    print("Docker PS:")
    print(stdout.read().decode())
    
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker inspect findix-backend")
    stdin.write(password + "\n")
    stdin.flush()
    print("Docker Inspect Backend:")
    # Look for "Source" or "Mounts"
    print(stdout.read().decode()[:1000]) # first 1000 chars
    
    ssh.close()

if __name__ == "__main__":
    check_docker()
