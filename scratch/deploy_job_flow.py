import paramiko
import os

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

base_dir = r'c:\Users\Jasur\.gemini\antigravity\scratch\findix\backend'
files_to_upload = [
    'routers/job_applications.py',
    'routers/orders.py',
    'schemas.py'
]

def deploy_job_flow():
    print(f"Connecting to {host}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, username=user, password=password)
        print("Connected.")

        sftp = ssh.open_sftp()
        for rel_path in files_to_upload:
            local_path = os.path.join(base_dir, rel_path.replace('/', os.sep))
            remote_path = f'/home/yaqingo/yaqin-production/backend/{rel_path}'
            print(f"Uploading {local_path} to {remote_path}...")
            sftp.put(local_path, remote_path)
        sftp.close()

        # Restart backend
        print("Restarting backend...")
        ssh.exec_command("cd /home/yaqingo/yaqin-production && docker compose restart backend")
        print("Deployment successful.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy_job_flow()
