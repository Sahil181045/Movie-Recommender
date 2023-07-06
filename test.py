import requests
import json

BASE = "http://127.0.0.1:5000"

data = {'movies' : ['Avatar','Spider-Man']}

response = requests.post(BASE,json.dumps(data))
print(response.json())