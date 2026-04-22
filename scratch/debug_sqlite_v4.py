import paramiko

def debug_sqlite_container():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    code = """
import sqlite3
import os
import sqlalchemy
print(f'PWD: {os.getcwd()}')
print(f'Files: {os.listdir(".")}')
fname = "old_findix.db"
if os.path.exists(fname):
    print(f'File {fname} exists, size: {os.path.getsize(fname)}')
    conn = sqlite3.connect(fname)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type=\'table\';")
    print('Tables:', [t[0] for t in cursor.fetchall()])
    conn.close()
else:
    print(f'File {fname} NOT FOUND')
"""
    ssh.exec_command(f'sudo -S docker exec -i findix-backend sh -c "cat > debug_sqlite.py"')
    stdin, stdout, stderr = ssh.exec_command(f'sudo -S docker exec -i findix-backend sh -c "cat > debug_sqlite.py"')
    stdin.write(password + "\n")
    stdin.write(code)
    stdin.close()
    
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker exec findix-backend python3 debug_sqlite.py")
    stdin.write(password + "\n")
    stdin.flush()
    print(stdout.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    debug_sqlite_container()
