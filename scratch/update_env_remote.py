import paramiko

def update_remote_env():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password, timeout=15)
        sftp = client.open_sftp()
        content = (
            'DATABASE_URL=postgresql://findix_user:findix_pass@db:5432/findix_db\n'
            'SECRET_KEY=findix-secret-key-2026-change-in-production\n'
            'ALGORITHM=HS256\n'
            'TOKEN_EXPIRE_DAYS=30\n'
            'LOG_LEVEL=INFO\n'
        )
        with sftp.file('yaqin-production/backend/.env', 'w') as f:
            f.write(content)
        print("ENV file updated successfully!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    update_remote_env()
