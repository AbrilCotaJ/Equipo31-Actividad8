import requests

url = "https://amatoryrabbit-us.backendless.app/api/data/tbl_users"
response = requests.get(url)

print(response.json())



