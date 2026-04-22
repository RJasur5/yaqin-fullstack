import paramiko
import os

def deploy_via_sftp():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    remote_base = "/home/yaqingo/yaqin-production"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    sftp = ssh.open_sftp()
    
    files_to_sync = [
        "backend/routers/auth.py",
        "backend/routers/masters.py",
        "backend/routers/orders.py",
        "backend/routers/subscriptions.py",
        "backend/utils/security.py",
        "backend/manage_db.py",
        "backend/schemas.py",
    ]
    
    for f in files_to_sync:
        local_path = f.replace("/", os.sep)
        remote_path = f"{remote_base}/{f}"
        print(f"Uploading {f} -> {remote_path}")
        try:
            sftp.put(local_path, remote_path)
        except Exception as e:
            print(f"Failed to upload {f}: {e}")
            # Try creating directory if missing
            dir_path = "/".join(remote_path.split("/")[:-1])
            ssh.exec_command(f"mkdir -p {dir_path}")
            sftp.put(local_path, remote_path)
    
    sftp.close()
    
    print("Restarting containers with rebuild...")
    cmd = f"cd {remote_base} && sudo -S docker compose up -d --build --force-recreate"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdin.write(password + "\n")
    stdin.flush()
    
    print(stdout.read().decode())
    print(stderr.read().decode())
    
    ssh.close()
    print("Deployment complete.")

if __name__ == "__main__":
    deploy_via_sftp()
