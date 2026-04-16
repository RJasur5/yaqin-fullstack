import paramiko
import os

def pro_upload():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    # Files to upload
    items_to_send = [
        "backend",
        "deploy",
        "docker-compose.yml",
        "findix_app/build/app/outputs/flutter-apk/app-release.apk"
    ]
    
    # Exclude these
    exclude = [".git", "venv", "__pycache__", ".pytest_cache", ".idea", ".vscode"]

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        print("CONNECTED TO SERVER!")
        
        sftp = client.open_sftp()
        
        # 1. Create remote root
        remote_root = "/home/yaqingo/yaqin-production"
        try:
            print(f"Creating remote folder: {remote_root}")
            sftp.mkdir(remote_root)
        except:
            pass

        def upload_recursive(l_path, r_path):
            if any(ex in l_path for ex in exclude):
                return
            
            if os.path.isdir(l_path):
                try:
                    sftp.mkdir(r_path)
                except:
                    pass
                for item in os.listdir(l_path):
                    upload_recursive(os.path.join(l_path, item), r_path + "/" + item)
            else:
                print(f"  Uploading: {l_path} -> {r_path}")
                sftp.put(l_path, r_path)

        for item in items_to_send:
            if item == "findix_app/build/app/outputs/flutter-apk/app-release.apk":
                print("Uploading APK...")
                sftp.put(item, remote_root + "/app-release.apk")
            else:
                upload_recursive(item, remote_root + "/" + item)
        
        # 2. Upload Database for migration
        print("Uploading Database...")
        sftp.put("backend/findix.db", "/home/yaqingo/findix.db")
        
        sftp.close()
        print("--- UPLOAD SUCCESSFUL ---")

    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    pro_upload()
