import paramiko

def sync_deploy():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    repo_url = "https://github.com/RJasur5/yaqin-fullstack.git"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    print("Setting up fresh deployment directory...")
    # 1. Create a clean deploy dir
    ssh.exec_command("rm -rf ~/findix-deploy && mkdir ~/findix-deploy")
    
    # 2. Clone the repo
    print(f"Cloning {repo_url}...")
    stdin, stdout, stderr = ssh.exec_command(f"git clone {repo_url} ~/findix-deploy")
    exit_status = stdout.channel.recv_exit_status()
    if exit_status != 0:
        print(f"Clone failed: {stderr.read().decode()}")
    
    # 3. Stop old containers (if any from this dir)
    print("Restarting docker-compose...")
    # We should stop the existing ones in yaqin-production first if we want to replace them
    # But for safety, I'll just try to scale/up in the new dir
    
    cmd = f"cd ~/findix-deploy && sudo -S docker-compose up -d --build"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdin.write(password + "\n")
    stdin.flush()
    
    print(stdout.read().decode())
    print(stderr.read().decode())
    
    ssh.close()
    print("Done!")

if __name__ == "__main__":
    sync_deploy()
