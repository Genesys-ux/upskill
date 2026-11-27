# BUMI LAGI NGE-BUG! — 3D Cinematic Animation Pipeline (Blender 4.2 + Python 2.5D Free-Rig)

Animasi 3D sinematik vertikal **9:16 (75 detik, 30 fps)** menggabungkan 6 karakter Python 2.5D Free-Rig (`generator.html` Shared Engine) dengan 3 dunia 3D mid-poly *cel-shaded semi-realistic* + PBR di Blender 4.2 EEVEE Next.

## Struktur Proyek
- `characters/` — Shared Engine (`character_engine_25d.py`) + 6 karakter Free-Rig (`arka`, `kapten_soren`, `astrid`, `kakek_henrik`, `bram`, `clara`) & preset `.json`
- `animation/` — Master 75 detik continuous camera choreography (>30 gerakan kamera, 7 sub-lokasi), biomekanika & sinkronisasi yaw 360° (`storyboard.py`, `render_characters.py`)
- `blender_scenes/` — 3 dunia 3D penuh dengan *set dressing* sibuk beranimasi & *dynamic story lighting* (`scene_diomede.py`, `scene_rjukan.py`, `scene_baarle.py`, `materials_lib.py`)
- `audio/` — Generator VO & dialog Bahasa Indonesia (`edge-tts`), procedural SFX + underscore, serta ekstraksi kurva *lip-sync* (`build_audio.py`)
- `assets/decals/` — Tekstur grafis referensi nyata (papan `USA / RUSSIA 3.8 KM`, hologram `GARIS TANGGAL INTERNASIONAL`, kalender `SENIN`, UI tablet Solspeilet, menu pajak ganda Baarle, ubin `+ B | NL`, & dua plat nomor rumah Belgia/Belanda)
- `.github/workflows/render_animation.yml` — Workflow GitHub Actions paralel untuk render **4 Clip Preview** (720×1280) maupun **Full Master 75 Detik** (1080×1920)

## Cara Render di GitHub Actions
1. **Otomatis saat `git push` ke `main`:** langsung merender paralel **4 Clip Preview + Showcase Reel + Keyframe Contact Sheets** (`bumi-ngebug-preview-clips`).
2. **Manual (`Actions` → `Render 3D Animation — Bumi Lagi Nge-Bug!` → `Run workflow`):**
   - `preview_clips` — Render cepat 4 clip preview (720×1280) untuk penilaian.
   - `full_75s` — Render penuh 75 detik Full HD (1080×1920, 6 chunk paralel + audio master).
