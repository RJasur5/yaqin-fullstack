import paramiko
import time

def pro_launch():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        print("CONNECTED!")

        def run_sudo(cmd):
            print(f"Executing: {cmd}")
            stdin, stdout, stderr = client.exec_command(f"sudo -S bash -c '{cmd}'", get_pty=True)
            stdin.write(password + '\n')
            stdin.flush()
            # Wait and return output
            time.sleep(2)
            return stdout.read().decode('utf-8', 'ignore')

        # 1. Add user to docker group (for future ease)
        print("Ensuring docker group permissions...")
        run_sudo("usermod -aG docker yaqingo")
        
        # 2. Setup production directory
        print("Moving files to /var/www/yaqin (Production Folder)...")
        run_sudo("rm -rf /var/www/yaqin && mkdir -p /var/www/yaqin")
        run_sudo("cp -r /home/yaqingo/yaqin-production/* /var/www/yaqin/")
        
        # 3. Setup APK
        print("Preparing APK for download...")
        run_sudo("mkdir -p /var/www/yaqin/downloads")
        run_sudo("cp /home/yaqingo/yaqin-production/app-release.apk /var/www/yaqin/downloads/app.apk")
        run_sudo("chmod -R 777 /var/www/yaqin")

        # 4. Launch with Docker Compose
        print("Launching Docker Compose...")
        res = run_sudo("cd /var/www/yaqin && docker compose up -d --build")
        print(f"Launch result: {res[:200]}")
        
        # 5. Wait for DB and Migrate
        print("Waiting for database to settle (15s)...")
        time.sleep(15)
        
        print("Migrating data SQLite -> Postgres...")
        run_sudo("docker cp /home/yaqingo/findix.db findix-backend:/app/findix.db")
        migration = run_sudo("docker exec -i findix-backend python migrate_sqlite_to_postgres.py")
        print(f"Migration: {migration[:200]}")
        
        # 6. Final verification
        print("Verification: Checking if port 80 is open...")
        status = run_sudo("ss -tulpn | grep :80")
        if ":80" in status:
            print("--- SUCCESS: PROJECT IS LIVE ON PORT 80 ---")
        else:
            print("--- WARNING: PORT 80 NOT RESPONDING YET ---")

    except Exception as e:
        print(f"PRO LAUNCH FAILED: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    pro_launch()
