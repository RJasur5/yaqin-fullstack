import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

def hard_rebuild():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, username=user, password=password)
        print("Rebuilding backend container to ensure code update...")
        stdin, stdout, stderr = ssh.exec_command("cd /home/yaqingo/yaqin-production && docker compose up -d --build backend")
        
        # Print output to monitor progress
        for line in stdout:
            print(line.strip())
        for line in stderr:
            print(line.strip())
            
        print("Rebuild complete.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    hard_rebuild()
