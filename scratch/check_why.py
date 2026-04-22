import paramiko

def check_why():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker logs findix-backend --tail 50")
    stdin.write(password + "\n")
    stdin.flush()
    print("LOGS:", stdout.read().decode())
    print("ERR:", stderr.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    check_why()
