"""Master configuration, 75-second script timeline, and preview clip definitions for BUMI LAGI NGE-BUG!"""
from __future__ import annotations

import os
from typing import Any, Dict, List

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CHAR_DIR = os.path.join(PROJECT_ROOT, "characters")
AUDIO_DIR = os.path.join(PROJECT_ROOT, "audio")
DECALS_DIR = os.path.join(PROJECT_ROOT, "assets", "decals")
BUILD_DIR = os.path.join(PROJECT_ROOT, "build")

FPS = 30
DURATION_SEC = 75.0
TOTAL_FRAMES = int(round(DURATION_SEC * FPS))  # 2250 frames

# Render presets (9:16 vertical)
PREVIEW_RES = (720, 1280)
MASTER_RES = (1080, 1920)

# Scene ranges in frames (inclusive start, exclusive end)
SCENE_RANGES = {
    "diomede": (0, 750),      # 00:00.0 – 00:25.0 (Act 0 Hook + Act 1 + Lens-Flare Whip Transition)
    "rjukan": (750, 1470),    # 00:25.0 – 00:49.0 (Act 2A Dark Noon + Act 2B Golden God Ray + Sunglasses Match-Cut)
    "baarle": (1470, 2250),   # 00:49.0 – 00:75.0 (Act 3A Cafe Border + Act 3B Comedy + Finale Loop Hook)
}

# 4 curated preview clips for user review (cover all 3 worlds, all 6 characters, all transitions)
PREVIEW_CLIPS: List[Dict[str, Any]] = [
    {
        "id": "clip_01_diomede_hook",
        "title": "Clip 1 — Hook 2 Detik & Pulau Diomede (00:00–00:14)",
        "scene": "diomede",
        "start_sec": 0.0,
        "end_sec": 14.8,
        "start_frame": 0,
        "end_frame": 444,
    },
    {
        "id": "clip_02_es_retak_ke_rjukan",
        "title": "Clip 2 — Jembatan Es Retak & Transisi ke Rjukan Gelap (00:19–00:36)",
        "scene": "multi",
        "segments": [
            {"scene": "diomede", "start_frame": 570, "end_frame": 750},
            {"scene": "rjukan", "start_frame": 750, "end_frame": 1086},
        ],
        "start_sec": 19.0,
        "end_sec": 36.2,
        "start_frame": 570,
        "end_frame": 1086,
    },
    {
        "id": "clip_03_godray_ke_baarle",
        "title": "Clip 3 — Sorotan Matahari Rjukan & Match-Cut ke Kafe Baarle (00:36–00:59)",
        "scene": "multi",
        "segments": [
            {"scene": "rjukan", "start_frame": 1086, "end_frame": 1470},
            {"scene": "baarle", "start_frame": 1470, "end_frame": 1776},
        ],
        "start_sec": 36.2,
        "end_sec": 59.2,
        "start_frame": 1086,
        "end_frame": 1776,
    },
    {
        "id": "clip_04_baarle_komedi_penutup",
        "title": "Clip 4 — Komedi Clara, Rumah 2 Bendera & Loop Penutup (00:59–00:75)",
        "scene": "baarle",
        "start_sec": 59.2,
        "end_sec": 75.0,
        "start_frame": 1776,
        "end_frame": 2250,
    },
]

# 30 parallel shards aligned cleanly to the 3 Blender worlds (no shard loads 2 scenes!):
# - World 1 (diomede, 0..750):    10 shards x 75 frames = 750 frames
# - World 2 (rjukan,  750..1470): 10 shards x 72 frames = 720 frames
# - World 3 (baarle,  1470..2250): 10 shards x 78 frames = 780 frames
SHARDS_30: List[Dict[str, Any]] = []
for _i in range(10):
    SHARDS_30.append({"shard": _i, "id": f"shard_{_i:02d}", "scene": "diomede", "start_frame": _i * 75, "end_frame": (_i + 1) * 75})
for _i in range(10):
    SHARDS_30.append({"shard": 10 + _i, "id": f"shard_{10 + _i:02d}", "scene": "rjukan", "start_frame": 750 + _i * 72, "end_frame": 750 + (_i + 1) * 72})
for _i in range(10):
    SHARDS_30.append({"shard": 20 + _i, "id": f"shard_{20 + _i:02d}", "scene": "baarle", "start_frame": 1470 + _i * 78, "end_frame": 1470 + (_i + 1) * 78})

# Legacy chunk aliases
FULL_CHUNKS: List[Dict[str, Any]] = SHARDS_30

# Character physical heights in meters (matches cast lineup proportions)
CHAR_HEIGHTS_M: Dict[str, float] = {
    "arka": 1.85,
    "kapten_soren": 1.94,
    "astrid": 1.82,
    "kakek_henrik": 1.68,
    "bram": 1.96,
    "clara": 1.76,
}

# Edge-TTS distinct Indonesian vocal profiles per character (fast YouTube Shorts / Reels tempo)
VOICE_PROFILES: Dict[str, Dict[str, str]] = {
    "arka": {"voice": "id-ID-ArdiNeural", "rate": "+28%", "pitch": "+5Hz"},
    "kapten_soren": {"voice": "id-ID-ArdiNeural", "rate": "+14%", "pitch": "-16Hz"},
    "astrid": {"voice": "id-ID-GadisNeural", "rate": "+20%", "pitch": "+2Hz"},
    "kakek_henrik": {"voice": "id-ID-ArdiNeural", "rate": "+6%", "pitch": "-12Hz"},
    "bram": {"voice": "id-ID-ArdiNeural", "rate": "+20%", "pitch": "-3Hz"},
    "clara": {"voice": "id-ID-GadisNeural", "rate": "+22%", "pitch": "+7Hz"},
}

# Complete 75-second dialogue & VO lines (100% faithful to user brief, balanced exact speech budgets)
DIALOGUE_LINES: List[Dict[str, Any]] = [
    {
        "id": "L01_hook_arka",
        "speaker": "arka",
        "start_sec": 0.10,
        "max_end_sec": 4.20,
        "text": "Bola salju ini cuma butuh lima menit buat nyebrang... tapi secara kalender, dia baru mendarat besok!",
    },
    {
        "id": "L02_diomede_arka",
        "speaker": "arka",
        "start_sec": 4.30,
        "max_end_sec": 12.20,
        "text": "Ini Pulau Diomede! Jarak antara Alaska di sini dan Rusia di sana cuma tiga koma delapan kilometer. Dekat banget, kan? Tapi Garis Tanggal Internasional persis motong di tengah-tengahnya!",
    },
    {
        "id": "L03_diomede_soren",
        "speaker": "kapten_soren",
        "start_sec": 12.30,
        "max_end_sec": 16.60,
        "text": "Di sini baru Senin pagi... di seberang sana udah Selasa subuh! Beda dua puluh satu jam!",
    },
    {
        "id": "L04_diomede_ice_arka",
        "speaker": "arka",
        "start_sec": 16.75,
        "max_end_sec": 23.85,
        "text": "Gokilnya, pas musim dingin lautnya beku jadi jembatan es! Secara teknis kamu bisa jalan kaki ke masa depan, asal siap dikejar patroli, karena nyeberangnya ilegal!",
    },
    {
        "id": "L05_rjukan_intro_arka",
        "speaker": "arka",
        "start_sec": 25.15,
        "max_end_sec": 32.35,
        "text": "Masih kurang aneh? Selamat datang di Rjukan, Norwegia! Kota ini kejepit gunung super tinggi, jadi selama enam bulan penuh tiap tahun... matahari gak pernah nyentuh tanahnya!",
    },
    {
        "id": "L06_rjukan_astrid",
        "speaker": "astrid",
        "start_sec": 32.50,
        "max_end_sec": 36.15,
        "radio_fx": True,
        "text": "Cermin satu sampai tiga aktif. Saatnya bikin siang!",
    },
    {
        "id": "L07_rjukan_mirrors_arka",
        "speaker": "arka",
        "start_sec": 36.45,
        "max_end_sec": 45.35,
        "text": "Solusi mereka? Pasang tiga cermin raksasa otomatis di puncak gunung sejak 2013 buat mantulin sinar matahari langsung ke alun-alun! Cuma di sini orang berjemur di tengah salju pakai matahari pantulan!",
    },
    {
        "id": "L08_rjukan_henrik",
        "speaker": "kakek_henrik",
        "start_sec": 45.50,
        "max_end_sec": 48.35,
        "text": "Lumayan, Nak... vitamin D gratis!",
    },
    {
        "id": "L09_baarle_intro_arka",
        "speaker": "arka",
        "start_sec": 49.30,
        "max_end_sec": 56.55,
        "text": "Terakhir, kota paling bikin GPS menyerah: Baarle! Di sini, perbatasan Belanda dan Belgia bukan garis lurus, tapi potongan puzzle yang nabrak rumah, toko, sampai meja kafe!",
    },
    {
        "id": "L10_baarle_bram",
        "speaker": "bram",
        "start_sec": 56.65,
        "max_end_sec": 59.40,
        "text": "Kopi diseduh di Belanda... diantar lintas negara ke Belgia!",
    },
    {
        "id": "L11_baarle_door_arka",
        "speaker": "arka",
        "start_sec": 59.55,
        "max_end_sec": 66.75,
        "text": "Kalau rumahmu terbelah dua, kewarganegaraanmu ditentukan satu hal: pintu depanmu hadap negara mana! Mau pindah negara? Gampang, tinggal bongkar tembok, pindahin pintu!",
    },
    {
        "id": "L12_baarle_clara",
        "speaker": "clara",
        "start_sec": 66.85,
        "max_end_sec": 69.95,
        "text": "Jadi kalau aku geser kursi sedikit... pajak kopiku beda?!",
    },
    {
        "id": "L13_outro_arka",
        "speaker": "arka",
        "start_sec": 70.10,
        "max_end_sec": 74.65,
        "text": "Bumi kita penuh aturan yang lebih absurd dari game! Dari tiga lokasi ini, mana yang paling pengen kamu datengin?",
    },
]
