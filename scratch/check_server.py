import paramiko

def find_project():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    stdin, stdout, stderr = ssh.exec_command("ls -F")
    print("Files on server:")
    print(stdout.read().decode())
    
    stdin, stdout, stderr = ssh.exec_command("find . -name .git -type d")
    print("Git repos found:")
    print(stdout.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    find_project()
