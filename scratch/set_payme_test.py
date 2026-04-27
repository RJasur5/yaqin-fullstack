import paramiko
import os

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

local_file = r'c:\Users\Jasur\.gemini\antigravity\scratch\findix\backend\services\payme_service.py'
remote_file = '/home/yaqingo/yaqin-production/backend/services/payme_service.py'

def deploy_payme_test():
    print(f"Connecting to {host}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, username=user, password=password)
        print("Connected.")

        # Upload updated payme_service.py
        sftp = ssh.open_sftp()
        print(f"Uploading {local_file} to {remote_file}...")
        sftp.put(local_file, remote_file)
        sftp.close()

        # Update .env and restart
        commands = [
            "sed -i 's/PAYME_USE_TEST=.*/PAYME_USE_TEST=true/' /home/yaqingo/yaqin-production/backend/.env",
            "cd /home/yaqingo/yaqin-production && docker compose restart backend"
        ]

        for cmd in commands:
            print(f"Running: {cmd}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            print(stdout.read().decode())
            print(stderr.read().decode())

        print("Payme test mode deployed and backend restarted.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy_payme_test()
