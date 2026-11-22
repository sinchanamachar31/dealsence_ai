import asyncio
import os
import re
import subprocess
import tempfile
from pathlib import Path

import edge_tts
import imageio_ffmpeg

from backend.scripts.demo_data import DEMO_CREATORS


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REEL_DIR = PROJECT_ROOT / "backend" / "static" / "media" / "reels"
VOICE_PROFILES = {
    "@ananya.nourish": {
        "voice": "en-IN-NeerjaNeural",
        "rate": "+4%",
        "pitch": "+2Hz",
    },
    "@meera.glowlab": {
        "voice": "en-IN-NeerjaNeural",
        "rate": "+6%",
        "pitch": "+6Hz",
    },
    "@rohan.movewell": {
        "voice": "en-IN-PrabhatNeural",
        "rate": "+5%",
        "pitch": "+0Hz",
    },
    "@kabir.desksetup": {
        "voice": "en-IN-PrabhatNeural",
        "rate": "+8%",
        "pitch": "+3Hz",
    },
    "@tara.earthhome": {
        "voice": "en-US-AriaNeural",
        "rate": "-2%",
        "pitch": "+0Hz",
    },
}


def _spoken_script(caption):
    clean_caption = re.sub(r"#\S+", "", caption)
    clean_caption = " ".join(clean_caption.split())
    return f"Hey everyone! {clean_caption}"


async def add_voiceovers():
    video_items = [
        (creator, content)
        for creator in DEMO_CREATORS
        for content in creator["contents"]
        if content.get("video_path") is not None
    ]
    if len(video_items) != 35:
        raise ValueError(f"Expected 35 reel/video items; found {len(video_items)}.")

    REEL_DIR.mkdir(parents=True, exist_ok=True)
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    voiced_count = 0

    for index, (creator, content) in enumerate(video_items, start=1):
        handle = creator["handle"]
        if handle not in VOICE_PROFILES:
            raise ValueError(f"No voice profile configured for {handle}.")

        slug = content["content_slug"]
        mp4_path = REEL_DIR / f"{slug}.mp4"
        profile = VOICE_PROFILES[handle]
        script = _spoken_script(content["caption"])
        print(f"[{index}/35] {handle} - {slug}", flush=True)

        mp3_fd, temp_mp3 = tempfile.mkstemp(
            prefix=f"{slug}_",
            suffix=".mp3",
            dir=REEL_DIR,
        )
        os.close(mp3_fd)
        mp4_fd, temp_mp4 = tempfile.mkstemp(
            prefix=f"{slug}_",
            suffix=".mp4",
            dir=REEL_DIR,
        )
        os.close(mp4_fd)

        try:
            await edge_tts.Communicate(
                script,
                voice=profile["voice"],
                rate=profile["rate"],
                pitch=profile["pitch"],
            ).save(temp_mp3)
            if os.path.getsize(temp_mp3) <= 1000:
                raise RuntimeError(
                    f"Generated voiceover is too small to mux for {slug}."
                )
            subprocess.run(
                [
                    ffmpeg_exe,
                    "-y",
                    "-i",
                    str(mp4_path),
                    "-i",
                    temp_mp3,
                    "-map",
                    "0:v:0",
                    "-map",
                    "1:a:0",
                    "-c:v",
                    "copy",
                    "-af",
                    "apad",
                    "-c:a",
                    "aac",
                    "-profile:a",
                    "aac_low",
                    "-b:a",
                    "128k",
                    "-ar",
                    "44100",
                    "-ac",
                    "2",
                    "-shortest",
                    "-movflags",
                    "+faststart",
                    temp_mp4,
                ],
                check=True,
            )
            os.replace(temp_mp4, mp4_path)
            voiced_count += 1
        finally:
            if os.path.exists(temp_mp3):
                os.remove(temp_mp3)
            if os.path.exists(temp_mp4):
                os.remove(temp_mp4)

    print(f"Voiced reels/videos: {voiced_count}/35")


if __name__ == "__main__":
    asyncio.run(add_voiceovers())
