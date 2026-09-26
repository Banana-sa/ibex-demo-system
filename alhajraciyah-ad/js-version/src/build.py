import base64, json
def uri(path, mime): return f"data:{mime};base64," + base64.b64encode(open(path, "rb").read()).decode()
s = open("template.html").read()
F = "/tmp/claude-0/ad/fonts/"
s = s.replace("__F_KUFI__", uri(F + "ReemKufi%5Bwght%5D.ttf", "font/ttf")).replace("__F_RUQAA__", uri(F + "ArefRuqaa-Bold.ttf", "font/ttf"))
s = s.replace("__F_AMIRI__", uri(F + "Amiri-Bold.ttf", "font/ttf")).replace("__F_TAJ_M__", uri(F + "Tajawal-Medium.ttf", "font/ttf")).replace("__F_TAJ_B__", uri(F + "Tajawal-Bold.ttf", "font/ttf"))
assets = {k: uri(f"web/{k}.jpg", "image/jpeg") for k in ["kid", "table", "harvest", "jareesh", "wheat", "flock", "elder", "sukari", "flatlay", "delivery"]}
assets["logo"] = uri("web/logo.png", "image/png")
s = s.replace("__ASSETS__", json.dumps(assets)).replace("__TIMELINE__", json.dumps(json.load(open("timeline.json")), ensure_ascii=False))
s = s.replace("__AUDIO__", uri("soundtrack3.mp3", "audio/mpeg"))
open("alhajraciyah_ad.html", "w").write(s)
print(round(len(s) / 1e6, 2), "MB")
