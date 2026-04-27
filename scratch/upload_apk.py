import paramiko

host = '95.182.118.245'
user = 'yaqingo'
password = 'nEQvV9Pi8e'

def upload_apk():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, username=user, password=password)
        sftp = ssh.open_sftp()
        
        print("Uploading APK...")
        ssh.exec_command("mkdir -p /home/yaqingo/yaqin-production/static")
        import time
        time.sleep(1)
        sftp.put(
            r'C:\Users\Jasur\.gemini\antigravity\scratch\findix\findix_app\build\app\outputs\flutter-apk\app-release.apk',
            '/home/yaqingo/yaqin-production/static/app-release.apk'
        )
        print("APK uploaded!")
        sftp.close()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    upload_apk()
