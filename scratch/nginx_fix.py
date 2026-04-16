import paramiko
import time

def final_nginx_fix():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    local_nginx = "deploy/nginx.conf"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        print("CONNECTED!")

        def run_sudo(command):
            print(f"Executing: {command}")
            stdin, stdout, stderr = client.exec_command(f"sudo -S {command}", get_pty=True)
            stdin.write(password + '\n')
            stdin.flush()
            return stdout.read().decode()

        # 1. Upload to home folder
        transport = client.get_transport()
        sftp = paramiko.SFTPClient.from_transport(transport)
        print("Uploading nginx fix to home...")
        sftp.put(local_nginx, "/home/yaqingo/nginx_fix.conf")
        sftp.close()

        # 2. Move to destination and Restart
        print("Applying nginx fix and launching...")
        run_sudo("mkdir -p /var/www/yaqin/deploy")
        run_sudo("cp /home/yaqingo/nginx_fix.conf /var/www/yaqin/deploy/nginx.conf")
        
        # Ensure downloads folder mapping is correct
        run_sudo("mkdir -p /var/www/yaqin/downloads")
        run_sudo("cp /home/yaqingo/app-release.apk /var/www/yaqin/downloads/app.apk")
        
        # Start Docker
        run_sudo("cd /var/www/yaqin && docker compose up -d --build")
        
        # Reload nginx explicitly
        run_sudo("docker exec findix-nginx nginx -s reload || docker restart findix-nginx")
        
        print("DONE! Site should be live at yaqingo.uz and api.yaqingo.uz on port 80.")

    except Exception as e:
        print(f"FIX FAILED: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    final_nginx_fix()
