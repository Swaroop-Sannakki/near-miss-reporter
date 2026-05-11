import requests
import os

def call_groq(prompt):
    api_key = os.getenv("GROQ_API_KEY")

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3  # 🔥 stable output
    }

    try:
        response = requests.post(url, headers=headers, json=body, timeout=2)

        if response.status_code != 200:
            return None

        return response.json()["choices"][0]["message"]["content"]

    except:
        return None