import paramiko

def force_up():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    stdin, stdout, stderr = ssh.exec_command(f'cd ~/yaqin-production && echo {password} | sudo -S docker compose up -d')
    stdin.write(password + "\n")
    stdin.flush()
    print("UP:", stdout.read().decode())
    print("ERR:", stderr.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    force_up()
