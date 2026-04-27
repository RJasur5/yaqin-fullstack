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
        local_nginx_conf = r'c:\Users\Jasur\.gemini\antigravity\scratch\findix\deploy\nginx.conf'
        remote_nginx_conf = f"{project_dir}/deploy/nginx.conf"
        
        print(f"Uploading {local_nginx_conf} to {remote_nginx_conf}...")
        sftp = ssh.open_sftp()
        sftp.put(local_nginx_conf, remote_nginx_conf)
        sftp.close()
        print("Upload successful!")
        
        print("Restarting Nginx...")
        cmd = f"cd {project_dir} && docker-compose restart nginx"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode())
        print(stderr.read().decode())
        print("Nginx restarted!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == '__main__':
    deploy_nginx_fix()
