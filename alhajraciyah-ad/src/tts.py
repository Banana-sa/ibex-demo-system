import sys, ssl, asyncio
import edge_tts.communicate as c
c._SSL_CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
import edge_tts
async def main(text, voice, out, rate="+0%", pitch="+0Hz"):
    com = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, boundary="SentenceBoundary")
    await com.save(out)
if __name__ == "__main__":
    a = sys.argv
    asyncio.run(main(a[1], a[2], a[3], *(a[4:])))
