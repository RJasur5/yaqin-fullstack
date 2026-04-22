import paramiko

def check_dirs():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    for d in ["project", "yaqin-production"]:
        print(f"Contents of {d}:")
        stdin, stdout, stderr = ssh.exec_command(f"ls -la {d}")
        print(stdout.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    check_dirs()
