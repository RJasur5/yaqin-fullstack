import paramiko

def verify_db_url():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker exec findix-backend cat .env")
    stdin.write(password + "\n")
    stdin.flush()
    print("Container .env:", stdout.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    verify_db_url()
