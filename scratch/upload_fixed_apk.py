import paramiko

def upload_apk():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {host}...")
        client.connect(host, username=user, password=password, timeout=60)
        
        sftp = client.open_sftp()
        source_path = r'findix_app\build\app\outputs\flutter-apk\app-release.apk'
        dest_path = 'yaqin-production/downloads/app.apk'
        
        print(f"Uploading {source_path} to {dest_path}...")
        sftp.put(source_path, dest_path)
        sftp.close()
        print("UPLOAD SUCCESSFUL!")

    except Exception as e:
        print(f"Error during upload: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    upload_apk()
