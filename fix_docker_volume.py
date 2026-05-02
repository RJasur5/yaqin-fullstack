import paramiko
host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

# 1. Check if serviceAccountKey.json exists on the server
stdin, stdout, stderr = ssh.exec_command('ls -la /home/yaqingo/yaqin-production/backend/serviceAccountKey.json')
print("File check:", stdout.read().decode().strip())

# 2. Read current docker-compose.yml
stdin, stdout, stderr = ssh.exec_command('cat /home/yaqingo/yaqin-production/docker-compose.yml')
compose_content = stdout.read().decode()
print("\nCurrent docker-compose.yml:")
print(compose_content)

# 3. Add volume mount for serviceAccountKey.json
if 'serviceAccountKey' not in compose_content:
    new_content = compose_content.replace(
        '      - ./backend/findix.db:/app/findix.db',
        '      - ./backend/findix.db:/app/findix.db\n      - ./backend/serviceAccountKey.json:/app/serviceAccountKey.json:ro'
    )
    
    # Write updated docker-compose.yml
    stdin, stdout, stderr = ssh.exec_command(f"cat > /home/yaqingo/yaqin-production/docker-compose.yml << 'ENDOFFILE'\n{new_content}ENDOFFILE")
    stdout.read()
    print("\nUpdated docker-compose.yml with serviceAccountKey volume!")
    
    # 4. Restart with new volume
    print("\nRestarting backend with new volume mount...")
    stdin, stdout, stderr = ssh.exec_command('cd /home/yaqingo/yaqin-production && docker compose up -d --force-recreate backend')
    print(stdout.read().decode())
    print(stderr.read().decode())
else:
    print("\nserviceAccountKey already in docker-compose.yml")

ssh.close()
print("Done!")
