"""Unified render orchestrator for preview clips & full 75-second 9:16 animation (GitHub Actions / Local)."""
from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from typing import Any, Dict, List

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PIL import Image, ImageDraw
from animation.render_characters import render_character_sprites
from project_config import AUDIO_DIR, BUILD_DIR, FPS, FULL_CHUNKS, MASTER_RES, PREVIEW_CLIPS, PREVIEW_RES


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
        scale=2.0 if width <= 720 else 2.5,
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


def make_contact_sheet(frames_dir: str, start_frame: int, end_frame: int, out_png: str, title: str) -> None:
    """Generate a 6-panel keyframe review sheet from rendered frames."""
    count = max(1, end_frame - start_frame)
    picks = [start_frame + int(round(i * (count - 1) / 5.0)) for i in range(6)]
    imgs = []
    for f in picks:
        p = os.path.join(frames_dir, f"frame_{f:04d}.png")
        if os.path.exists(p):
            imgs.append((f, Image.open(p).convert("RGB")))
    if not imgs:
        return
    tw, th = 360, 640
    sheet = Image.new("RGB", (tw * len(imgs), th + 54), (20, 18, 28))
    draw = ImageDraw.Draw(sheet)
    draw.text((16, 16), title, fill=(240, 246, 255))
    for i, (f, im) in enumerate(imgs):
        im_r = im.resize((tw, th), Image.Resampling.LANCZOS)
        sheet.paste(im_r, (i * tw, 54))
        draw.rectangle([i * tw + 8, 62, i * tw + 135, 90], fill=(16, 14, 24))
        draw.text((i * tw + 16, 69), f"t={f / FPS:05.2f}s (f{f})", fill=(130, 238, 255))
    os.makedirs(os.path.dirname(os.path.abspath(out_png)), exist_ok=True)
    sheet.save(out_png, quality=92)
    print(f"[Pipeline] Saved keyframe contact sheet: {out_png}")


def encode_mp4_with_audio(
    frames_dir: str,
    start_frame: int,
    end_frame: int,
    out_mp4: str,
    audio_wav: str,
) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg not found in PATH.")
    os.makedirs(os.path.dirname(os.path.abspath(out_mp4)), exist_ok=True)

    start_sec = start_frame / float(FPS)
    dur_sec = (end_frame - start_frame) / float(FPS)
    pattern = os.path.join(frames_dir, "frame_%04d.png")

    cmd = [
        ffmpeg, "-y", "-v", "warning",
        "-framerate", str(FPS),
        "-start_number", str(start_frame),
        "-i", pattern,
        "-frames:v", str(end_frame - start_frame),
    ]
    if audio_wav and os.path.exists(audio_wav):
        cmd += ["-ss", f"{start_sec:.4f}", "-t", f"{dur_sec:.4f}", "-i", audio_wav]

    cmd += [
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        "-preset", "medium",
        "-movflags", "+faststart",
    ]
    if audio_wav and os.path.exists(audio_wav):
        cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd.append(out_mp4)
    print("[FFmpeg] Encoding:", out_mp4, flush=True)
    subprocess.run(cmd, check=True)


def render_clip(clip_id: str, samples: int = 20, blender_bin: str = "blender") -> None:
    clip = next((c for c in PREVIEW_CLIPS if c["id"] == clip_id), None)
    if not clip:
        raise ValueError(f"Unknown clip_id: {clip_id}")

    w, h = PREVIEW_RES
    frames_dir = os.path.join(BUILD_DIR, "frames", clip_id)
    os.makedirs(frames_dir, exist_ok=True)

    segments = clip.get("segments") or [
        {"scene": clip["scene"], "start_frame": clip["start_frame"], "end_frame": clip["end_frame"]}
    ]
    for seg in segments:
        run_blender_segment(
            scene_name=seg["scene"],
            start_frame=seg["start_frame"],
            end_frame=seg["end_frame"],
            frames_out_dir=frames_dir,
            width=w,
            height=h,
            samples=samples,
            blender_bin=blender_bin,
        )

    out_dir = os.path.join(BUILD_DIR, "outputs", "previews")
    os.makedirs(out_dir, exist_ok=True)
    out_mp4 = os.path.join(out_dir, f"{clip_id}.mp4")
    out_sheet = os.path.join(out_dir, f"{clip_id}_keyframes.png")
    master_wav = os.path.join(AUDIO_DIR, "master_audio.wav")

    encode_mp4_with_audio(frames_dir, clip["start_frame"], clip["end_frame"], out_mp4, master_wav)
    make_contact_sheet(frames_dir, clip["start_frame"], clip["end_frame"], out_sheet, clip["title"])


def render_full_part(part_id: str, samples: int = 24, blender_bin: str = "blender") -> None:
    part = next((p for p in FULL_CHUNKS if p["id"] == part_id), None)
    if not part:
        raise ValueError(f"Unknown part_id: {part_id}")

    w, h = MASTER_RES
    frames_dir = os.path.join(BUILD_DIR, "frames_full", part_id)
    os.makedirs(frames_dir, exist_ok=True)
    run_blender_segment(
        scene_name=part["scene"],
        start_frame=part["start_frame"],
        end_frame=part["end_frame"],
        frames_out_dir=frames_dir,
        width=w,
        height=h,
        samples=samples,
        blender_bin=blender_bin,
    )
    out_dir = os.path.join(BUILD_DIR, "outputs", "full_parts")
    os.makedirs(out_dir, exist_ok=True)
    out_mp4 = os.path.join(out_dir, f"{part_id}.mp4")
    encode_mp4_with_audio(frames_dir, part["start_frame"], part["end_frame"], out_mp4, "")


def concat_videos(mp4_list: List[str], out_mp4: str, master_audio: str = "") -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg not found.")
    os.makedirs(os.path.dirname(os.path.abspath(out_mp4)), exist_ok=True)
    list_txt = out_mp4 + ".concat.txt"
    with open(list_txt, "w", encoding="utf-8") as fh:
        for p in mp4_list:
            fh.write(f"file '{os.path.abspath(p)}'\n")
    cmd = [ffmpeg, "-y", "-v", "warning", "-f", "concat", "-safe", "0", "-i", list_txt]
    if master_audio and os.path.exists(master_audio):
        cmd += ["-i", master_audio, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out_mp4]
    else:
        cmd += ["-c", "copy", "-movflags", "+faststart", out_mp4]
    subprocess.run(cmd, check=True)
    os.remove(list_txt)
    print(f"[Pipeline] Assembled: {out_mp4}")


def main() -> None:
    parser = argparse.ArgumentParser(description="BUMI LAGI NGE-BUG! 3D Animation Render Pipeline")
    parser.add_argument("--clip", help="Render one preview clip by id")
    parser.add_argument("--part", help="Render one full-HD 75s chunk by id")
    parser.add_argument("--assemble-previews", action="store_true", help="Combine all 4 preview clips into one showcase reel")
    parser.add_argument("--assemble-full", action="store_true", help="Combine all 6 Full-HD chunks + master audio into 75s MP4")
    parser.add_argument("--samples", type=int, default=20)
    parser.add_argument("--blender", default="blender")
    args = parser.parse_args()

    if args.clip:
        render_clip(args.clip, samples=args.samples, blender_bin=args.blender)
    elif args.part:
        render_full_part(args.part, samples=args.samples, blender_bin=args.blender)
    elif args.assemble_previews:
        prev_dir = os.path.join(BUILD_DIR, "outputs", "previews")
        clips = [os.path.join(prev_dir, f"{c['id']}.mp4") for c in PREVIEW_CLIPS if os.path.exists(os.path.join(prev_dir, f"{c['id']}.mp4"))]
        if clips:
            concat_videos(clips, os.path.join(prev_dir, "BUMI_LAGI_NGEBUG_PREVIEW_REEL.mp4"))
    elif args.assemble_full:
        parts_dir = os.path.join(BUILD_DIR, "outputs", "full_parts")
        parts = [os.path.join(parts_dir, f"{p['id']}.mp4") for p in FULL_CHUNKS]
        out_master = os.path.join(BUILD_DIR, "outputs", "BUMI_LAGI_NGEBUG_FULL_75S_1080x1920.mp4")
        concat_videos(parts, out_master, master_audio=os.path.join(AUDIO_DIR, "master_audio.wav"))


if __name__ == "__main__":
    main()
