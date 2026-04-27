import paramiko
import os

hostname = "95.182.118.245"
username = "yaqingo"
password = "nEQvV9Pi8e"
base_dir = "yaqin-production"

def remote_fix():
    try:
        print(f"Connecting to {hostname}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        
        db_path = "/home/yaqingo/yaqin-production/backend/findix.db"
        print(f"Targeting specific database at {db_path}")

        local_script = "scratch/remote_script.py"
        with open(local_script, "w") as f:
            f.write(f"""
import sqlite3
import os

db_path = '{db_path}'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('PRAGMA table_info(users)')
    cols = [r[1] for r in cursor.fetchall()]
    if 'is_trial_used' not in cols:
        print("Adding is_trial_used")
        cursor.execute('ALTER TABLE users ADD COLUMN is_trial_used BOOLEAN DEFAULT 0')
    if 'fcm_token' not in cols:
        print("Adding fcm_token")
        cursor.execute('ALTER TABLE users ADD COLUMN fcm_token VARCHAR(255)')
    conn.commit()
    conn.close()
    print("DB fix applied")
else:
    print(f"DB not found at {{db_path}}")
""")
        
        sftp = ssh.open_sftp()
        remote_script = "fix_db_tmp.py" # In home dir
        print(f"Uploading fix script to {remote_script}...")
        sftp.put(local_script, remote_script)
        sftp.close()

        print("Running fix script on server...")
        stdin, stdout, stderr = ssh.exec_command(f"python3 {remote_script}")
        print(stdout.read().decode())
        print(stderr.read().decode())

        print("Restarting backend container to apply changes...")
        # Check if we should use 'docker compose' or 'docker-compose'
        ssh.exec_command(f"cd {base_dir} && docker compose restart backend || docker-compose restart backend")
        
        ssh.close()
        print("Remote fix completed.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    remote_fix()
