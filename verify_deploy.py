import paramiko
import requests

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

# Check if DB still exists and has data
cmd = """docker exec findix-backend python -c "
import sqlite3
db = sqlite3.connect('findix.db')
rows = db.execute('SELECT id, phone FROM users WHERE phone LIKE '+chr(39)+'%1234567%'+chr(39)).fetchall()
for r in rows:
    print(r)
print(f'Total users: {db.execute(chr(39)+'SELECT count(*) FROM users'+chr(39)).fetchone()[0]}')
db.close()
" """
stdin, stdout, stderr = ssh.exec_command(cmd)
out = stdout.read().decode()
err = stderr.read().decode()
print("=== DB CHECK AFTER REBUILD ===")
print(out)
if err: print("ERR:", err)

# Check if new schemas.py is deployed
cmd2 = 'docker exec findix-backend grep normalize_phone schemas.py'
stdin2, stdout2, stderr2 = ssh.exec_command(cmd2)
out2 = stdout2.read().decode()
print("\n=== CHECK normalize_phone in schemas.py ===")
print(out2 if out2 else "NOT FOUND!")

# Check phone_formatter.py
cmd3 = 'docker exec findix-backend grep normalize_phone utils/phone_formatter.py'
stdin3, stdout3, stderr3 = ssh.exec_command(cmd3)
out3 = stdout3.read().decode()
print("\n=== CHECK normalize_phone in phone_formatter.py ===")
print(out3 if out3 else "NOT FOUND!")

ssh.close()

# Test login API
print("\n=== API LOGIN TEST ===")
try:
    r = requests.post('https://yaqingo.uz/api/auth/login', json={
        'phone': '+998991234567',
        'password': '123456'
    }, timeout=10)
    print(f"Clean phone: Status={r.status_code} Response={r.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

try:
    r2 = requests.post('https://yaqingo.uz/api/auth/login', json={
        'phone': '+998 (99) 123-45-67',
        'password': '123456'
    }, timeout=10)
    print(f"Formatted phone: Status={r2.status_code} Response={r2.text[:200]}")
except Exception as e:
    print(f"Error: {e}")
