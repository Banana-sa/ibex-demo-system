# الهجرسية — إعلان ٤٣ ثانية | Al-Hajraciyah 43s Ad

Vertical 9:16 (1080×1920, 30 fps) spot for Snapchat, TikTok, Reels and Shorts, with Arabic voice-over and an original score in maqam Hijaz.

| File | What it is |
|---|---|
| `alhajraciyah_ad_43s.mp4` | Final master: H.264 video, AAC 320k audio, loudness normalised to −14 LUFS |
| `alhajraciyah_ad_poster.jpg` | Thumbnail / cover frame |
| `audio/soundtrack.wav` | Full mix, 48 kHz stereo |
| `audio/stem_*.wav` | Stems for re-editing: music (already ducked), VO, SFX + ambience |
| `src/render.py` | Frame renderer: every scene is procedural, plus the store's real product photos |
| `src/audio.py` | Score and sound design, all synthesised in code |
| `src/vo.txt`, `src/tts*.py` | VO script and the TTS helpers (voice `ar-SA-HamedNeural`) |

## The story (from the farm's own sources)
- Al-Hajraciyah is a pioneering organic farm in **Al-Qassim**, with local and international organic certification for crops **and** livestock (alhajraciyah.com).
- The farm's roots go back to the **1960s**, when the current farmer started working the land beside his father at **age seven**. It has kept farming without chemicals ever since (farm profile on azkabasket.com).
- **Sept 2026:** the farm won the **grand prize of the first Jameel Dates Award (جائزة جميل للتمور)** at the Buraydah International Dates Festival, for its Sukkari dates.

## Products shown
Every product in the ad is from the live catalogue at alhajraciyah.com, shown with the store's own photos. Nothing was invented:

| Section | Products |
|---|---|
| من نخيلنا (from our palms) | الونّانة · الخلاص · دبس التمر |
| من حقولنا (from our fields) | دقيق البُرّ · الجريش · التلبينة · قهوة الشعير |
| على سُفرتكم (on your table) | المطازيز · معمول الهجرسية |
| Award scene background | سكري (the award-winning variety) |

## Script and timeline

| Time | Scene | VO (Arabic) | Meaning |
|---|---|---|---|
| 0:00–0:05 | Starry night over Qassim turns to sunrise over palm groves. Title: **القصيم** | في قلبِ القصيم، بدأت الحكايةُ قبلَ ستّينَ عاماً. | In the heart of Qassim, the story began sixty years ago. |
| 0:05–0:11 | Sepia memory: a boy walks hand in hand with his father among the palms | طفلٌ في السابعة، خلفَ أبيه بين النخيل، يتعلّمُ أنّ الأرضَ أمانة. | A seven-year-old behind his father among the palms, learning that the land is a trust. |
| 0:11–0:16 | Golden wheat at sunset. **بلا كيماويات / بلا استعجال** | بلا كيماويّات، بلا استعجال، كما زرعها الأجداد. | No chemicals, no rushing, the way our grandfathers farmed. |
| 0:16–0:20 | Product cards: dates | من نخيلِنا: الوَنّانة، والخلاص، ودِبسُ التمر. | From our palms… |
| 0:20–0:26 | Product cards: grains | ومن حقولِنا: البُرّ، والجَريش، والتَّلبينة، وقهوةُ الشعير. | From our fields… |
| 0:26–0:30 | Product cards: sweets and traditional food | وعلى سُفرتِكم: المَطازيز، ومعمولُ الهجرسيّة. | On your table… |
| 0:30–0:36 | Organic seal, certification chips, gold medal. **الجائزة الكبرى — جائزة جميل للتمور ٢٠٢٦** | موثّقةٌ عالميّاً ومحلّيّاً، وتُوِّجت بجائزةِ جميل للتمور. | Certified internationally and locally, crowned with the Jameel Dates Award. |
| 0:36–0:43 | Logo end card: **من أرضِنا.. إلى سُفرتِكم**, alhajraciyah.com, شحن مبرّد • استلام من المتجر | الهجرسيّة. من أرضِنا، إلى سُفرتِكم. | Al-Hajraciyah. From our land to your table. |

Each product card cuts in 0.25 s before its name is spoken. The cut times come from TTS word-boundary timestamps.

## Sound design
- **Score:** maqam **Hijaz on D**, 98 BPM.
  - Karplus–Strong **oud** with bowl-back body resonances.
  - Breathy **ney** with delayed vibrato.
  - **Darbuka** playing *maqsum* (dum-tek-tek-dum-tek), with **daf** and **riq** jingles.
  - Low string pads that follow the section chords: i, iv, VII, then back to i.
- **Arc:**
  1. Night crickets and a lone ney call.
  2. A tender oud *taqsim* over the memory scene.
  3. An oud ostinato and daf heartbeat over the wheat.
  4. A darbuka roll into the full groove for the products.
  5. An impact and a soaring ney for the award.
  6. A signature boom, then a final oud strum and resolve on the logo.
- **Foley and ambience:**
  - Desert wind throughout, and dawn birds.
  - Footsteps in sand timed to the walking father and son.
  - Old-film crackle in the memory scene and wheat rustle in the field.
  - Whoosh plus shimmer on every product push, and risers into each hit.
- **Mix:** the VO has a high-pass, presence lift and levelling. Music and ambience are side-chain ducked under the voice, the mix is glue-compressed and soft-limited to −14 LUFS integrated, and output is 48 kHz stereo.

## Visual language
- **Colours:** brand maroon from the logo, date gold and cream.
- **Motifs:** the logo's arch repeats as a pattern, and every card carries an «عضوي / ORGANIC» seal.
- **Type:**
  - Reem Kufi for headlines.
  - Aref Ruqaa for product names.
  - Amiri for the story lines.
  - Tajawal for UI text.
- All Arabic text is revealed right to left with a soft wipe, following the reading direction.
- Film grain and vignette run throughout. The memory scene has a sepia grade with light leaks and scratches.

## Rebuild
```bash
pip install pillow numpy scipy imageio-ffmpeg edge-tts
# fonts (Google Fonts, OFL) go in fonts/, product photos in img/ (see PRODUCTS in render.py)
python3 src/render.py video video_silent.mp4
python3 src/audio.py
ffmpeg -i video_silent.mp4 -i soundtrack.wav -c:v copy -c:a aac -b:a 320k -shortest alhajraciyah_ad_43s.mp4
```

> Before running paid media, get the farm's sign-off on the award wording and on using their product photos.
