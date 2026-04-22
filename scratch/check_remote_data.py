import paramiko

def check_remote_data():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    # Check category count via docker exec
    cmd = "sudo -S docker exec findix-backend python3 -c 'from database import SessionLocal; from models import Category; db=SessionLocal(); print(f\"Categories: {db.query(Category).count()}\"); db.close()'"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdin.write(password + "\n")
    stdin.flush()
    
    print(stdout.read().decode())
    print(stderr.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    check_remote_data()
