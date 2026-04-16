import paramiko

def final_victory():
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

        conf_path = "/var/www/yaqin/deploy/nginx.conf"
        
        # 1. Precise replace with sed
        print("Fixing Nginx Config (alias -> root)...")
        # Use a more robust sed pattern to avoid escaping issues
        run_sudo(f"sed -i 's|alias /app/downloads/app.apk;|root /app/downloads;|g' {conf_path}")

        # 2. Restart Nginx
        print("Restarting Nginx...")
        run_sudo("docker restart findix-nginx")
        
        # 3. Final Check from server side
        print("Verifying link from server-side...")
        check = run_sudo("curl -I http://localhost/app.apk")
        print(f"CURL result: {check}")

        if "200 OK" in check:
            print("--- !!! FINAL VICTORY !!! ---")
        else:
            print("--- STILL ISSUES, CHECKING FOLDER... ---")
            run_sudo("ls -la /app/downloads") # In case it's wrong

    except Exception as e:
        print(f"VICTORY SCRIPT FAILED: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    final_victory()
