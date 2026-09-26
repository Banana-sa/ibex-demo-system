# «تعرف من وين جا أكلك؟» — JavaScript version

A second Al-Hajraciyah spot with a new storyline, built as a proper commercial: hook, journey, proof, offer, CTA and a closing button line. Length is 45.0 s, vertical 9:16.

The whole ad renders live in the browser with **HTML canvas and JavaScript**. The same page also rendered the MP4 frame by frame in headless Chromium.

| File | What it is |
|---|---|
| `alhajraciyah_ad.html` | Self-contained interactive player (7.3 MB). Stills, soundtrack and fonts are embedded, and it works offline. Tap a beat to jump to it. |
| `alhajraciyah_ad_js.mp4` | 1080×1920 30 fps master rendered from the page, H.264 + AAC, −14 LUFS |
| `alhajraciyah_ad_js_preview720.mp4` | Light preview |
| `audio/` | Final mix plus stems (music, VO, SFX) |
| `src/` | Page template, build step, mix, shared timeline, and the prompts for images, voices and music |

## Story
| Time | Beat | On screen | VO |
|---|---|---|---|
| 0:00 | Hook | A child's hand holds a date up to the lamplight at the family sufra | Kid: «يُبه.. هالتمر من وين؟» |
| 0:02.6 | Question | Majlis table. Super: **تعرف من وين جا أكلك؟** | Father: «تبي تعرف؟ خلّني أرجّعك للبداية.» |
| 0:05.9 | Rewind | Tape-rewind effect (slice tearing, scanlines, ◀◀), music tape-stops | Rewind SFX |
| 0:06.6 | Palm | Hands cradling a date cluster on the palm, pin «القصيم», **قُطف بيدينا** | «هالتمرة.. قطفناها بيدينا، من نخل القصيم.» |
| 0:10.5 | Wheat | Jareesh bowl, then a hand brushing ripe wheat: **بُرّ عضوي، بلا كيماويات ولا مبيدات** | «وهالجريش.. من بُرٍّ زرعناه بلا كيماويات.» |
| 0:15.0 | Flock | Shepherd with the Naimi flock between palms: **نعيمي.. تربّى حُر** | «والنعيمي.. تربّى حُر، بين النخل.» |
| 0:18.2 | Proof | Elder among the palms: **٦٠ سنة من الأمانة**, then the organic seal and certification chips | «ستين سنة وإحنا نزرع بنفس الأمانة.. بشهادات عضوية عالمية ومحلية…» |
| 0:25.4 | Award | Gold medal over Sukkari dates: **الجائزة الكبرى — جائزة جميل للتمور ٢٠٢٦** | «…وتوّجناها بجائزة جميل للتمور.» |
| 0:29.3 | Offer | Product flat-lay with labels popping in sync (تمور، دبس، بُرّ، تلبينة، عسل) | «تمور، ودبس، وبُر، وتلبينة، وعسل..» |
| 0:33.4 | Delivery | Chilled box opened at the door: **من مزرعتنا لين باب بيتك**, «شحن مبرّد» chip | «من مزرعتنا لين باب بيتك، بشحن مبرّد.» |
| 0:37.3 | CTA | Logo, **من أرضِنا.. إلى سُفرتِكم**, alhajraciyah.com, **اطلب الحين** | «الهجرسية.. من أرضنا، إلى سُفرتكم.» |
| 0:41.5 | Button | The kid's line is set over the end card | Kid: «يُبه.. صدق طعمه غير!» |

All products named are sold at alhajraciyah.com. The certification and award claims come from the farm's site and the Sept 2026 coverage of the Jameel Dates Award.

## How it was made (OpenRouter, $0.84 in total)
- **Stills:** `google/gemini-3.1-flash-image` at 2K, 8 new shots (~$0.81). The jareesh and Sukkari shots are reused from v2. Prompts are in `src/image_prompts.json`.
- **Voices:** `openai/gpt-audio`. The narrator is voice `cedar`, directed as a warm Najdi father and farmer; the kid is voice `coral`, directed as a curious 8-year-old. Each line was recorded separately. Long pauses were tightened to 0.4 s and the lines sped up 4 % with pitch preserved.
- **Score:** `google/lyria-3-pro-preview`, a 60 s Hijaz cue with oud, ney, darbuka and qanun ($0.08).
  - The first 37.2 s play as generated. The edit then jumps exactly 3 bars (11.62 s) ahead into the ending, so the resolution lands under the logo and the kid's line.
  - The Lyria cue's own transition hit at ~6.3 s lines up with the rewind.
- **SFX (synthesized):**
  - Tape-stop, then a reversed and sped-up tape-rewind built from the upcoming music.
  - Whooshes on cuts and ticks on the flat-lay labels.
  - Booms and shimmers on the award and the logo, a cold-mist hiss on the chilled box, and majlis room tone.
- **Mix:** gated side-chain ducking keeps the voice 7–19 dB above the music. The master is loudness-normalised to −14 LUFS.

## Rebuild
```bash
# keys only via environment, never committed
export OPENROUTER_API_KEY=...
python3 src/vo_gen.py                      # voices → vo/
python3 src/mix3.py                        # needs music.wav, vo2/*.wav, timeline.json
python3 src/build.py                       # embeds assets → alhajraciyah_ad.html
PW=$(npm root -g)/playwright node src/rec.js   # renders the MP4 from the page
```
