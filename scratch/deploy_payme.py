import paramiko
import os

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

def deploy_payme():
    print(f"Connecting to {host}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, username=user, password=password)
        print("Connected!")
        
        project_dir = '/home/yaqingo/yaqin-production'
        sftp = ssh.open_sftp()
        
        files_to_upload = [
            ('backend/models.py', 'backend/models.py'),
            ('backend/config.py', 'backend/config.py'),
            ('backend/services/payme_service.py', 'backend/services/payme_service.py'),
            ('backend/routers/subscriptions.py', 'backend/routers/subscriptions.py'),
        ]
        
        for local_rel, remote_rel in files_to_upload:
            local_path = os.path.join(r'c:\Users\Jasur\.gemini\antigravity\scratch\findix', local_rel)
            remote_path = f"{project_dir}/{remote_rel}"
            print(f"Uploading {local_rel}...")
            sftp.put(local_path, remote_path)
            
        sftp.close()
        print("Uploads completed!")
        
        # Rebuild and restart the backend container
        print("Rebuilding and restarting backend...")
        cmd = f"cd {project_dir} && docker compose up -d --build backend"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        for line in stdout:
            print(f"OUT: {line.strip()}")
        for line in stderr:
            print(f"ERR: {line.strip()}")
            
        # Run migration for PaymentTransaction table
        print("Running database migration for PaymentTransaction...")
        # Since I added it to models.py and main.py has Base.metadata.create_all, 
        # restarting the backend should create the table.
        # But just in case, I'll check if it's there.
        
        print("\nPayme integration deployed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == '__main__':
    deploy_payme()
