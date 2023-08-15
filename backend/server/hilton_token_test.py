import requests

url = "https://www.hilton.com/dx-customer/auth/applications/token"

payload = {
    "app_id": "096a02c6-e844-41b4-bebf-ec74e3ca3cd4"
}

response = requests.post(url, json=payload)

print("Status code:", response.status_code)
print("Response text:", response.text)
