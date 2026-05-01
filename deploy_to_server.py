import paramiko
import os
import stat

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

def deploy():
    print(f"Connecting to {host} as {user}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, username=user, password=password, timeout=30)
        print("Connected successfully!")

        
        project_dir = '/home/yaqingo/yaqin-production'
        print(f"Project directory found at: {project_dir}")
        
        # Upload backend files
        print("Uploading backend files...")
        local_backend = r'c:\Users\Jasur\.gemini\antigravity\scratch\findix\backend'
        remote_backend = f"{project_dir}/backend"
        
        sftp = ssh.open_sftp()
        
        # Make sure remote backend exists
        try:
            sftp.stat(remote_backend)
        except FileNotFoundError:
            sftp.mkdir(remote_backend)
            
        # Recursive upload function
        def upload_dir(local_dir, remote_dir):
            for item in os.listdir(local_dir):
                # skip pycache and virtual environments
                if item in ['.git', '__pycache__', 'venv', 'env', 'findix.db']:
                    continue
                    
                local_path = os.path.join(local_dir, item)
                remote_path = f"{remote_dir}/{item}"
                
                if os.path.isfile(local_path):
                    print(f"  Uploading {local_path} to {remote_path}")
                    sftp.put(local_path, remote_path)
                elif os.path.isdir(local_path):
                    try:
                        sftp.stat(remote_path)
                    except FileNotFoundError:
                        sftp.mkdir(remote_path)
                    upload_dir(local_path, remote_path)
        
        upload_dir(local_backend, remote_backend)
        print("Backend files uploaded.")
        
        # Upload deploy files
        print("Uploading deploy files...")
        local_deploy = r'c:\Users\Jasur\.gemini\antigravity\scratch\findix\deploy'
        remote_deploy = f"{project_dir}/deploy"
        try:
            sftp.stat(remote_deploy)
        except FileNotFoundError:
            sftp.mkdir(remote_deploy)
        upload_dir(local_deploy, remote_deploy)
        
        # Upload docker-compose.yml
        print("Uploading docker-compose.yml...")
        local_compose = r'c:\Users\Jasur\.gemini\antigravity\scratch\findix\docker-compose.yml'
        remote_compose = f"{project_dir}/docker-compose.yml"
        sftp.put(local_compose, remote_compose)
        
        # Upload APK
        print("Uploading new APK...")
        local_apk = r'c:\Users\Jasur\.gemini\antigravity\scratch\findix\findix_app\build\app\outputs\flutter-apk\app-release.apk'
        remote_apk_dir = f"{project_dir}/downloads"
        remote_apk = f"{remote_apk_dir}/findix.apk"

        try:
            sftp.stat(remote_apk_dir)
        except FileNotFoundError:
            sftp.mkdir(remote_apk_dir)
            
        if os.path.exists(local_apk):
            sftp.put(local_apk, remote_apk)
            print("APK uploaded successfully!")
        else:
            print(f"APK not found at {local_apk}. Skipping APK upload.")
            
        sftp.close()
        
        # Commands to rebuild and migrate
        # Restart EVERYTHING to apply nginx changes
        full_command = f"cd {project_dir} && (docker compose up --build -d || docker-compose up --build -d) && sleep 5 && docker compose restart nginx && docker exec findix-backend python migrate_company_mode.py && docker exec findix-backend python normalize_phones.py && docker exec findix-backend python migrate_payme.py && docker exec findix-backend python migrate_regions.py"
        
        print(f"Running: {full_command}")
        stdin, stdout, stderr = ssh.exec_command(full_command)
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        if out: print(f"  Output: {out}")
        if err: print(f"  Error: {err}")
            
        print("Deployment completed!")
        
    except Exception as e:
        print(f"Error during deployment: {e}")
    finally:
        ssh.close()

if __name__ == '__main__':
    deploy()
