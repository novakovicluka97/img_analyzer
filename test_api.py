import requests

url = "https://img-analyzer.onrender.com/detect-faces/"

# Replace this with any public image URL you want to test
sample_image_url = "https://bvcukfllrjayptavsicx.supabase.co/storage/v1/object/public/avatars//gala.png"

payload = {"image_url": sample_image_url}
response = requests.post(url, json=payload)
print(response.json()) 