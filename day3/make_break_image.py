import os
import base64
import requests

# читаем ключ из .env в корне проекта (без печати на экран)
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
env = {}
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()

api_key = env["LLM_IMAGE_API_KEY"]
url = "https://llm.alem.ai/v1/images/generations"

prompt = 'A clean poster with large bold centered text that reads exactly "BREAK TILL 11:45"'

resp = requests.post(
    url,
    headers={"Authorization": f"Bearer {api_key}"},
    json={"model": "text-to-image", "prompt": prompt, "n": 1, "size": "1024x1024"},
    timeout=120,
)
resp.raise_for_status()
data = resp.json()["data"][0]

# ответ может содержать base64 (b64_json) или ссылку (url)
out_path = "break_till_1145.png"
if "b64_json" in data and data["b64_json"]:
    with open(out_path, "wb") as f:
        f.write(base64.b64decode(data["b64_json"]))
else:
    img = requests.get(data["url"], timeout=120)
    img.raise_for_status()
    with open(out_path, "wb") as f:
        f.write(img.content)

print("saved", out_path)
