import paramiko
import os

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

def deploy():
    print(f"Connecting to {host}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    sftp = ssh.open_sftp()
    
    project_dir = '/home/yaqingo/yaqin-production'
    
    print("Uploading APK...")
    local_apk = r'c:\Users\Jasur\.gemini\antigravity\scratch\findix\findix_app\build\app\outputs\flutter-apk\app-release.apk'
    sftp.put(local_apk, f'{project_dir}/downloads/findix.apk')
    
    sftp.close()
    ssh.close()
    print("Done APK!")

if __name__ == '__main__':
    deploy()
