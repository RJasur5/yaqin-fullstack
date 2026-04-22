import paramiko
import time

def deep_restart():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    print("Stopping all containers...")
    ssh.exec_command(f'cd ~/yaqin-production && echo {password} | sudo -S docker compose down')
    time.sleep(5)
    
    print("Pruning docker networks (Deep clean)...")
    stdin, stdout, stderr = ssh.exec_command(f'echo {password} | sudo -S docker network prune -f')
    stdout.channel.recv_exit_status()
    
    print("Starting containers fresh with rebuild...")
    # This ensures everything is rebuilt from the SFTP-uploaded files
    cmd = 'cd ~/yaqin-production && sudo -S docker compose up -d --build --force-recreate'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdin.write(password + "\n")
    stdin.flush()
    
    print("Waiting for startup...")
    time.sleep(10)
    
    print("Verifying backend health...")
    # Check if backend responds to localhost search
    stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost/api/categories | head -c 100")
    print("Response from API:", stdout.read().decode())
    
    ssh.close()
    print("Deep Restart Done!")

if __name__ == "__main__":
    deep_restart()
