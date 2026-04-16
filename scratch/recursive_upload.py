import paramiko
import os

def upload_dir(sftp, local, remote):
    print(f"Directory: {local} -> {remote}")
    try:
        sftp.mkdir(remote)
    except:
        pass
    
    for item in os.listdir(local):
        if item in ['.git', 'venv', '__pycache__', '.pytest_cache']:
            continue
        
        l_path = os.path.join(local, item)
        r_path = remote + '/' + item
        
        if os.path.isdir(l_path):
            upload_dir(sftp, l_path, r_path)
        else:
            print(f"  Uploading: {item}")
            sftp.put(l_path, r_path)

def main():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        print("CONNECTED!")
        
        sftp = client.open_sftp()
        
        # Ensure project root
        project_root = "/home/yaqingo/project"
        try:
            sftp.mkdir(project_root)
        except:
            pass
            
        print("Starting recursive upload...")
        upload_dir(sftp, "backend", project_root + "/backend")
        upload_dir(sftp, "deploy", project_root + "/deploy")
        
        print("Uploading docker-compose.yml...")
        sftp.put("docker-compose.yml", project_root + "/docker-compose.yml")
        
        sftp.close()
        print("UPLOAD COMPLETE!")
        
    except Exception as e:
        print(f"UPLOAD FAILED: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()
