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
    
    print("Uploading APK in chunks...")
    local_apk = r'c:\Users\Jasur\.gemini\antigravity\scratch\findix\findix_app\build\app\outputs\flutter-apk\app-release.apk'
    remote_apk = f'{project_dir}/downloads/findix.apk'
    
    # Upload manually to prevent hanging on Windows with paramiko
    with open(local_apk, 'rb') as f:
        with sftp.open(remote_apk, 'wb') as remote_f:
            remote_f.set_pipelined(True)
            chunk_size = 32768
            total_size = os.path.getsize(local_apk)
            uploaded = 0
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                remote_f.write(data)
                uploaded += len(data)
                if uploaded % (chunk_size * 100) == 0:
                    print(f"Uploaded {uploaded} / {total_size} bytes ({(uploaded/total_size)*100:.2f}%)")
            
    sftp.close()
    ssh.close()
    print("Done APK!")

if __name__ == '__main__':
    deploy()
