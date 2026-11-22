import os
import subprocess
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(dotenv_path):
        dotenv_path = Path(dotenv_path)
        if not dotenv_path.is_file():
            return False

        with dotenv_path.open(encoding="utf-8") as env_file:
            for line in env_file:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                if line.startswith("export "):
                    line = line[len("export "):].lstrip()
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                if (
                    len(value) >= 2
                    and value[0] == value[-1]
                    and value[0] in ("'", '"')
                ):
                    value = value[1:-1]
                if key:
                    os.environ.setdefault(key, value)
        return True

from backend.scripts.demo_data import DEMO_CREATORS


PROJECT_ROOT = Path(__file__).resolve().parents[2]
THUMBNAIL_DIR = PROJECT_ROOT / "backend" / "static" / "media" / "thumbnails"
REEL_DIR = PROJECT_ROOT / "backend" / "static" / "media" / "reels"
THUMBNAIL_MIN_SIZE = 2000
VIDEO_MIN_SIZE = 5000
MAX_RETRIES = 3

load_dotenv(dotenv_path=PROJECT_ROOT / ".env")
POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY", "").strip()


def _request_thumbnail(prompt, seed, output_path):
    if not POLLINATIONS_API_KEY:
        raise RuntimeError(
            "POLLINATIONS_API_KEY is missing from the environment or project-root .env."
        )

    encoded_prompt = quote(prompt, safe="")
    url = (
        f"https://gen.pollinations.ai/image/{encoded_prompt}"
        f"?model=flux&width=720&height=1280&nologo=true&seed={seed}"
    )
    request = Request(
        url,
        headers={
            "Authorization": f"Bearer {POLLINATIONS_API_KEY}",
            "User-Agent": "DealSenseSim/1.0",
        },
    )

    for attempt in range(MAX_RETRIES + 1):
        try:
            with urlopen(request, timeout=120) as response:
                image_bytes = response.read()
            with output_path.open("wb") as image_file:
                image_file.write(image_bytes)
            return
        except HTTPError as error:
            if error.code != 429 and not 500 <= error.code < 600:
                raise
            if attempt == MAX_RETRIES:
                raise
            error.close()
            time.sleep(attempt + 1)


def _generate_video(thumbnail_path, video_path):
    try:
        import imageio_ffmpeg
    except ImportError as error:
        raise RuntimeError(
            "imageio-ffmpeg is required to generate reel and video files."
        ) from error

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    zoom_filter = (
        "scale=1080:1920,"
        "zoompan=z='min(zoom+0.00018,1.16)':d=900:"
        "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        "s=720x1280:fps=30"
    )
    command = [
        ffmpeg_exe,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(thumbnail_path),
        "-f",
        "lavfi",
        "-i",
        "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-vf",
        zoom_filter,
        "-frames:v",
        "900",
        "-t",
        "30",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-shortest",
        "-movflags",
        "+faststart",
        str(video_path),
    ]
    subprocess.run(command, check=True)


def generate_all_media():
    content_items = [
        (creator, content)
        for creator in DEMO_CREATORS
        for content in creator["contents"]
    ]
    video_items = [
        (creator, content)
        for creator, content in content_items
        if content.get("video_path") is not None
    ]
    if len(content_items) != 50:
        raise ValueError(f"Expected 50 demo content items; found {len(content_items)}.")
    if len(video_items) != 35:
        raise ValueError(f"Expected 35 reel/video items; found {len(video_items)}.")

    THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)
    REEL_DIR.mkdir(parents=True, exist_ok=True)
    video_slugs = {
        content["content_slug"]
        for _, content in video_items
    }

    for idx, (creator, content) in enumerate(content_items, start=1):
        slug = content["content_slug"]
        thumbnail_path = THUMBNAIL_DIR / f"{slug}.jpg"
        video_path = REEL_DIR / f"{slug}.mp4"
        print(f"[{idx}/50] {creator['handle']} - {slug}", flush=True)

        if (
            thumbnail_path.is_file()
            and thumbnail_path.stat().st_size > THUMBNAIL_MIN_SIZE
        ):
            print(f"  Skipping existing thumbnail: {thumbnail_path}", flush=True)
        else:
            prompt = (
                f"Photorealistic vertical 9:16 lifestyle photograph for "
                f"{creator['niche']}: {content['caption']}. Natural lighting, "
                "sharp focus, clean aesthetic, no text overlay"
            )
            _request_thumbnail(prompt, idx, thumbnail_path)
            print(f"  Generated thumbnail: {thumbnail_path}", flush=True)

        if slug not in video_slugs:
            continue
        if video_path.is_file() and video_path.stat().st_size > VIDEO_MIN_SIZE:
            print(f"  Skipping existing video: {video_path}", flush=True)
            continue

        _generate_video(thumbnail_path, video_path)
        print(f"  Generated video: {video_path}", flush=True)

    real_thumbnail_count = sum(
        1
        for _, content in content_items
        if (
            (THUMBNAIL_DIR / f"{content['content_slug']}.jpg").is_file()
            and (THUMBNAIL_DIR / f"{content['content_slug']}.jpg").stat().st_size
            > THUMBNAIL_MIN_SIZE
        )
    )
    real_video_count = sum(
        1
        for _, content in video_items
        if (
            (REEL_DIR / f"{content['content_slug']}.mp4").is_file()
            and (REEL_DIR / f"{content['content_slug']}.mp4").stat().st_size
            > VIDEO_MIN_SIZE
        )
    )
    print(
        f"Summary: real thumbnails {real_thumbnail_count}/50; "
        f"real reels/videos {real_video_count}/35"
    )


if __name__ == "__main__":
    generate_all_media()
