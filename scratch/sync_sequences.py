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
        
        # SQL command to sync sequences for all tables in public schema
        # This finds all sequences, finds their owner tables, and sets sequence to MAX(id)
        sync_sql = """
        DO $$ 
        DECLARE 
            r RECORD; 
        BEGIN 
            FOR r IN (SELECT table_name, column_name, column_default 
                      FROM information_schema.columns 
                      WHERE column_default LIKE 'nextval%' 
                      AND table_schema = 'public') 
            LOOP 
                EXECUTE 'SELECT setval(pg_get_serial_sequence(' || quote_literal(r.table_name) || ', ' || quote_literal(r.column_name) || '), COALESCE(MAX(' || r.column_name || '), 1)) FROM ' || r.table_name; 
            END LOOP; 
        END $$;
        """
        
        print("SYNCING POSTGRESQL SEQUENCES...")
        # We run this inside the db container
        cmd = f"docker exec -i findix-db psql -U findix_user -d findix_db -c \"{sync_sql}\""
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
