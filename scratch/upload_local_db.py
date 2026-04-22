import paramiko

def upload_local_db():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    print("Uploading local findix.db to host...")
    sftp = ssh.open_sftp()
    sftp.put("backend/findix.db", "/home/yaqingo/tmp_old.db")
    sftp.close()
    
    print("Copying to container...")
    ssh.exec_command(f'echo {password} | sudo -S docker cp /home/yaqingo/tmp_old.db findix-backend:/app/old_findix.db')
    
    ssh.close()
    print("Upload and Copy Done!")

if __name__ == "__main__":
    upload_local_db()
