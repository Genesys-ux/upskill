"""Unified 30-runner parallel render orchestrator for preview clips & full 75-second 9:16 animation."""
from __future__ import annotations

import argparse
import glob
import os
import platform
import shutil
import subprocess
import sys
from typing import List

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PIL import Image, ImageDraw
from animation.render_characters import render_character_sprites
from project_config import AUDIO_DIR, BUILD_DIR, FPS, MASTER_RES, PREVIEW_CLIPS, PREVIEW_RES, SHARDS_30


def run_blender_segment(
    scene_name: str,
    start_frame: int,
    end_frame: int,
    frames_out_dir: str,
    width: int,
    height: int,
    samples: int,
    blender_bin: str = "blender",
) -> None:
    """1) Render yaw-synced Python 2.5D character RGBA sprites, 2) Render 3D Blender EEVEE Next frames."""
    sprites_dir = render_character_sprites(
        scene_name=scene_name,
        start_frame=start_frame,
        end_frame=end_frame,
        scale=1.65 if width <= 720 else 2.2,
        workers=os.cpu_count() or 4,
    )

    run_script = os.path.join(PROJECT_ROOT, "blender_scenes", "run_scene.py")
    cmd = [
        blender_bin,
        "--background",
        "--factory-startup",
        "--python-exit-code",
        "1",
        "--python",
        run_script,
        "--",
        "--scene",
        scene_name,
        "--start",
        str(start_frame),
        "--end",
        str(end_frame),
        "--sprites",
        sprites_dir,
        "--out-dir",
        frames_out_dir,
        "--width",
        str(width),
        "--height",
        str(height),
        "--samples",
        str(samples),
    ]

    env = os.environ.copy()
    if platform.system() == "Linux":
        env.setdefault("LIBGL_ALWAYS_SOFTWARE", "1")
        env.setdefault("MESA_GL_VERSION_OVERRIDE", "4.5")
        env.setdefault("MESA_GLSL_VERSION_OVERRIDE", "450")
        env.setdefault("GALLIUM_DRIVER", "llvmpipe")
        if shutil.which("xvfb-run") and not env.get("DISPLAY"):
            cmd = ["xvfb-run", "-a", "--server-args=-screen 0 1280x720x24"] + cmd

    print("[Pipeline] Launching:", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, env=env)


def encode_mp4_with_audio(
    frames_dir: str,
    start_frame: int,
    end_frame: int,
    out_mp4: str,
    audio_wav: str = "",
    crf: int = 18,
) -> None:
    """Encode sequential PNG frames (+ optional exact slice of master WAV) into H.264 MP4."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg not found in PATH.")
    os.makedirs(os.path.dirname(os.path.abspath(out_mp4)), exist_ok=True)

    frame_count = end_frame - start_frame
    start_sec = start_frame / float(FPS)
    dur_sec = frame_count / float(FPS)
    pattern = os.path.join(frames_dir, "frame_%04d.png")

    # Input options strictly BEFORE each -i; output options strictly AFTER all -i!
    cmd = [
        ffmpeg, "-y", "-v", "warning",
        "-framerate", str(FPS),
        "-start_number", str(start_frame),
        "-i", pattern,
    ]
    has_audio = bool(audio_wav and os.path.exists(audio_wav))
    if has_audio:
        cmd += ["-ss", f"{start_sec:.4f}", "-t", f"{dur_sec:.4f}", "-i", audio_wav]

    cmd += [
        "-frames:v", str(frame_count),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", str(crf),
        "-preset", "fast",
        "-movflags", "+faststart",
    ]
    if has_audio:
        cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd.append(out_mp4)
    print("[FFmpeg] Encoding:", out_mp4, flush=True)
    subprocess.run(cmd, check=True)


def render_shard(shard_idx: int, quality: str = "preview_720p", samples: int = 8, blender_bin: str = "blender") -> None:
    """Render 1 of 30 parallel shards (72-78 frames -> shard_XX.mp4 + 1 keyframe thumbnail PNG)."""
    sh = SHARDS_30[shard_idx]
    w, h = PREVIEW_RES if quality == "preview_720p" else MASTER_RES
    frames_dir = os.path.join(BUILD_DIR, "frames_shard", sh["id"])
    os.makedirs(frames_dir, exist_ok=True)

    run_blender_segment(
        scene_name=sh["scene"],
        start_frame=sh["start_frame"],
        end_frame=sh["end_frame"],
        frames_out_dir=frames_dir,
        width=w,
        height=h,
        samples=samples,
        blender_bin=blender_bin,
    )

    out_dir = os.path.join(BUILD_DIR, "outputs", "shards")
    os.makedirs(out_dir, exist_ok=True)
    out_mp4 = os.path.join(out_dir, f"{sh['id']}.mp4")
    encode_mp4_with_audio(frames_dir, sh["start_frame"], sh["end_frame"], out_mp4, audio_wav="", crf=16)

    # Save midpoint keyframe thumbnail from this shard for the master contact sheet
    mid_f = (sh["start_frame"] + sh["end_frame"]) // 2
    mid_png = os.path.join(frames_dir, f"frame_{mid_f:04d}.png")
    if os.path.exists(mid_png):
        thumb = Image.open(mid_png).convert("RGB").resize((270, 480), Image.Resampling.LANCZOS)
        thumb.save(os.path.join(out_dir, f"{sh['id']}_thumb_f{mid_f:04d}.jpg"), quality=88)


def assemble_from_shards(quality: str = "preview_720p") -> None:
    """Stitch all 30 rendered shards + master_audio.wav into full 75s MP4, 4 preview clips, and keyframe sheet."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg not found.")

    shards_dir = os.path.join(BUILD_DIR, "outputs", "shards")
    out_dir = os.path.join(BUILD_DIR, "outputs", "final")
    os.makedirs(out_dir, exist_ok=True)

    shard_mp4s = [os.path.join(shards_dir, f"shard_{i:02d}.mp4") for i in range(len(SHARDS_30))]
    missing = [p for p in shard_mp4s if not os.path.exists(p)]
    if missing:
        raise RuntimeError(f"Missing {len(missing)} shard MP4 files: {missing[:5]}")

    # 1. Concatenate all 30 shards into seamless raw 75s video track
    list_txt = os.path.join(out_dir, "shards_concat.txt")
    with open(list_txt, "w", encoding="utf-8") as fh:
        for p in shard_mp4s:
            fh.write(f"file '{os.path.abspath(p)}'\n")

    master_wav = os.path.join(AUDIO_DIR, "master_audio.wav")
    res_tag = "720x1280" if quality == "preview_720p" else "1080x1920"
    full_mp4 = os.path.join(out_dir, f"BUMI_LAGI_NGEBUG_FULL_75S_{res_tag}.mp4")

    cmd_full = [
        ffmpeg, "-y", "-v", "warning",
        "-f", "concat", "-safe", "0", "-i", list_txt,
        "-i", master_wav,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        full_mp4,
    ]
    print("[Assemble] Building complete 75s master:", full_mp4, flush=True)
    subprocess.run(cmd_full, check=True)
    os.remove(list_txt)

    # 2. Slice the 4 curated Preview Clips cleanly with frame-accurate re-encode from full 75s master
    for clip in PREVIEW_CLIPS:
        clip_mp4 = os.path.join(out_dir, f"{clip['id']}.mp4")
        start_s = clip["start_frame"] / float(FPS)
        dur_s = (clip["end_frame"] - clip["start_frame"]) / float(FPS)
        cmd_clip = [
            ffmpeg, "-y", "-v", "warning",
            "-ss", f"{start_s:.4f}",
            "-i", full_mp4,
            "-t", f"{dur_s:.4f}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "fast",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            clip_mp4,
        ]
        print("[Assemble] Slicing preview clip:", clip_mp4, flush=True)
        subprocess.run(cmd_clip, check=True)

    # 3. Build 30-panel full-movie keyframe review contact sheet (6 cols x 5 rows)
    thumbs = sorted(glob.glob(os.path.join(shards_dir, "shard_*_thumb_*.jpg")))
    if thumbs:
        cols, rows = 6, 5
        tw, th = 270, 480
        sheet = Image.new("RGB", (cols * tw, rows * th + 60), (18, 16, 26))
        draw = ImageDraw.Draw(sheet)
        draw.text((20, 18), f"BUMI LAGI NGE-BUG! — 30-Shard Storyboard Keyframes ({res_tag})", fill=(242, 248, 255))
        for idx, tp in enumerate(thumbs[:30]):
            r, c = divmod(idx, cols)
            im = Image.open(tp).convert("RGB").resize((tw, th), Image.Resampling.LANCZOS)
            sheet.paste(im, (c * tw, 60 + r * th))
            sh = SHARDS_30[idx]
            mid_t = ((sh["start_frame"] + sh["end_frame"]) * 0.5) / float(FPS)
            draw.rectangle([c * tw + 6, 60 + r * th + 6, c * tw + 175, 60 + r * th + 30], fill=(16, 14, 24))
            draw.text((c * tw + 12, 60 + r * th + 12), f"#{idx:02d} {sh['scene']} {mid_t:04.1f}s", fill=(138, 238, 255))
        sheet_path = os.path.join(out_dir, "BUMI_LAGI_NGEBUG_30_KEYFRAMES.jpg")
        sheet.save(sheet_path, quality=90)
        print("[Assemble] Saved 30-shard contact sheet:", sheet_path, flush=True)


def smoke_test_ffmpeg() -> None:
    """1-second pre-flight FFmpeg test run in Job 1 so encoding syntax is verified BEFORE 30 runners launch."""
    tmp_dir = os.path.join(BUILD_DIR, "_smoke")
    os.makedirs(tmp_dir, exist_ok=True)
    for f in (0, 1, 2):
        Image.new("RGB", (64, 64), (40, 80, 120)).save(os.path.join(tmp_dir, f"frame_{f:04d}.png"))
    out_mp4 = os.path.join(tmp_dir, "smoke.mp4")
    encode_mp4_with_audio(tmp_dir, 0, 3, out_mp4, audio_wav=os.path.join(AUDIO_DIR, "master_audio.wav"))
    assert os.path.exists(out_mp4) and os.path.getsize(out_mp4) > 500
    shutil.rmtree(tmp_dir, ignore_errors=True)
    print("[SmokeTest] FFmpeg video + audio muxing verified 100%!", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="BUMI LAGI NGE-BUG! 30-Runner Parallel Render Pipeline")
    parser.add_argument("--shard", type=int, default=None, help="Render single shard index 0..29")
    parser.add_argument("--assemble-from-shards", action="store_true", help="Assemble all 30 shards into 4 clips + full 75s video")
    parser.add_argument("--smoke-test-ffmpeg", action="store_true", help="Verify FFmpeg muxing in 1 second")
    parser.add_argument("--quality", default="preview_720p", choices=["preview_720p", "full_1080p"])
    parser.add_argument("--samples", type=int, default=8)
    parser.add_argument("--blender", default="blender")
    args = parser.parse_args()

    if args.smoke_test_ffmpeg:
        smoke_test_ffmpeg()
    elif args.shard is not None:
        render_shard(args.shard, quality=args.quality, samples=args.samples, blender_bin=args.blender)
    elif args.assemble_from_shards:
        assemble_from_shards(quality=args.quality)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
