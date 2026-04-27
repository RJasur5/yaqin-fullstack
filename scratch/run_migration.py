import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

def run_migration():
    print(f"Connecting to {host}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, username=user, password=password)
        print("Connected!")
        
        project_dir = '/home/yaqingo/yaqin-production'
        
        # Run the migration script inside the container
        print("Running database migration...")
        cmd = "docker exec findix-backend python migrate_job_applications.py"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        print(f"OUT: {stdout.read().decode()}")
        print(f"ERR: {stderr.read().decode()}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == '__main__':
    run_migration()
