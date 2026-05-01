import paramiko
import os

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

def run():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=10)
    
    sftp = ssh.open_sftp()
    
    local_apk = r'c:\Users\Jasur\.gemini\antigravity\scratch\findix\findix_app\build\app\outputs\flutter-apk\app-release.apk'
    remote_apk = '/home/yaqingo/yaqin-production/downloads/findix-v3.apk'
    
    print("Uploading APK...")
    sftp.put(local_apk, remote_apk)
    print("Uploaded!")

    sftp.close()
    ssh.close()

if __name__ == '__main__':
    run()
