import paramiko

def check_db_again():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker exec findix-backend python3 -c 'from database import SessionLocal; from models import Order; db=SessionLocal(); print(f\"Orders inside container NOW: {db.query(Order).count()}\"); db.close()'")
    stdin.write(password + "\n")
    stdin.flush()
    print("Output:", stdout.read().decode())
    
    # check db size internally
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker exec findix-backend ls -la findix.db")
    stdin.write(password + "\n")
    stdin.flush()
    print("DB file:", stdout.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    check_db_again()
