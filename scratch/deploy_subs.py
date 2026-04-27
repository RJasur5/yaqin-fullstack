import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

def deploy():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, username=user, password=password)
        sftp = ssh.open_sftp()
        
        print("Uploading subscriptions.py...")
        sftp.put(r'c:\Users\Jasur\.gemini\antigravity\scratch\findix\backend\routers\subscriptions.py', '/home/yaqingo/yaqin-production/backend/routers/subscriptions.py')
        
        print("Restarting backend...")
        ssh.exec_command("cd /home/yaqingo/yaqin-production && docker compose restart backend")
        print("Deployment successful.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy()
