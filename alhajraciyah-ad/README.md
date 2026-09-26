# الهجرسية — إعلان ٤٥ ثانية | Al-Hajraciyah 45s Ad

Vertical 9:16 (1080×1920, 30 fps) spot for Snapchat, TikTok, Reels and Shorts, with Arabic voice-over and an original score in maqam Hijaz.

| File | What it is |
|---|---|
| `alhajraciyah_ad_45s.mp4` | Final master: H.264 video, AAC 320k audio, loudness normalised to −14 LUFS |
| `alhajraciyah_ad_45s_preview720.mp4` | Light 720p preview |
| `images/` | The 16 AI-generated photoreal scenes and product shots used in the ad |
| `alhajraciyah_ad_poster.jpg` | Thumbnail / cover frame |
| `audio/soundtrack.wav` | Full mix, 48 kHz stereo |
| `audio/stem_*.wav` | Stems for re-editing: music (already ducked), VO, SFX + ambience |
| `src/render2.py` | Frame renderer for this cut: camera moves, grading, transitions and Arabic type (imports helpers from `render.py`, the first cut) |
| `src/audio2.py` | Score and sound design for this cut, all synthesised in code |
| `src/gen_images.py`, `src/image_prompts.json` | Image generation through OpenRouter (`google/gemini-3.1-flash-image`); reads `OPENROUTER_API_KEY` from the environment |
| `src/vo.txt`, `src/tts*.py` | VO script and the TTS helpers (voice `ar-SA-HamedNeural`) |

## The story (from the farm's own sources)
- Al-Hajraciyah is a pioneering organic farm in **Al-Qassim**, with local and international organic certification for crops **and** livestock (alhajraciyah.com).
- The farm's roots go back to the **1960s**, when the current farmer started working the land beside his father at **age seven**. It has kept farming without chemicals ever since (farm profile on azkabasket.com).
- **Sept 2026:** the farm won the **grand prize of the first Jameel Dates Award (جائزة جميل للتمور)** at the Buraydah International Dates Festival, for its Sukkari dates.

## Products shown
Every product named in the ad is sold at alhajraciyah.com; nothing was invented. The visuals are AI-generated hero shots instead of the store's catalogue photos, and no packaging or labels are shown:

| Section | Products |
|---|---|
| من نخيلنا (from our palms) | الونّانة · الخلاص · دبس التمر |
| من حقولنا (from our fields) | دقيق البُرّ · الجريش · التلبينة · قهوة الشعير |
| على سُفرتكم (on your table) | المطازيز · معمول الهجرسية · العسل العضوي (acacia) |
| Certification scene | Naimi sheep and goats grazing among the palms (the farm's certified organic livestock) |
| Award scene background | سكري (the award-winning variety) |

## Script and timeline

| Time | Scene | VO (Arabic) | Meaning |
|---|---|---|---|
| 0:00–0:05 | Night over the Qassim palm farm turns to sunrise. Title: **القصيم** | في قلبِ القصيم، بدأت الحكايةُ قبلَ ستّينَ عاماً. | In the heart of Qassim, the story began sixty years ago. |
| 0:05–0:11 | 1960s-style film memory: a boy in a thobe walks hand in hand with his father (shemagh) among the palms | طفلٌ في السابعة، خلفَ أبيه بين النخيل، يتعلّمُ أنّ الأرضَ أمانة. | A seven-year-old behind his father among the palms, learning that the land is a trust. |
| 0:11–0:16 | Golden wheat at sunset. **بلا كيماويات / بلا استعجال** | بلا كيماويّات، بلا استعجال، كما زرعها الأجداد. | No chemicals, no rushing, the way our grandfathers farmed. |
| 0:16–0:20 | Full-bleed product heroes: dates | من نخيلِنا: الوَنّانة، والخلاص، ودِبسُ التمر. | From our palms… |
| 0:20–0:26 | Product heroes: grains | ومن حقولِنا: البُرّ، والجَريش، والتَّلبينة، وقهوةُ الشعير. | From our fields… |
| 0:26–0:32 | Product heroes: traditional food, sweets, honey | وعلى سُفرتِكم: المَطازيز، ومعمولُ الهجرسيّة، والعسلُ العضوي. | On your table… |
| 0:32–0:39 | Livestock among the palms with an organic seal and certification chips, then a gold medal over Sukkari dates. **الجائزة الكبرى — جائزة جميل للتمور ٢٠٢٦** | موثّقةٌ عالميّاً ومحلّيّاً، في الزراعةِ والمواشي، وتُوِّجت بجائزةِ جميل للتمور. | Certified internationally and locally, in crops and livestock, crowned with the Jameel Dates Award. |
| 0:39–0:45.5 | Logo end card: **من أرضِنا.. إلى سُفرتِكم**, alhajraciyah.com, شحن مبرّد • استلام من المتجر | الهجرسيّة. من أرضِنا، إلى سُفرتِكم. | Al-Hajraciyah. From our land to your table. |

Each product shot slides in from the left, the right-to-left reading direction, 0.25 s before its name is spoken. The cut times come from TTS word-boundary timestamps.

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
  - Footsteps in the sand under the father-and-son scene.
  - Old-film crackle in the memory scene and wheat rustle in the field.
  - Whoosh plus shimmer on every product push, and risers into each hit.
- **Mix:** the VO has a high-pass, presence lift and levelling. Music and ambience are side-chain ducked under the voice, the mix is glue-compressed and soft-limited to −14 LUFS integrated, and output is 48 kHz stereo.

## Visual language
- **Colours:** brand maroon from the logo, date gold and cream.
- **Motifs:** the logo's arch repeats as a pattern on the end card, and every product shot carries an «عضوي / ORGANIC» seal.
- **Camera:** slow push-ins and drifts on every shot, slides with motion blur between products, a light sweep as each product lands, and floating pollen.
- **Type:**
  - Reem Kufi for headlines.
  - Aref Ruqaa for product names.
  - Amiri for the story lines.
  - Tajawal for UI text.
- All Arabic text is revealed right to left with a soft wipe, following the reading direction.
- Film grain and vignette run throughout. The opening grades from night to sunrise, and the memory scene has a sepia grade with light leaks and scratches.

## Rebuild
```bash
pip install pillow numpy scipy imageio-ffmpeg edge-tts
# fonts (Google Fonts, OFL) go in fonts/; generated PNGs in gen/ (or convert images/*.jpg); logo.png in img/
OPENROUTER_API_KEY=... python3 src/gen_images.py src/image_prompts.json   # only if regenerating images
python3 src/render2.py video video_silent.mp4
python3 src/audio2.py
ffmpeg -i video_silent.mp4 -i soundtrack2.wav -c:v copy -c:a aac -b:a 320k -shortest alhajraciyah_ad_45s.mp4
```

> Before running paid media, get the farm's sign-off on the award wording. The product images are AI-generated illustrations of the product types, not photos of the farm's actual stock.
