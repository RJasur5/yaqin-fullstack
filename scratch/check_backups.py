import paramiko

def check_backups():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    # Check for findix.db and its size
    print("Checking for SQLite DB files:")
    stdin, stdout, stderr = ssh.exec_command("find ~ -name '*.db' -ls")
    print(stdout.read().decode())
    
    # Check if there are any .sql files or backups
    print("Checking for SQL dumps:")
    stdin, stdout, stderr = ssh.exec_command("find ~ -name '*.sql' -ls")
    print(stdout.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    check_backups()
