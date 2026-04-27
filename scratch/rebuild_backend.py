import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

def rebuild_backend():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, username=user, password=password)
        
        print("--- Rebuilding Backend ---")
        stdin, stdout, stderr = ssh.exec_command("cd /home/yaqingo/yaqin-production && docker compose up -d --build backend")
        
        # Stream the output
        for line in iter(stdout.readline, ""):
            print(line, end="")
        for line in iter(stderr.readline, ""):
            print(line, end="")
            
        print("\n--- Done Rebuilding ---")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    rebuild_backend()
