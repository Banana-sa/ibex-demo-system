import json, sys, base64, urllib.request
import os
KEY = os.environ["OPENROUTER_API_KEY"]
def call(model, messages, out, audio=None, extra=None):
    body = {"model": model, "messages": messages, "stream": True, "modalities": ["text", "audio"]}
    if audio: body["audio"] = audio
    if extra: body.update(extra)
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    chunks, text, usage = [], [], None
    with urllib.request.urlopen(req, timeout=600) as r:
        for line in r:
            line = line.decode().strip()
            if not line.startswith("data:") or line == "data: [DONE]": continue
            d = json.loads(line[5:])
            if d.get("usage"): usage = d["usage"]
            for ch in d.get("choices", []):
                de = ch.get("delta", {})
                a = de.get("audio") or {}
                if a.get("data"): chunks.append(a["data"])
                if a.get("transcript"): text.append(a["transcript"])
                if de.get("content"): text.append(de["content"] if isinstance(de["content"], str) else str(de["content"]))
    raw = b"".join(base64.b64decode(c) for c in chunks)
    open(out, "wb").write(raw)
    print(out, len(raw), "usage:", usage and usage.get("cost"), "|", "".join(text)[:200])
    return raw
if __name__ == "__main__":
    j = json.loads(sys.argv[1])
    call(j["model"], j["messages"], j["out"], j.get("audio"), j.get("extra"))
