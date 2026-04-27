import paramiko
import os

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

def deploy_nginx_fix():
    print(f"Connecting to {host}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, username=user, password=password)
        print("Connected!")
        
        project_dir = '/home/yaqingo/yaqin-production'
        
        print("Restarting Nginx with 'docker compose'...")
        cmd = f"cd {project_dir} && docker compose restart nginx"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(f"OUT: {stdout.read().decode()}")
        print(f"ERR: {stderr.read().decode()}")
        print("Nginx restart command sent.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == '__main__':
    deploy_nginx_fix()
