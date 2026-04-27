import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

def get_user(user_id):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, username=user, password=password)
        cmd = f"docker exec findix-backend python3 -c \"from database import SessionLocal; from models import User; db=SessionLocal(); u=db.query(User).filter(User.id=={user_id}).first(); print(f'ID: {{u.id}}, Phone: {{u.phone}}, Role: {{u.role}}' if u else 'Not found')\""
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode())
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    import sys
    uid = sys.argv[1] if len(sys.argv) > 1 else "40"
    get_user(uid)
