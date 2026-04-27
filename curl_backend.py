import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

def run():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    print("--- CURL ---")
    stdin, stdout, stderr = ssh.exec_command("curl http://localhost:8005/api/auth/login")
    print("STDOUT:", stdout.read().decode())
    print("STDERR:", stderr.read().decode())

    ssh.close()

if __name__ == '__main__':
    run()
