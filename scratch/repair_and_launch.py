import paramiko
import time

def repair_and_launch():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
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
            # Wait and read
            while not stdout.channel.exit_status_ready():
                time.sleep(0.1)
            return stdout.read().decode()

        # 1. Install unzip and extract
        print("Ensuring unzip is installed...")
        run_sudo("apt-get update && apt-get install -y unzip")
        
        print("Extracting project files...")
        run_sudo("mkdir -p /var/www/yaqin")
        run_sudo("unzip -o /home/yaqingo/project.zip -d /var/www/yaqin/")
        
        # 2. Restart Docker
        print("Restarting Docker service...")
        run_sudo("systemctl restart docker")
        time.sleep(5)
        
        # 3. Final check
        print("Checking project directory...")
        res = run_sudo("ls -F /var/www/yaqin/")
        print(f"Directory content: {res}")
        
        # 4. Launch!
        print("Launching project...")
        run_sudo(f"docker compose -f /var/www/yaqin/docker-compose.yml up -d --build")
        
        print("SUCCESS!")

    except Exception as e:
        print(f"FAILED: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    repair_and_launch()
