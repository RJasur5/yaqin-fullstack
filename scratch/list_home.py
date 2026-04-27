import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

def list_home():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, username=user, password=password)
        stdin, stdout, stderr = ssh.exec_command("ls -F /home/yaqingo")
        print("Home listing:")
        print(stdout.read().decode())
        
        stdin, stdout, stderr = ssh.exec_command("ls -F /home/yaqingo/findix")
        print("Findix listing:")
        print(stdout.read().decode())
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    list_home()
