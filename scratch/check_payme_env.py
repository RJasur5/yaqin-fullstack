import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

debug_script = """
import os
print(f"PAYME_ID: {os.getenv('PAYME_ID')}")
print(f"PAYME_KEY: {os.getenv('PAYME_KEY')}")
print(f"PAYME_TEST_KEY: {os.getenv('PAYME_TEST_KEY')}")
print(f"PAYME_USE_TEST: {os.getenv('PAYME_USE_TEST')}")
"""

def check_env():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, username=user, password=password)
        print("--- Checking backend environment variables ---")
        cmd = "cat << 'EOF' | docker exec -i findix-backend python\n" + debug_script + "\nEOF"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode())
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check_env()
