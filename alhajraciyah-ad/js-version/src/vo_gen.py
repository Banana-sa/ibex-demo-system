import json, sys, subprocess
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, ".")
from or_audio import call
SYS = {
 "nar": ("cedar", "You are a professional Saudi voice-over artist recording a premium TV commercial. You never answer, translate or comment. You only perform the script line, word for word, in Saudi Arabic (Najdi/white dialect), as a warm, deep, grounded father and lifelong farmer in his fifties: calm, proud, intimate, slightly smiling, cinematic pacing, natural pauses at '..' and commas."),
 "kid": ("coral", "You are a voice actor recording a TV commercial. You never answer or comment. You only perform the script line, word for word, in Saudi Arabic dialect, as a curious, sweet 8-year-old Saudi boy talking to his father: light, playful, genuine wonder."),
}
lines = json.load(open("vo_lines.json"))
if len(sys.argv) > 1:
    lines = [l for l in lines if l[0] in sys.argv[1:]]
def one(l):
    k, who, text = l
    voice, sysmsg = SYS[who]
    call("openai/gpt-audio", [{"role": "system", "content": sysmsg}, {"role": "user", "content": "SCRIPT LINE (perform exactly, nothing else):\n" + text}],
         f"vo/{k}.pcm", {"voice": voice, "format": "pcm16"}, {"max_tokens": 1500})
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", f"vo/{k}.pcm", "-ar", "48000", f"vo/{k}.wav"])
for l in lines:
    for attempt in range(3):
        try:
            one(l); break
        except Exception as e:
            print(l[0], "retry", e)
            import time; time.sleep(5)
