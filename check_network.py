import socket
import urllib.request

try:
    ip = socket.gethostbyname('yaqingo.uz')
    print(f"yaqingo.uz resolves to {ip}")
except Exception as e:
    print(f"DNS lookup failed: {e}")

try:
    url = "http://95.182.118.245/"
    response = urllib.request.urlopen(url, timeout=5)
    print(f"Direct IP HTTP Status: {response.getcode()}")
except Exception as e:
    print(f"Direct IP HTTP Request failed: {e}")
