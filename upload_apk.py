"""
Script to upload just the APK to the server.
"""
import paramiko
import os

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
project_dir = '/home/yaqingo/yaqin-production'

def deploy_apk():
    print(f"Connecting to {host}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, username=user, password=password, timeout=30)
        print("Connected!")
        
        sftp = ssh.open_sftp()
        local_apk = r'findix_app\build\app\outputs\flutter-apk\app-release.apk'
        if os.path.exists(local_apk):
            print("Uploading APK...")
            sftp.put(local_apk, f'{project_dir}/downloads/findix.apk')
            print("APK uploaded.")
        else:
            print(f"Error: APK not found at {local_apk}")
            
        sftp.close()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == '__main__':
    deploy_apk()
