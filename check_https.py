import ssl
import socket
from urllib.request import urlopen, Request

hostname = 'yaqingo.uz'
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

try:
    with socket.create_connection((hostname, 443)) as sock:
        with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
            print(ssock.version())
            print("Successfully connected to 443")
except Exception as e:
    print(f"Failed to connect to 443: {e}")

try:
    req = Request(f"https://{hostname}/download/app-release.apk", headers={'User-Agent': 'Mozilla/5.0'})
    response = urlopen(req, context=ctx, timeout=5)
    print(f"HTTPS Download Request Status: {response.getcode()}")
except Exception as e:
    print(f"HTTPS Download Request Failed: {e}")
