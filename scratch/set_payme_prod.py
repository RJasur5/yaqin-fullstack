import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

def set_payme_production():
    print(f"Connecting to {host}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, username=user, password=password)
        print("Connected!")
        
        env_path = '/home/yaqingo/yaqin-production/backend/.env'
        project_dir = '/home/yaqingo/yaqin-production'
        
        # Update PAYME_USE_TEST to false
        print("Switching Payme to production mode...")
        cmd = f"sed -i 's/PAYME_USE_TEST=true/PAYME_USE_TEST=false/g' {env_path}"
        ssh.exec_command(cmd)
        
        # Rebuild and restart the backend container
        print("Rebuilding and restarting backend...")
        cmd = f"cd {project_dir} && docker compose up -d --build backend"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        for line in stdout:
            print(f"OUT: {line.strip()}")
        for line in stderr:
            print(f"ERR: {line.strip()}")
            
        print("\nPayme switched to production successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == '__main__':
    set_payme_production()
