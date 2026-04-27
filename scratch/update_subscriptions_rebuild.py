import paramiko
import os

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

def update_subscriptions_and_rebuild():
    print(f"Connecting to {host}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, username=user, password=password)
        print("Connected!")
        
        project_dir = '/home/yaqingo/yaqin-production'
        local_file = r'c:\Users\Jasur\.gemini\antigravity\scratch\findix\backend\routers\subscriptions.py'
        remote_file = f"{project_dir}/backend/routers/subscriptions.py"
        
        print(f"Uploading {local_file} to {remote_file}...")
        sftp = ssh.open_sftp()
        sftp.put(local_file, remote_file)
        sftp.close()
        print("Upload successful!")
        
        # Rebuild and restart the backend container
        print("Rebuilding and restarting backend...")
        cmd = f"cd {project_dir} && docker compose up -d --build backend"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        for line in stdout:
            print(f"OUT: {line.strip()}")
        for line in stderr:
            print(f"ERR: {line.strip()}")
            
        print("\nBackend updated and rebuilt successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == '__main__':
    update_subscriptions_and_rebuild()
