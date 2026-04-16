import paramiko
import time

def launch():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    project_root = "/var/www/yaqin"

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
            return stdout.read().decode()

        # 1. Create .env
        print("Creating .env file...")
        env_content = f"""
DATABASE_URL=postgresql://findix_user:findix_prod_pass@db:5432/findix_db
POSTGRES_USER=findix_user
POSTGRES_PASSWORD=findix_prod_pass
POSTGRES_DB=findix_db
SECRET_KEY=yaqingo-secure-key-{int(time.time())}
ALGORITHM=HS256
TOKEN_EXPIRE_DAYS=30
LOG_LEVEL=INFO
""".strip()
        client.exec_command(f"echo '{env_content}' > {project_root}/backend/.env")

        # 2. Launch Docker
        print("Launching containers...")
        run_sudo(f"docker compose -f {project_root}/docker-compose.yml up -d --build")
        
        # Wait for DB to be ready
        print("Waiting for database to initialize (15s)...")
        time.sleep(15)
        
        # 3. Migrate Data
        print("Migrating data SQLite -> Postgres...")
        # Copy DB into container
        run_sudo(f"docker cp /home/yaqingo/findix.db findix-backend:/app/findix.db")
        # Run migration inside container
        # Note: We need to use 'echo y' to confirm migration in the script
        migration_cmd = 'docker exec -i findix-backend bash -c "echo y | python migrate_sqlite_to_postgres.py"'
        result = run_sudo(migration_cmd)
        print(f"Migration result: {result}")
        
        print("ALL SERVICES LAUNCHED AND DATA MIGRATED!")

    except Exception as e:
        print(f"Launch failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    launch()
