import paramiko

def sync_sequences():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {host}...")
        client.connect(host, username=user, password=password, timeout=60)
        
        # Create a simple SQL file without $ signs to avoid shell issues
        sql_commands = [
            "SELECT setval(pg_get_serial_sequence('users', 'id'), COALESCE(MAX(id), 1)) FROM users;",
            "SELECT setval(pg_get_serial_sequence('orders', 'id'), COALESCE(MAX(id), 1)) FROM orders;",
            "SELECT setval(pg_get_serial_sequence('app_reviews', 'id'), COALESCE(MAX(id), 1)) FROM app_reviews;",
            "SELECT setval(pg_get_serial_sequence('master_profiles', 'id'), COALESCE(MAX(id), 1)) FROM master_profiles;",
            "SELECT setval(pg_get_serial_sequence('subscriptions', 'id'), COALESCE(MAX(id), 1)) FROM subscriptions;",
            "SELECT setval(pg_get_serial_sequence('chat_messages', 'id'), COALESCE(MAX(id), 1)) FROM chat_messages;",
            "SELECT setval(pg_get_serial_sequence('reviews', 'id'), COALESCE(MAX(id), 1)) FROM reviews;"
        ]
        
        full_sql = "\n".join(sql_commands)
        
        print("SYNCING POSTGRESQL SEQUENCES MANUALLY...")
        # Write to a file first to be safe
        client.exec_command(f"echo \\\"{full_sql}\\\" > /tmp/sync.sql")
        cmd = "docker exec -i findix-db psql -U findix_user -d findix_db -f - < /tmp/sync.sql"
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("DATABASE SYNC COMPLETE!")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    sync_sequences()
