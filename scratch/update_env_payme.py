import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

payme_id = '69eef6070ba8aa967a862f8c'
payme_key_prod = 'Mq76zn36QUhGI7fZnICTFcR&5DJ078SVT#1f'
payme_key_test = '5hkiF#4%zE5sAMsRyXqkYFP2sEjZZtaPE?PQ'

def update_env():
    print(f"Connecting to {host}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, username=user, password=password)
        print("Connected!")
        
        env_path = '/home/yaqingo/yaqin-production/backend/.env'
        
        # Read existing .env
        stdin, stdout, stderr = ssh.exec_command(f"cat {env_path}")
        content = stdout.read().decode()
        
        # Add Payme variables
        new_lines = [
            f"PAYME_ID={payme_id}",
            f"PAYME_KEY={payme_key_prod}",
            f"PAYME_TEST_KEY={payme_key_test}",
            "PAYME_USE_TEST=true" # Default to test for sandbox testing
        ]
        
        for line in new_lines:
            key = line.split('=')[0]
            if key in content:
                # Replace existing
                import re
                content = re.sub(f"^{key}=.*", line, content, flags=re.MULTILINE)
            else:
                # Append new
                content += f"\n{line}"
        
        # Write back
        sftp = ssh.open_sftp()
        with sftp.file(env_path, 'w') as f:
            f.write(content)
        sftp.close()
        print("Updated .env successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == '__main__':
    update_env()
