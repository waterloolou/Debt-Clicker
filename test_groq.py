"""Groq diagnostic — prints the full error body so we know exactly why it's failing."""
import json, urllib.request, urllib.error

KEY = input("Paste your Groq API key: ").strip()

models = ["llama3-8b-8192", "mixtral-8x7b-32768", "llama-3.1-8b-instant", "gemma2-9b-it"]

for model in models:
    print(f"\n--- Trying model: {model} ---")
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": "Say hello"}],
        "max_tokens": 10,
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=payload,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json", "User-Agent": "groq-python/1.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print("SUCCESS:", data["choices"][0]["message"]["content"])
            break
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"HTTP {e.code}: {body}")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
