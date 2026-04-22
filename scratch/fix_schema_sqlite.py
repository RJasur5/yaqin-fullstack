import paramiko

def fix_sqlite_schema():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    
    print("Fixing SQLite schema to add missing columns...")
    code = """
import sqlite3

try:
    conn = sqlite3.connect('findix.db')
    cursor = conn.cursor()
    
    # Add is_trial_used
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_trial_used BOOLEAN DEFAULT 0")
        print("Added is_trial_used to users.")
    except Exception as e:
        print("Column is_trial_used might already exist:", e)
        
    conn.commit()
    conn.close()
    print("Schema fix applied!")
except Exception as e:
    print("Error:", e)
"""
    ssh.exec_command(f'sudo -S docker exec -i findix-backend sh -c "cat > fix_schema.py"')
    stdin, stdout, stderr = ssh.exec_command(f'sudo -S docker exec -i findix-backend sh -c "cat > fix_schema.py"')
    stdin.write(password + "\n")
    stdin.write(code)
    stdin.close()
    
    stdin, stdout, stderr = ssh.exec_command("sudo -S docker exec findix-backend python3 fix_schema.py")
    stdin.write(password + "\n")
    stdin.flush()
    print(stdout.read().decode())
    
    # Restart the backend to clear any cached SQLAlchemy models
    ssh.exec_command(f"cd ~/yaqin-production && echo {password} | sudo -S docker restart findix-backend")
    
    ssh.close()
    print("Fix Schema complete!")

if __name__ == "__main__":
    fix_sqlite_schema()
