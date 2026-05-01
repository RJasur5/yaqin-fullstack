"""
Quick patch deploy - uploads only changed files and restarts backend.
"""
import paramiko
import os

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
project_dir = '/home/yaqingo/yaqin-production'

# Only the files we changed
CHANGED_FILES = [
    (r'backend\routers\orders.py', f'{project_dir}/backend/routers/orders.py'),
    (r'backend\schemas.py', f'{project_dir}/backend/schemas.py'),
    (r'backend\routers\subscriptions.py', f'{project_dir}/backend/routers/subscriptions.py'),
]

def deploy():
    print(f"Connecting to {host}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, username=user, password=password, timeout=30)
        print("Connected!")
        
        sftp = ssh.open_sftp()
        for local_path, remote_path in CHANGED_FILES:
            print(f"  Uploading {local_path} -> {remote_path}")
            sftp.put(local_path, remote_path)
        sftp.close()
        print("Files uploaded.")
        
        cmd = (
            f"cd {project_dir} && "
            f"(docker compose up --build -d || docker-compose up --build -d) && "
            f"sleep 8 && "
            f"docker compose restart nginx"
        )
        print(f"Running: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=120)
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        if out: print(f"OUTPUT:\n{out}")
        if err: print(f"STDERR:\n{err}")
        
        print("\nDeployment completed!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == '__main__':
    deploy()
