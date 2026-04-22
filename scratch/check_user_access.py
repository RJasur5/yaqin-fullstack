import paramiko

def check_user_access():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    # Check if user exists and has a password
    code = """
import sqlite3
conn = sqlite3.connect('findix.db')
c = conn.cursor()
c.execute('SELECT phone, name, password_hash FROM users WHERE phone="+998998426574"')
res = c.fetchone()
print(f'User Found: {res is not None}')
if res:
    print(f'Name: {res[1]}')
    # We can't easily verify the hash here without passlib, 
    # but at least we see it is not empty.
    print(f'Has Password: {len(res[2]) > 0}')
conn.close()
"""
    ssh.exec_command(f'sudo -S docker exec -i findix-backend sh -c "cat > check_user.py"')
    stdin, stdout, stderr = ssh.exec_command(f'sudo -S docker exec -i findix-backend sh -c "cat > check_user.py"')
    stdin.write(password + "\n")
    stdin.write(code)
    stdin.close()
    
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker exec findix-backend python3 check_user.py")
    stdin.write(password + "\n")
    stdin.flush()
    print(stdout.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    check_user_access()
