import paramiko

def check_tables_py():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    code = """
import sqlite3
import os
print(f'Checking {os.path.abspath("old_findix.db")}')
try:
    conn = sqlite3.connect('old_findix.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print('Tables:', [t[0] for t in cursor.fetchall()])
    conn.close()
except Exception as e:
    print(f'Error: {e}')
"""
    ssh.exec_command(f'sudo -S docker exec -i findix-backend sh -c "cat > check_tables.py"')
    stdin, stdout, stderr = ssh.exec_command(f'sudo -S docker exec -i findix-backend sh -c "cat > check_tables.py"')
    stdin.write(password + "\n")
    stdin.write(code)
    stdin.close()
    
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker exec findix-backend python3 check_tables.py")
    stdin.write(password + "\n")
    stdin.flush()
    print(stdout.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    check_tables_py()
