import paramiko
import sys
import time

def deploy():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"

    print(f"Connecting to {host}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname=host, username=user, password=password)
        print("Connected successfully!")

        def run_sudo(command):
            print(f"Executing: {command}")
            stdin, stdout, stderr = client.exec_command(f"sudo -S {command}", get_pty=True)
            stdin.write(password + '\n')
            stdin.flush()
            
            # Print output
            output = stdout.read().decode()
            print(f"  {output.strip()}")
            
            err = stderr.read().decode()
            if err:
                print(f"  Error: {err}")

        # 1. Fix dpkg
        print("Fixing interrupted dpkg...")
        run_sudo("dpkg --configure -a")
        
        # 2. Fix CD-ROM issue again just in case
        run_sudo("sed -i '/cdrom/d' /etc/apt/sources.list")
        
        # 3. Update and Install Docker
        print("Cleaning up and updating apt...")
        run_sudo("apt-get update")
        
        print("Installing Docker...")
        client.exec_command("curl -fsSL https://get.docker.com -o get-docker.sh")
        run_sudo("sh get-docker.sh")
        
        # 3. Add user to docker group
        run_sudo(f"usermod -aG docker {user}")
        
        # 5. Check if it worked
        print("Verifying installation...")
        stdin, stdout, stderr = client.exec_command("docker --version")
        print(f"Result: {stdout.read().decode().strip()}")

    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        client.close()
        print("Connection closed.")

if __name__ == "__main__":
    deploy()
