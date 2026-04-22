import paramiko
import time

def deploy():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print(f"Connecting to {host}...")
    ssh.connect(host, username=user, password=password)
    
    commands = [
        "cd yaqin-fullstack || cd findix-fullstack || cd *fullstack || ls", # Try to find the dir
        "git pull origin master",
        "sudo docker-compose up -d --build"
    ]
    
    for cmd in commands:
        print(f"Running: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        # If sudo asks for password
        if "sudo" in cmd:
            stdin.write(password + "\n")
            stdin.flush()
            
        exit_status = stdout.channel.recv_exit_status()
        print(f"STDOUT: {stdout.read().decode()}")
        print(f"STDERR: {stderr.read().decode()}")
        print(f"Status: {exit_status}")
    
    ssh.close()
    print("Deployment finished.")

if __name__ == "__main__":
    try:
        deploy()
    except Exception as e:
        print(f"Error: {e}")
