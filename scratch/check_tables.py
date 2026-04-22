import paramiko

def check_tables():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    print("Checking tables in old_findix.db...")
    cmd = "sudo -S docker exec findix-backend sqlite3 old_findix.db '.tables'"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdin.write(password + "\n")
    stdin.flush()
    print("Tables:", stdout.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    check_tables()
