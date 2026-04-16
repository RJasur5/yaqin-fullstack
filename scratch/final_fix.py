import paramiko
import time

def final_fix():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        print("CONNECTED!")

        def run_cmd(command, use_sudo=False):
            print(f"Executing: {command}")
            if use_sudo:
                stdin, stdout, stderr = client.exec_command(f"sudo -S {command}", get_pty=True)
                stdin.write(password + '\n')
                stdin.flush()
            else:
                stdin, stdout, stderr = client.exec_command(command)
            return stdout.read().decode().strip()

        # 1. Unzip
        print("Extracting project.zip...")
        run_cmd("sudo unzip -o /home/yaqingo/project.zip -d /var/www/yaqin/", use_sudo=True)
        
        # 2. Check files
        print("Checking /var/www/yaqin/ content:")
        res = run_cmd("ls -F /var/www/yaqin/")
        print(res)
        
        if "docker-compose.yml" in res:
            print("Zip extracted successfully!")
            # 3. Launch Docker Compose
            print("Launching Docker Compose...")
            run_cmd("cd /var/www/yaqin && sudo docker compose up -d --build", use_sudo=True)
            print("DOCKER UP!")
        else:
            print("ERROR: docker-compose.yml NOT FOUND in extracted folder!")

    except Exception as e:
        print(f"FIX FAILED: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    final_fix()
