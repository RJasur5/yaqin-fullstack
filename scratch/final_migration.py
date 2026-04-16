import paramiko

def final_migration():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        print("CONNECTED!")

        def run_sudo(cmd):
            # Run command with sudo and handle password
            stdin, stdout, stderr = client.exec_command(f"sudo -S {cmd}", get_pty=True)
            stdin.write(password + '\n')
            stdin.flush()
            return stdout.read().decode('utf-8', 'ignore')

        # Use bash -c with single quotes to wrap the echo pipe
        print("Starting forced migration...")
        cmd = "bash -c 'echo y | docker exec -i findix-backend python migrate_sqlite_to_postgres.py'"
        result = run_sudo(cmd)
        print(f"Migration Output:\n{result}")

        # Verification
        print("\n--- FINAL VERIFICATION ---")
        count = run_sudo("docker exec findix-db psql -U findix_user -d findix_db -t -c 'SELECT COUNT(*) FROM masters;'")
        print(f"Masters in DB: {count.strip()}")

    except Exception as e:
        print(f"FINAL MIGRATION FAILED: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    final_migration()
