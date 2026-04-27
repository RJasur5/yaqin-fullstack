import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

def check_remote_paths():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, username=user, password=password)
        stdin, stdout, stderr = ssh.exec_command("find /home/yaqingo/findix -name payme_service.py")
        print("Found payme_service.py at:")
        print(stdout.read().decode())
        
        stdin, stdout, stderr = ssh.exec_command("ls -R /home/yaqingo/findix/backend/services")
        print("Backend services listing:")
        print(stdout.read().decode())
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check_remote_paths()
