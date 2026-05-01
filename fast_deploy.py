import paramiko
import os

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
        sftp = ssh.open_sftp()
        
        print("Uploading backend.tar...")
        sftp.put('backend.tar', f'{project_dir}/backend.tar')
        
        print("Uploading deploy.tar...")
        sftp.put('deploy.tar', f'{project_dir}/deploy.tar')
        
        print("Uploading APK...")
        local_apk = r'findix_app\build\app\outputs\flutter-apk\app-release.apk'
        if os.path.exists(local_apk):
            sftp.put(local_apk, f'{project_dir}/downloads/findix.apk')
            print("APK uploaded.")
            
        sftp.close()
        
        # Commands to rebuild and migrate
        # We need to extract the tar files first
        full_command = f"cd {project_dir} && tar -xf backend.tar && tar -xf deploy.tar && rm backend.tar deploy.tar && (docker compose up --build -d || docker-compose up --build -d) && sleep 5 && docker compose restart nginx"
        
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
