"""Build full 75-second VO, character dialogue, procedural SFX, upbeat underscore, and per-character lip-sync curves."""
from __future__ import annotations

import asyncio
import json
import math
import os
import shutil
import subprocess
import sys
import wave
from typing import Any, Dict, List

import numpy as np
from scipy import signal

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from project_config import AUDIO_DIR, DIALOGUE_LINES, DURATION_SEC, FPS, TOTAL_FRAMES, VOICE_PROFILES

SR = 48000


def write_wav_stereo(path: str, stereo: np.ndarray, sr: int = SR) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    clipped = np.clip(stereo, -0.98, 0.98)
    pcm = (clipped * 32767.0).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())


def read_audio_mono_ffmpeg(path: str, sr: int = SR) -> np.ndarray:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg required to decode MP3 stems on render host.")
    cmd = [ffmpeg, "-v", "error", "-i", path, "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    samples = np.frombuffer(proc.stdout, dtype=np.int16).astype(np.float32) / 32768.0
    return samples


def time_stretch_ffmpeg(in_mp3: str, out_wav: str, max_dur: float, radio_fx: bool = False) -> np.ndarray:
    """Decode TTS MP3, trim trailing silence, fit cleanly within max_dur, optionally apply walkie-talkie EQ."""
    raw = read_audio_mono_ffmpeg(in_mp3, SR)
    if len(raw) == 0:
        return np.zeros(int(0.1 * SR), dtype=np.float32)

    # Trim leading/trailing near-silence
    env = np.abs(raw)
    nz = np.where(env > 0.015)[0]
    if len(nz) > 0:
        start_i = max(0, int(nz[0]) - int(0.03 * SR))
        end_i = min(len(raw), int(nz[-1]) + int(0.06 * SR))
        raw = raw[start_i:end_i]

    cur_dur = len(raw) / float(SR)
    tempo = 1.0
    if cur_dur > max_dur and max_dur > 0.3:
        tempo = min(1.42, cur_dur / max_dur)

    ffmpeg = shutil.which("ffmpeg")
    filters = []
    if tempo > 1.01:
        filters.append(f"atempo={tempo:.4f}")
    if radio_fx:
        # Walkie-talkie bandpass + subtle crunch for Astrid
        filters.append("highpass=f=480,lowpass=f=3200,acompressor=threshold=0.12:ratio=4")
    else:
        filters.append("highpass=f=85,acompressor=threshold=0.18:ratio=2.5:makeup=1.2")

    # Write temp wav then run ffmpeg filter cleanly
    tmp_in = out_wav + ".raw.wav"
    pcm = (np.clip(raw, -0.98, 0.98) * 32767.0).astype(np.int16)
    with wave.open(tmp_in, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())

    cmd = [
        ffmpeg, "-y", "-v", "error", "-i", tmp_in,
        "-af", ",".join(filters),
        "-ac", "1", "-ar", str(SR), "-f", "s16le", "-",
    ]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    os.remove(tmp_in)
    out = np.frombuffer(proc.stdout, dtype=np.float32 if False else np.int16).astype(np.float32) / 32768.0
    # Normalize peak to -1.5 dBFS (~0.84)
    pk = float(np.max(np.abs(out))) if len(out) else 1.0
    if pk > 1e-4:
        out = out * (0.84 / pk)
    return out


async def generate_all_tts_mp3(stems_dir: str) -> Dict[str, str]:
    import edge_tts

    os.makedirs(stems_dir, exist_ok=True)
    paths: Dict[str, str] = {}
    for line in DIALOGUE_LINES:
        out_mp3 = os.path.join(stems_dir, f"{line['id']}.mp3")
        paths[line["id"]] = out_mp3
        if os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 500:
            continue
        prof = VOICE_PROFILES[line["speaker"]]
        comm = edge_tts.Communicate(
            line["text"],
            voice=prof["voice"],
            rate=prof["rate"],
            pitch=prof["pitch"],
        )
        await comm.save(out_mp3)
        print(f"[TTS] Generated {line['id']} ({line['speaker']})")
    return paths


def _bandpass(noise: np.ndarray, low_hz: float, high_hz: float, order: int = 3) -> np.ndarray:
    sos = signal.butter(order, [low_hz / (SR * 0.5), high_hz / (SR * 0.5)], btype="bandpass", output="sos")
    return signal.sosfilt(sos, noise).astype(np.float32)


def _add_stereo(buf: np.ndarray, mono: np.ndarray, start_sec: float, gain: float = 1.0, pan: float = 0.0) -> None:
    s0 = int(round(start_sec * SR))
    if s0 >= buf.shape[0] or len(mono) == 0:
        return
    n = min(len(mono), buf.shape[0] - s0)
    if s0 < 0:
        mono = mono[-s0:]
        n = min(len(mono), buf.shape[0])
        s0 = 0
    if n <= 0:
        return
    lg = gain * math.cos((pan + 1.0) * math.pi * 0.25)
    rg = gain * math.sin((pan + 1.0) * math.pi * 0.25)
    buf[s0 : s0 + n, 0] += mono[:n] * lg
    buf[s0 : s0 + n, 1] += mono[:n] * rg


def synth_sfx_and_music(total_samples: int) -> np.ndarray:
    """Procedural cinematic SFX + energetic rhythmic underscore synchronized to all 75s story beats."""
    rng = np.random.default_rng(20261127)
    mix = np.zeros((total_samples, 2), dtype=np.float32)
    t_all = np.arange(total_samples, dtype=np.float32) / float(SR)

    # 1. AMBIENCES PER LOCATION (subtle spatial beds)
    # 00:00-00:25 Arctic Bering Strait wind bed
    n_arc = int(25.2 * SR)
    w_noise = rng.standard_normal(n_arc).astype(np.float32)
    w_band = _bandpass(w_noise, 240, 1150)
    t_arc = np.arange(n_arc, dtype=np.float32) / float(SR)
    w_mod = 0.65 + 0.35 * np.sin(2 * math.pi * 0.28 * t_arc)
    w_env = np.minimum(1.0, t_arc / 0.4) * np.minimum(1.0, (25.2 - t_arc) / 0.6)
    _add_stereo(mix, w_band * w_mod * w_env, 0.0, gain=0.14, pan=-0.1)

    # 00:25-00:49 Rjukan cold valley wind -> warm acoustic hum when mirrors hit at 36.5s
    n_rju = int(24.0 * SR)
    r_noise = _bandpass(rng.standard_normal(n_rju).astype(np.float32), 180, 750)
    t_rju = np.arange(n_rju, dtype=np.float32) / float(SR)
    r_env = np.minimum(1.0, t_rju / 0.5) * np.minimum(1.0, (24.0 - t_rju) / 0.5)
    _add_stereo(mix, r_noise * r_env, 25.0, gain=0.10, pan=0.05)

    # 00:49-00:75 Baarle cozy European café ambience + espresso hiss
    n_baa = int(26.0 * SR)
    b_noise = _bandpass(rng.standard_normal(n_baa).astype(np.float32), 450, 2200)
    t_baa = np.arange(n_baa, dtype=np.float32) / float(SR)
    b_env = np.minimum(1.0, t_baa / 0.5) * np.minimum(1.0, (26.0 - t_baa) / 0.4)
    _add_stereo(mix, b_noise * b_env, 49.0, gain=0.06, pan=0.0)

    # 2. HERO SFX CUES FROM BRIEF
    def whoosh(dur: float, f0: float, f1: float) -> np.ndarray:
        n = int(dur * SR)
        t = np.linspace(0.0, 1.0, n, dtype=np.float32)
        nz = rng.standard_normal(n).astype(np.float32)
        bp = _bandpass(nz, min(f0, f1), max(f0, f1))
        env = np.maximum(0.0, np.sin(math.pi * t)) ** 1.6
        tone = np.sin(2 * math.pi * (f0 * 0.4 + (f1 - f0) * 0.25 * t) * t * dur) * 0.18
        return (bp * 1.4 + tone) * env

    def glitch_burst(dur: float = 0.22) -> np.ndarray:
        n = int(dur * SR)
        t = np.arange(n, dtype=np.float32) / float(SR)
        # Stepped digital pitch hops
        step_freq = np.where((t * 40).astype(int) % 2 == 0, 1420.0, 880.0)
        sig = np.sign(np.sin(2 * math.pi * step_freq * t)) * 0.22
        env = np.exp(-t * 9.0) * (1.0 - 0.5 * ((t * 55).astype(int) % 2))
        return (sig * env).astype(np.float32)

    def chime(dur: float = 0.85, base_f: float = 1174.66) -> np.ndarray:
        n = int(dur * SR)
        t = np.arange(n, dtype=np.float32) / float(SR)
        s1 = np.sin(2 * math.pi * base_f * t) * np.exp(-t * 4.5)
        s2 = np.sin(2 * math.pi * base_f * 1.5 * t) * np.exp(-t * 6.0) * 0.5
        s3 = np.sin(2 * math.pi * base_f * 2.0 * t) * np.exp(-t * 8.0) * 0.35
        return (s1 + s2 + s3).astype(np.float32) * 0.45

    def ice_crack(dur: float = 0.55) -> np.ndarray:
        n = int(dur * SR)
        t = np.arange(n, dtype=np.float32) / float(SR)
        nz = _bandpass(rng.standard_normal(n).astype(np.float32), 1600, 6800)
        clicks = np.exp(-((t - 0.04) ** 2) / 0.00018) + 0.8 * np.exp(-((t - 0.14) ** 2) / 0.00025) + 0.6 * np.exp(-((t - 0.27) ** 2) / 0.0004)
        low_snap = np.sin(2 * math.pi * 145.0 * t) * np.exp(-t * 14.0) * 0.5
        return (nz * clicks * 2.4 + low_snap).astype(np.float32)

    def hydraulic_hum(dur: float = 3.2) -> np.ndarray:
        n = int(dur * SR)
        t = np.arange(n, dtype=np.float32) / float(SR)
        freq = 72.0 + 28.0 * np.sin(math.pi * t / dur)
        sig = (np.sin(2 * math.pi * freq * t) * 0.5 + np.sin(2 * math.pi * freq * 2.01 * t) * 0.25)
        env = np.minimum(1.0, t / 0.35) * np.minimum(1.0, (dur - t) / 0.45)
        return (sig * env).astype(np.float32) * 0.35

    def light_boom(dur: float = 1.6) -> np.ndarray:
        n = int(dur * SR)
        t = np.arange(n, dtype=np.float32) / float(SR)
        sub = np.sin(2 * math.pi * (82.0 * np.exp(-t * 1.1) + 44.0) * t) * np.exp(-t * 2.2)
        chord = (
            np.sin(2 * math.pi * 261.63 * t)
            + np.sin(2 * math.pi * 329.63 * t)
            + np.sin(2 * math.pi * 392.00 * t)
            + np.sin(2 * math.pi * 523.25 * t)
        ) * 0.14 * np.exp(-t * 1.8) * np.minimum(1.0, t / 0.08)
        return (sub * 0.55 + chord).astype(np.float32)

    def espresso_hiss(dur: float = 2.4) -> np.ndarray:
        n = int(dur * SR)
        t = np.arange(n, dtype=np.float32) / float(SR)
        nz = _bandpass(rng.standard_normal(n).astype(np.float32), 2800, 9500)
        env = np.minimum(1.0, t / 0.15) * np.exp(-t * 0.9)
        return (nz * env).astype(np.float32) * 0.24

    def spoon_clink(dur: float = 0.45) -> np.ndarray:
        n = int(dur * SR)
        t = np.arange(n, dtype=np.float32) / float(SR)
        c1 = (np.sin(2 * math.pi * 3280 * t) + 0.6 * np.sin(2 * math.pi * 4910 * t)) * np.exp(-t * 16.0)
        c2 = (np.sin(2 * math.pi * 3310 * np.maximum(0, t - 0.12)) * (t > 0.12)) * np.exp(-np.maximum(0, t - 0.12) * 18.0) * 0.7
        return (c1 + c2).astype(np.float32) * 0.38

    # Place exact story SFX
    _add_stereo(mix, whoosh(0.65, 280, 1950), 0.0, gain=0.42)
    _add_stereo(mix, glitch_burst(0.24), 0.35, gain=0.35, pan=0.15)
    _add_stereo(mix, whoosh(0.55, 320, 1600), 9.0, gain=0.32)       # Launch over Bering Strait
    _add_stereo(mix, chime(0.5, 1320.0), 11.0, gain=0.22)           # Date Line slice
    _add_stereo(mix, ice_crack(0.6), 19.6, gain=0.52)               # Arka steps on thin ice!
    _add_stereo(mix, chime(0.9, 1396.9), 24.05, gain=0.44)          # Lens flare chime
    _add_stereo(mix, whoosh(0.75, 260, 2400), 24.25, gain=0.50)     # Whip-pan transition 1 -> 2
    _add_stereo(mix, chime(0.25, 1760.0), 32.7, gain=0.24)          # Walkie-talkie beep
    _add_stereo(mix, hydraulic_hum(3.2), 34.0, gain=0.36)           # 3 giant mirrors rotating
    _add_stereo(mix, whoosh(1.1, 300, 1400), 36.2, gain=0.36)       # Tracking volumetric beam down
    _add_stereo(mix, light_boom(1.8), 39.6, gain=0.48)              # Golden sunlight slams into square!
    _add_stereo(mix, chime(0.65, 1568.0), 48.35, gain=0.34)         # Sunglasses glint match-cut
    _add_stereo(mix, whoosh(0.60, 380, 2200), 48.55, gain=0.45)     # Transition 2 -> 3
    _add_stereo(mix, espresso_hiss(2.6), 53.0, gain=0.28, pan=-0.2) # Café espresso steam
    _add_stereo(mix, whoosh(0.32, 420, 1900), 62.0, gain=0.30)      # Fast whip-pan to dual-flag door
    _add_stereo(mix, whoosh(0.32, 420, 1900), 66.2, gain=0.30)      # Whip-pan back to Clara
    _add_stereo(mix, spoon_clink(0.45), 73.7, gain=0.45)            # Final coffee spoon clink
    _add_stereo(mix, glitch_burst(0.25), 74.55, gain=0.42)          # Finger snap loop glitch!

    # 3. LIGHT UPBEAT ADVENTURE UNDERSCORE (BPM 124, stops sharply at 74.65s!)
    bpm = 124.0
    beat_sec = 60.0 / bpm
    bass_notes = [130.81, 130.81, 164.81, 146.83, 174.61, 174.61, 196.00, 164.81]  # C3 E3 D3 F3 G3
    pluck_notes = [523.25, 659.25, 783.99, 659.25, 587.33, 698.46, 783.99, 880.00]
    cur_t = 0.45
    step = 0
    while cur_t < 74.45:
        # Soft kick on beats 0, 2
        if step % 2 == 0:
            kn = int(0.14 * SR)
            kt = np.arange(kn, dtype=np.float32) / float(SR)
            kick = np.sin(2 * math.pi * (115.0 * np.exp(-kt * 24.0) + 46.0) * kt) * np.exp(-kt * 16.0)
            _add_stereo(mix, kick, cur_t, gain=0.14)
        # Warm muted pluck bass
        bn = int(0.26 * SR)
        bt = np.arange(bn, dtype=np.float32) / float(SR)
        bf = bass_notes[(step // 2) % len(bass_notes)]
        # Shift mood slightly warmer in Baarle (brighter triad) and darker in Rjukan dark noon (25-39s)
        if 25.0 <= cur_t < 39.5:
            bf *= 0.8909  # minor shade shift
        bass = (np.sin(2 * math.pi * bf * bt) + 0.3 * np.sin(2 * math.pi * bf * 2 * bt)) * np.exp(-bt * 7.5)
        _add_stereo(mix, bass, cur_t, gain=0.075)
        # Crisp marimba/kalimba travel pluck on upbeat 8ths
        if step % 2 == 1:
            pn = int(0.18 * SR)
            pt = np.arange(pn, dtype=np.float32) / float(SR)
            pf = pluck_notes[step % len(pluck_notes)]
            if 25.0 <= cur_t < 39.5:
                pf *= 0.9438
            pluck = np.sin(2 * math.pi * pf * pt) * np.exp(-pt * 14.0)
            _add_stereo(mix, pluck, cur_t, gain=0.045, pan=0.22 if step % 4 == 1 else -0.22)
        cur_t += beat_sec * 0.5
        step += 1

    # Sharp beat drop cut at 74.65s
    cut_i = int(74.68 * SR)
    fade_n = int(0.06 * SR)
    if cut_i + fade_n < total_samples:
        mix[cut_i : cut_i + fade_n] *= np.linspace(1.0, 0.0, fade_n, dtype=np.float32)[:, None]
        mix[cut_i + fade_n :] *= 0.2  # leave only final glitch/clink tail

    return mix


def compute_lipsync_from_array(mono: np.ndarray, fps: int = FPS, total_frames: int = TOTAL_FRAMES) -> List[float]:
    step = max(1, int(round(SR / float(fps))))
    rms_vals: List[float] = []
    for f in range(total_frames):
        s0 = f * step
        s1 = min(len(mono), s0 + step)
        if s0 >= len(mono) or s1 <= s0:
            rms_vals.append(0.0)
            continue
        chunk = mono[s0:s1]
        rms_vals.append(float(np.sqrt(np.mean(chunk * chunk))))
    peak = max(rms_vals) if rms_vals else 1.0
    div = max(peak, 0.06)
    curve: List[float] = []
    prev = 0.0
    for r in rms_vals:
        tgt = max(0.0, min(1.0, (r / div) * 2.2))
        if tgt < 0.09:
            tgt = 0.0
        cur = prev * 0.32 + tgt * 0.68
        curve.append(round(cur, 4))
        prev = cur
    return curve


def main(tts_only: bool = False) -> None:
    stems_dir = os.path.join(AUDIO_DIR, "stems")
    mp3_paths = asyncio.run(generate_all_tts_mp3(stems_dir))

    if tts_only or not shutil.which("ffmpeg"):
        print("[Audio] TTS MP3 stems ready in:", stems_dir)
        if not shutil.which("ffmpeg"):
            print("[Audio] FFmpeg not found locally; full WAV mix & lip-sync will run automatically on GitHub Actions.")
        return

    total_samples = int(round(DURATION_SEC * SR))
    master_mix = synth_sfx_and_music(total_samples)

    # Per-speaker dry mono track for 100% accurate lip-sync
    speakers = sorted({l["speaker"] for l in DIALOGUE_LINES})
    speaker_tracks: Dict[str, np.ndarray] = {sp: np.zeros(total_samples, dtype=np.float32) for sp in speakers}
    timing_report: List[Dict[str, Any]] = []

    for line in DIALOGUE_LINES:
        max_dur = max(0.5, line["max_end_sec"] - line["start_sec"])
        wav_tmp = os.path.join(stems_dir, f"{line['id']}.wav")
        samples = time_stretch_ffmpeg(mp3_paths[line["id"]], wav_tmp, max_dur=max_dur, radio_fx=bool(line.get("radio_fx")))
        dur = len(samples) / float(SR)
        s0 = int(round(line["start_sec"] * SR))
        n = min(len(samples), total_samples - s0)
        if n > 0:
            speaker_tracks[line["speaker"]][s0 : s0 + n] += samples[:n]
            # Slight stereo ducking of music/SFX during speech
            master_mix[s0 : s0 + n] *= 0.62
            _add_stereo(master_mix, samples[:n], line["start_sec"], gain=0.95, pan=0.0)
        timing_report.append({
            "id": line["id"],
            "speaker": line["speaker"],
            "start_sec": line["start_sec"],
            "end_sec": round(line["start_sec"] + dur, 3),
            "max_end_sec": line["max_end_sec"],
            "duration_sec": round(dur, 3),
        })
        print(f"[Mix] {line['id']:24s} {line['start_sec']:5.2f}s -> {line['start_sec']+dur:5.2f}s (budget {line['max_end_sec']:5.2f}s)")

    # Master limiter
    pk = float(np.max(np.abs(master_mix)))
    if pk > 0.94:
        master_mix *= 0.94 / pk

    master_wav = os.path.join(AUDIO_DIR, "master_audio.wav")
    write_wav_stereo(master_wav, master_mix, SR)
    print(f"[Audio] Wrote master_audio.wav ({DURATION_SEC}s @ {SR}Hz stereo)")

    # Lip-sync curves per character
    lipsync_data = {
        "fps": FPS,
        "total_frames": TOTAL_FRAMES,
        "timings": timing_report,
        "curves": {sp: compute_lipsync_from_array(tr, FPS, TOTAL_FRAMES) for sp, tr in speaker_tracks.items()},
    }
    ls_path = os.path.join(AUDIO_DIR, "lipsync_curves.json")
    with open(ls_path, "w", encoding="utf-8") as fh:
        json.dump(lipsync_data, fh)
    print(f"[Audio] Wrote lipsync_curves.json ({len(speakers)} speakers, {TOTAL_FRAMES} frames)")


if __name__ == "__main__":
    main(tts_only="--tts-only" in sys.argv)
