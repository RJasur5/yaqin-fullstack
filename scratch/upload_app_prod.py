import paramiko
import os

def upload_final_apk():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    local_apk = "findix_app/build/app/outputs/flutter-apk/app-release.apk"
    remote_path = "/home/yaqingo/yaqin-production/downloads/app.apk"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    sftp = ssh.open_sftp()
    print(f"Uploading production APK: {remote_path}...")
    sftp.put(local_apk, remote_path)
    sftp.close()
    
    ssh.close()
    print("Done!")

if __name__ == "__main__":
    upload_final_apk()
