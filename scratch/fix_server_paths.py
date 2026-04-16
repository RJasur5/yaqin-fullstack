import paramiko

def fix_server_paths():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        print("CONNECTED!")

        def run_sudo(cmd):
            print(f"Executing: {cmd}")
            stdin, stdout, stderr = client.exec_command(f"sudo -S bash -c \"{cmd}\"", get_pty=True)
            stdin.write(password + '\n')
            stdin.flush()
            return stdout.read().decode('utf-8', 'ignore')

        yaml_path = "/var/www/yaqin/docker-compose.yml"
        
        # Replace relative paths with absolute ones
        print("Updating docker-compose.yml...")
        run_sudo(f"sed -i 's|./downloads|/var/www/yaqin/downloads|g' {yaml_path}")
        run_sudo(f"sed -i 's|./deploy|/var/www/yaqin/deploy|g' {yaml_path}")
        run_sudo(f"sed -i 's|./backend|/var/www/yaqin/backend|g' {yaml_path}")

        # Restart
        print("Restarting with absolute paths...")
        run_sudo(f"cd /var/www/yaqin && docker compose up -d")
        
        # Verify inside container
        print("Verifying file visibility inside Nginx...")
        check = run_sudo("docker exec findix-nginx ls -la /app/downloads/app.apk")
        print(f"Check result: {check}")

        if "app.apk" in check:
            print("--- SUCCESS: FILE IS NOW VISIBLE IN DOCKER ---")
        else:
            print("--- STILL MISSING ---")

    except Exception as e:
        print(f"FIX FAILED: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    fix_server_paths()
