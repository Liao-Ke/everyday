import requests


def estimate_tokens(api_key, model, messages, url):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": model,
        "messages": messages
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # 检查请求是否成功

    token_data = response.json()
    return token_data['data']['total_tokens']
