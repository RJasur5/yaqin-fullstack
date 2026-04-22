import paramiko

def check_real_db():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    print("Checking active DATABASE_URL in container...")
    cmd = "sudo -S docker exec findix-backend env | grep DATABASE_URL"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdin.write(password + "\n")
    stdin.flush()
    print(stdout.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    check_real_db()
