import paramiko
import os

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

def deploy():
    print(f"Connecting to {host}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    sftp = ssh.open_sftp()
    
    project_dir = '/home/yaqingo/yaqin-production'
    
    print("Uploading backend/routers/subscriptions.py...")
    sftp.put(r'c:\Users\Jasur\.gemini\antigravity\scratch\findix\backend\routers\subscriptions.py', f'{project_dir}/backend/routers/subscriptions.py')
    
    print("Uploading backend/config.py...")
    sftp.put(r'c:\Users\Jasur\.gemini\antigravity\scratch\findix\backend\config.py', f'{project_dir}/backend/config.py')
    
    print("Uploading backend/.env...")
    sftp.put(r'c:\Users\Jasur\.gemini\antigravity\scratch\findix\backend\.env', f'{project_dir}/backend/.env')
    
    sftp.close()
    
    print("Restarting backend...")
    stdin, stdout, stderr = ssh.exec_command(f'cd {project_dir} && docker compose restart backend')
    print(stdout.read().decode())
    print(stderr.read().decode())
    
    ssh.close()
    print("Done!")

if __name__ == '__main__':
    deploy()
