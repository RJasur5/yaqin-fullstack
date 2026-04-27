import paramiko

def optimize_server():
    host = "95.182.118.245"
    user = "yaqingo"
    password = "nEQvV9Pi8e"
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(host, username=user, password=password)
        
        # 1. Update Nginx config with Gzip and better proxy settings
        nginx_conf = """map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

server {
    listen 80 default_server;
    server_name _;

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript application/xml+rss image/svg+xml;

    # Download APK
    location = /app.apk {
        root /app/downloads;
        try_files /app.apk =404;
        default_type application/vnd.android.package-archive;
    }

    # Backend API
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffering
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }

    # WebSocket
    location /ws {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }

    # Static for Web / Uploads
    location /uploads {
        proxy_pass http://backend:8000;
        expires 7d;
        add_header Cache-Control "public, no-transform";
    }

    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
    }
}
"""
        print("Optimizing Nginx config...")
        client.exec_command(f"echo '{nginx_conf}' > yaqin-production/deploy/nginx.conf")
        
        # 2. Update Dockerfile to use more workers
        print("Optimizing Backend Dockerfile (4 workers)...")
        dockerfile_content = """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
"""
        client.exec_command(f"echo '{dockerfile_content}' > yaqin-production/backend/Dockerfile")
        
        # 3. Restart services
        print("Restarting services to apply optimizations...")
        stdin, stdout, stderr = client.exec_command("cd yaqin-production && docker compose up -d --build")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("OPTIMIZATION COMPLETE!")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    optimize_server()
