import paramiko

def update_nginx():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    # 1. Upload nginx.conf
    sftp = ssh.open_sftp()
    print("Uploading new nginx.conf...")
    sftp.put("deploy/nginx.conf", "/home/yaqingo/yaqin-production/deploy/nginx.conf")
    sftp.close()
    
    # 2. Restart Nginx container
    print("Restarting Nginx container...")
    ssh.exec_command(f'echo {password} | sudo -S docker restart findix-nginx')
    
    ssh.close()
    print("Done!")

if __name__ == "__main__":
    update_nginx()
