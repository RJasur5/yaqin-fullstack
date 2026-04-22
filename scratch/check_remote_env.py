import paramiko

def check_env():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    stdin, stdout, stderr = ssh.exec_command("cat ~/yaqin-production/backend/.env")
    print(stdout.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    check_env()
