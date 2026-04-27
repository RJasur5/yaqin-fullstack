import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

def run():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    print("--- PS ---")
    stdin, stdout, stderr = ssh.exec_command("cd /home/yaqingo/yaqin-production && docker compose ps")
    print(stdout.read().decode())
    
    print("--- BACKEND LOGS ---")
    stdin, stdout, stderr = ssh.exec_command("cd /home/yaqingo/yaqin-production && docker compose logs backend --tail 50")
    print(stdout.read().decode())
    print(stderr.read().decode())
    
    print("--- NGINX LOGS ---")
    stdin, stdout, stderr = ssh.exec_command("docker logs findix-nginx --tail 50")
    print(stdout.read().decode())
    print(stderr.read().decode())

    ssh.close()

if __name__ == '__main__':
    run()
