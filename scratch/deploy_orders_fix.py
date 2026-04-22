import paramiko

def deploy_fix():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {host}...")
        client.connect(host, username=user, password=password, timeout=60)
        
        sftp = client.open_sftp()
        source_path = r'backend\routers\orders.py'
        dest_path = 'yaqin-production/backend/routers/orders.py'
        
        print(f"Uploading {source_path} to {dest_path}...")
        sftp.put(source_path, dest_path)
        sftp.close()
        
        print("RESTARTING BACKEND...")
        cmd = "cd yaqin-production && echo 'nEQvV9Pi8e' | sudo -S docker compose restart backend"
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("DEPLOYMENT COMPLETE!")

    except Exception as e:
        print(f"Error during deployment: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_fix()
