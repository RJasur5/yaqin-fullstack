import paramiko
import os

def mega_deploy():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    local_zip = "project_clean.zip"
    local_apk = "findix_app/build/app/outputs/flutter-apk/app-release.apk"
    local_db = "backend/findix.db"

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        print("CONNECTED!")

        def run_sudo(command):
            print(f"Executing: {command}")
            stdin, stdout, stderr = client.exec_command(f"sudo -S {command}", get_pty=True)
            stdin.write(password + '\n')
            stdin.flush()
            res = stdout.read().decode()
            print(f"Output: {res[:100]}...") # Print first 100 chars
            return res

        # 1. Clean Server
        print("Cleaning server folder...")
        run_sudo("rm -rf /var/www/yaqin && mkdir -p /var/www/yaqin/downloads")

        # 2. Upload
        print("Uploading files...")
        sftp = client.open_sftp()
        sftp.put(local_zip, "/home/yaqingo/project_clean.zip")
        sftp.put(local_apk, "/home/yaqingo/app.apk")
        sftp.put(local_db, "/home/yaqingo/findix.db")
        sftp.close()

        # 3. Extract and Setup
        print("Extracting project...")
        run_sudo("unzip -o /home/yaqingo/project_clean.zip -d /var/www/yaqin/")
        run_sudo("cp /home/yaqingo/app.apk /var/www/yaqin/downloads/app.apk")
        run_sudo("chmod 644 /var/www/yaqin/downloads/app.apk")

        # 4. Launch
        print("LAUNCHING DOCKER...")
        run_sudo("cd /var/www/yaqin && docker compose down && docker compose up -d --build")
        
        # 5. DB Migrate
        print("Confirming DB migration...")
        run_sudo("docker cp /home/yaqingo/findix.db findix-backend:/app/findix.db")
        run_sudo('docker exec -i findix-backend bash -c "echo y | python migrate_sqlite_to_postgres.py"')

        print("--- MEGA DEPLOY COMPLETE! ---")

    except Exception as e:
        print(f"FAILED: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    mega_deploy()
