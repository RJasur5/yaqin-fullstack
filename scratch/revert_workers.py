import paramiko

def revert_workers():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        
        # 1. Revert Dockerfile to 1 worker for WebSocket consistency
        print("Reverting Backend Dockerfile to 1 worker (for WebSocket consistency)...")
        dockerfile_content = """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        client.exec_command(f"echo '{dockerfile_content}' > yaqin-production/backend/Dockerfile")
        
        # 2. Rebuild and restart
        print("Restarting services...")
        stdin, stdout, stderr = client.exec_command("cd yaqin-production && docker compose up -d --build")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("REVERT COMPLETE!")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    revert_workers()
