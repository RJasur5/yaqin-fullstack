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
    ssh.exec_command("rm -rf ~/findix-deploy && mkdir ~/findix-deploy")
    
    print(f"Cloning {repo_url}...")
    stdin, stdout, stderr = ssh.exec_command(f"git clone {repo_url} ~/findix-deploy")
    stdout.channel.recv_exit_status()
    
    # Copy .env from old production if it exists
    print("Copying configuration...")
    ssh.exec_command("cp ~/yaqin-production/backend/.env ~/findix-deploy/backend/.env")
    ssh.exec_command("cp ~/yaqin-production/findix.db ~/findix-deploy/backend/findix.db") # Restore DB
    
    print("Restarting docker compose...")
    # Try both 'docker-compose' and 'docker compose'
    cmd = f"cd ~/findix-deploy && (sudo -S docker compose up -d --build || sudo -S docker-compose up -d --build)"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    # Send password twice just in case both cmds ask
    stdin.write(password + "\n")
    stdin.flush()
    time.sleep(1)
    stdin.write(password + "\n")
    stdin.flush()
    
    print(stdout.read().decode())
    err = stderr.read().decode()
    if err:
        print(f"Notes/Errors: {err}")
    
    ssh.close()
    print("Done!")

if __name__ == "__main__":
    import time
    sync_deploy()
