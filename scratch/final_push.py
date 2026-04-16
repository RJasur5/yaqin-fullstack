import paramiko
import os
import time

def final_push():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    local_zip = "project_clean.zip"
    local_apk = "findix_app/build/app/outputs/flutter-apk/app-release.apk"
    local_db = "findix.db"
    
    remote_path = "/var/www/yaqin"

    print("Connecting for final push...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password)

    def run_sudo(command):
        stdin, stdout, stderr = client.exec_command(f"sudo -S {command}", get_pty=True)
        stdin.write(password + '\n')
        stdin.flush()
        return stdout.read().decode()

    # Upload files using SFTP
    transport = client.get_transport()
    sftp = paramiko.SFTPClient.from_transport(transport)
    
    print("Uploading clean project...")
    sftp.put(local_zip, "/home/yaqingo/project_clean.zip")
    
    print("Uploading APK...")
    sftp.put(local_apk, "/home/yaqingo/app-release.apk")
    
    print("Uploading Database...")
    sftp.put(local_db, "/home/yaqingo/findix.db")
    sftp.close()

    # Repair paths and extract
    print("Extracting and launching on server...")
    run_sudo("mkdir -p /var/www/yaqin/downloads")
    run_sudo("unzip -o /home/yaqingo/project_clean.zip -d /var/www/yaqin/")
    run_sudo("cp /home/yaqingo/app-release.apk /var/www/yaqin/downloads/app.apk")
    
    # Launch
    print("Launching containers...")
    run_sudo(f"cd {remote_path} && docker compose up -d --build")
    
    # Wait for DB and Migrate
    print("Waiting 10s for DB...")
    time.sleep(10)
    print("Migrating data SQLite -> Postgres...")
    run_sudo("docker cp /home/yaqingo/findix.db findix-backend:/app/findix.db")
    run_sudo('docker exec -i findix-backend bash -c "echo y | python migrate_sqlite_to_postgres.py"')

    print("--- EVERYTHING IS READY! ---")
    client.close()

if __name__ == "__main__":
    final_push()
