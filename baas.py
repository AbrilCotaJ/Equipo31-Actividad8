import requests

url = "https://XXXXXXXXX.backendless.app/api/data/peliculas"
response = requests.get(url)

print(response.json())



