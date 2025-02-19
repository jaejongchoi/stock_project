import requests
import json

url = "https://openapi.koreainvestment.com:9443/oauth2/tokenP"

payload = json.dumps({
  "grant_type": "client_credentials",
  "appkey": "PS6M6OZYHPcFUdMDi6w5GYOhfXYOhZUJzCXs",
  "appsecret": "LWUcdYzPG+BWuPjAsnnamF5QQeDJqd0Pop26sJmJPe+VCPD5kx/tMuYkTYXe2MwEw8Siz5O04UVapKoezwXzcOiEVZPF+GjNdAwy5+EBed/ptp2REOAM/P9IfN6GgCeOTYpe43Qyavr/iOZUVRbiat4Zc1ayCaPqH3ci/n62dZXOEXFuOps="
})
headers = {
  'content-type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
