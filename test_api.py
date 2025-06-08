import requests

url = "https://img-analyzer.onrender.com/detect-faces/"

# Replace this with any public image URL you want to test
image_url = "https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png"

payload = {"image_url": image_url}
response = requests.post(url, json=payload)
print(response.json()) 