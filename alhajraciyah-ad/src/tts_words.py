import sys, ssl, asyncio, json
import edge_tts.communicate as c
c._SSL_CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
import edge_tts
async def main(text, out):
    com = edge_tts.Communicate(text, "ar-SA-HamedNeural", rate="+4%", pitch="-5Hz", boundary="WordBoundary")
    words = []
    with open(out, "wb") as f:
        async for ch in com.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] == "WordBoundary": words.append((ch["offset"]/1e7, ch["duration"]/1e7, ch["text"]))
    json.dump(words, open(out + ".json", "w"), ensure_ascii=False)
asyncio.run(main(sys.argv[1], sys.argv[2]))
