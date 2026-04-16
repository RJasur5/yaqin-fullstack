import paramiko

def check_db_content():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        print("CONNECTED TO SERVER!")

        def run_sudo_sql(sql):
            # Run psql inside the findix-db container
            cmd = f"sudo -S docker exec findix-db psql -U findix_user -d findix_db -t -c \"{sql}\""
            stdin, stdout, stderr = client.exec_command(cmd, get_pty=True)
            stdin.write(password + '\n')
            stdin.flush()
            return stdout.read().decode('utf-8', 'ignore').strip()

        tables = ['users', 'masters', 'orders', 'categories']
        print("\n--- DATABASE STATUS REPORT ---")
        for table in tables:
            try:
                count = run_sudo_sql(f"SELECT COUNT(*) FROM {table};")
                # The output will include the sudo password prompt, so we take the last line
                lines = count.split('\n')
                actual_count = lines[-1].strip()
                print(f"Table '{table}': {actual_count} records")
            except Exception as e:
                print(f"Table '{table}': ERROR ({e})")
        
        # Check if findix.db exists in backend container
        print("\n--- CHECKING SQLITE FILE IN BACKEND ---")
        sqlite_check = run_sudo_sql("ls -l /app/findix.db") # Wait, this won't work inside psql.
        # Run regular docker exec
        stdin, stdout, stderr = client.exec_command(f"sudo -S docker exec findix-backend ls -la /app/findix.db", get_pty=True)
        stdin.write(password + '\n')
        stdin.flush()
        print(f"SQLite file check: {stdout.read().decode()}")

    except Exception as e:
        print(f"CHECK FAILED: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_db_content()
