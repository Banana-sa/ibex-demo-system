import json, sys, base64, os, urllib.request
KEY = os.environ["OPENROUTER_API_KEY"]
def gen(name, prompt, model="google/gemini-3.1-flash-image", ar="9:16"):
    body = {"model": model, "modalities": ["image", "text"],
            "messages": [{"role": "user", "content": prompt}],
            "image_config": {"aspect_ratio": ar}}
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=300))
    msg = r["choices"][0]["message"]
    imgs = msg.get("images") or []
    if not imgs:
        print(name, "NO IMAGE", str(msg.get("content"))[:300]); return
    url = imgs[0]["image_url"]["url"]
    data = base64.b64decode(url.split(",", 1)[1])
    out = f"/tmp/claude-0/ad/gen/{name}.png"
    open(out, "wb").write(data)
    print(name, "ok", r.get("usage", {}).get("cost"), len(data))
if __name__ == "__main__":
    jobs = json.load(open(sys.argv[1]))
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(6) as ex:
        list(ex.map(lambda j: gen(j["name"], j["prompt"], j.get("model", "google/gemini-3.1-flash-image"), j.get("ar", "9:16")), jobs))
