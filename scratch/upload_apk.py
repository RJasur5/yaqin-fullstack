import paramiko
import os

def upload_apk():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    local_path = "findix_app/build/app/outputs/flutter-apk/app-release.apk"
    remote_path = "yaqin-production/downloads/app.apk"

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {host}...")
        client.connect(host, username=user, password=password, timeout=30)
        sftp = client.open_sftp()
        
        try:
            sftp.mkdir('yaqin-production/downloads')
            print("Created downloads directory.")
        except:
            pass
            
        print(f"Uploading {local_path} to {remote_path}...")
        sftp.put(local_path, remote_path)
        sftp.close()
        print("Upload successful!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    upload_apk()
