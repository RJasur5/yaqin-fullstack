import paramiko
import os

def upload():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    local_project = "project.zip"
    local_apk = "findix_app/build/app/outputs/flutter-apk/app-release.apk"
    
    remote_path = "/home/yaqingo/project.zip"
    remote_apk = "/home/yaqingo/app-release.apk"

    print("Connecting for upload...")
    transport = paramiko.Transport((host, 22))
    transport.connect(username=user, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    
    print(f"Uploading {local_project}...")
    sftp.put(local_project, remote_path)
    
    print(f"Uploading {local_apk}...")
    sftp.put(local_apk, remote_apk)
    
    sftp.close()
    transport.close()
    
    # Extract
    print("Extracting files on server...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password)
    
    # Clean and extract
    client.exec_command("rm -rf /var/www/yaqin && mkdir -p /var/www/yaqin/downloads")
    client.exec_command("unzip -o /home/yaqingo/project.zip -d /var/www/yaqin/")
    client.exec_command("cp /home/yaqingo/app-release.apk /var/www/yaqin/downloads/app-release.apk")
    
    print("UPLOAD AND EXTRACTION COMPLETE!")
    client.close()

if __name__ == "__main__":
    upload()
