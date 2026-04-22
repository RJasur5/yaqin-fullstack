import paramiko

def check_container():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    # Check directory
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker exec findix-backend pwd")
    stdin.write(password + "\n")
    stdin.flush()
    print("PWD in container:", stdout.read().decode())
    
    # Check files
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker exec findix-backend ls -la")
    stdin.write(password + "\n")
    stdin.flush()
    print("Files in container:", stdout.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    check_container()
