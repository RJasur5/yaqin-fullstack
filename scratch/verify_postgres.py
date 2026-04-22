import paramiko

def verify_postgres_data():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    # Check counts in Postgres
    code = """
from database import SessionLocal
from models import Category, User, Order
db = SessionLocal()
print(f'Categories: {db.query(Category).count()}')
print(f'Users: {db.query(User).count()}')
print(f'Orders: {db.query(Order).count()}')
db.close()
"""
    ssh.exec_command(f'sudo -S docker exec -i findix-backend sh -c "cat > verify_data.py"')
    stdin, stdout, stderr = ssh.exec_command(f'sudo -S docker exec -i findix-backend sh -c "cat > verify_data.py"')
    stdin.write(password + "\n")
    stdin.write(code)
    stdin.close()
    
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker exec findix-backend python3 verify_data.py")
    stdin.write(password + "\n")
    stdin.flush()
    print(stdout.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    verify_postgres_data()
