import os
import requests
import datetime

env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
config = {}
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, value = line.split("=", 1)
        config[key] = value


inventory = [
    {
        "name": "samsung galaxy 5s",
        "price": 250000,
    },
    {
        "name": "samsung galaxy 5",
        "price": 150000,
    },
    {
        "name": "xiaomi 7 pro turbo 128GB",
        "price": 70000,
    },
    {
        "name": "xiaomi 7 pro turbo 256GB",
        "price": 100000,
    },
    {
        "name": "iphone 5s 64GB",
        "price": 200000,
    },
    {
        "name": "iphone 17 256GB",
        "price": 600000,
    },
]


def prompt(prompt: str):
    system_prompt = f"""
            СЕГОДНЯ: {str(datetime.datetime.now())}
            Ты ассистент в Sulpak - магазин электроники в Алматы.
            Не придумывай ничего. Если ответа нет в твоей базе, говори, что не знаешь.
            В магазине есть следующие товары:
            {inventory}
            Ещё есть iphone 16, 256GB за 35000 тенге.
            
            Если пользователь хочет отправить сообщение администратору,
            верни функцию:
            {{
                "function": "send_email_to_admin",
                "reason": "a reason from user" (optional),
            }}
            
            """
    print(system_prompt)
    payload = {
        "model": config["LLM_CHAT_MODEL"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    }

    headers = {"Authorization": "Bearer " + config["LLM_CHAT_API_KEY"]}
    response = requests.post(
        config["LLM_CHAT_URL"],
        json=payload,
        headers=headers
    )
    data = response.json()
    return data["choices"][0]["message"]["content"]


print(prompt(" У вас есть айфоны?"))
print(prompt("Скажи администратору, что лампочка на входе перегорела"))
