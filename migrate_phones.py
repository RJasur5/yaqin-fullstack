import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=10)

cmd = """docker exec findix-backend python -c "
import re
import sqlite3

def normalize_phone(phone):
    if not phone:
        return phone
    digits = re.sub(r'\\\\D', '', phone)
    if len(digits) >= 12 and digits.startswith('998'):
        return '+' + digits[:12]
    elif len(digits) == 9:
        return '+998' + digits
    else:
        if len(digits) > 9:
            return '+998' + digits[-9:]
        return phone

db = sqlite3.connect('findix.db')
rows = db.execute('SELECT id, phone FROM users').fetchall()
updated = 0
skipped = 0
for uid, phone in rows:
    clean = normalize_phone(phone)
    if clean != phone:
        # Check if clean phone already exists
        existing = db.execute('SELECT id FROM users WHERE phone = ? AND id != ?', (clean, uid)).fetchone()
        if existing:
            print(f'  SKIP user {uid}: [{phone}] -> [{clean}] (conflicts with user {existing[0]})')
            skipped += 1
        else:
            print(f'  UPDATE user {uid}: [{phone}] -> [{clean}]')
            db.execute('UPDATE users SET phone = ? WHERE id = ?', (clean, uid))
            updated += 1
db.commit()
print(f'\\nDone: {updated} updated, {skipped} skipped (duplicates)')
db.close()
" """
stdin, stdout, stderr = ssh.exec_command(cmd)
out = stdout.read().decode()
err = stderr.read().decode()
print(out)
if err: print("ERR:", err)

# Now test login
print("\n=== LOGIN TEST ===")
import requests
r = requests.post('https://yaqingo.uz/api/auth/login', json={
    'phone': '+998991234567',
    'password': '123456'
}, timeout=10)
print(f"Clean phone login: {r.status_code} {r.text[:100]}")

r2 = requests.post('https://yaqingo.uz/api/auth/login', json={
    'phone': '+998 (99) 123-45-67',
    'password': '123456'
}, timeout=10)
print(f"Formatted phone login: {r2.status_code} {r2.text[:100]}")

ssh.close()
