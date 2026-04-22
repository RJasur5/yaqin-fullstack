import paramiko

def alter_remote_db():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password, timeout=15)
        # Execute ALTER TABLE in the container
        sql = "ALTER TABLE users ADD COLUMN IF NOT EXISTS fcm_token VARCHAR(255);"
        command = f"sudo -S docker exec findix-db psql -U findix_user -d findix_db -c '{sql}'"
        
        stdin, stdout, stderr = client.exec_command(command)
        stdin.write(password + '\n')
        stdin.flush()
        
        print("Output:", stdout.read().decode())
        print("Error:", stderr.read().decode())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    alter_remote_db()
