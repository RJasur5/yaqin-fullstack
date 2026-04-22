import paramiko

def final_verify():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker exec findix-backend python3 -c \"from database import SessionLocal; from models import User; db=SessionLocal(); print(db.query(User).count()); db.close()\"")
    stdin.write(password + "\n")
    stdin.flush()
    print("User count in PostgreSQL:", stdout.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    final_verify()
