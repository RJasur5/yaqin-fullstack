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
        
        print("Uploading orders.py...")
        sftp.put(r'c:\Users\Jasur\.gemini\antigravity\scratch\findix\backend\routers\orders.py', '/home/yaqingo/yaqin-production/backend/routers/orders.py')
        
        print("Uploading subscriptions.py...")
        sftp.put(r'c:\Users\Jasur\.gemini\antigravity\scratch\findix\backend\routers\subscriptions.py', '/home/yaqingo/yaqin-production/backend/routers/subscriptions.py')
        
        print("Uploading schemas.py...")
        sftp.put(r'c:\Users\Jasur\.gemini\antigravity\scratch\findix\backend\schemas.py', '/home/yaqingo/yaqin-production/backend/schemas.py')
        
        print("Uploading click_service.py...")
        sftp.put(r'c:\Users\Jasur\.gemini\antigravity\scratch\findix\backend\services\click_service.py', '/home/yaqingo/yaqin-production/backend/services/click_service.py')
        
        print("Uploading job_applications.py...")
        sftp.put(r'c:\Users\Jasur\.gemini\antigravity\scratch\findix\backend\routers\job_applications.py', '/home/yaqingo/yaqin-production/backend/routers/job_applications.py')
        
        print("Uploading security.py...")
        sftp.put(r'c:\Users\Jasur\.gemini\antigravity\scratch\findix\backend\utils\security.py', '/home/yaqingo/yaqin-production/backend/utils/security.py')
        
        sftp.close()
        
        print("Rebuilding backend...")
        stdin, stdout, stderr = ssh.exec_command("cd /home/yaqingo/yaqin-production && docker compose up -d --build backend")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("Done!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy()
