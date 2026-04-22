import paramiko

def debug_up():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    print("Running docker compose up -d and capturing output...")
    stdin, stdout, stderr = ssh.exec_command(f'cd ~/yaqin-production && echo {password} | sudo -S docker compose up -d')
    
    print("STDOUT:")
    print(stdout.read().decode())
    print("STDERR:")
    print(stderr.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    debug_up()
