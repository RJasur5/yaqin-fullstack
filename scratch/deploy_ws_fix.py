import paramiko
import io

def deploy_ws_fix():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    # Read updated local files
    with open('backend/requirements.txt', 'r') as f:
        req_content = f.read()
    with open('deploy/nginx.conf', 'r') as f:
        nginx_content = f.read()

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        print("CONNECTED!")
        
        sftp = client.open_sftp()
        
        # 1. Update files on server
        print("Uploading updated requirements.txt...")
        sftp.putfo(io.BytesIO(req_content.encode()), "/var/www/yaqin/backend/requirements.txt")
        
        print("Uploading updated nginx.conf...")
        sftp.putfo(io.BytesIO(nginx_content.encode()), "/var/www/yaqin/deploy/nginx.conf")
        sftp.close()

        # 2. Rebuild and restart
        print("Rebuilding backend with WebSocket support...")
        stdin, stdout, stderr = client.exec_command("sudo -S docker compose -f /var/www/yaqin/docker-compose.yml up -d --build", get_pty=True)
        stdin.write(password + '\n')
        stdin.flush()
        
        # Read output to ensure completion
        print("Waiting for build to finish (this may take a minute)...")
        print(stdout.read().decode('utf-8', 'ignore'))

        print("--- DEPLOY COMPLETE! ---")

    except Exception as e:
        print(f"DEPLOY FIX FAILED: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_ws_fix()
