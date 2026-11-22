import argparse
import asyncio
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request

import edge_tts
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from backend.scripts.demo_data import DEMO_CREATORS
from backend.scripts.reel_storyboards import build_reel_storyboard


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = PROJECT_ROOT / "backend" / "static" / "media"
REEL_DIR = STATIC_DIR / "reels"
CUSTOM_CLIP_DIR = STATIC_DIR / "custom_clips"
SCENE_FRAME_DIR = STATIC_DIR / "scene_frames"
IMAGE_SIZE = (720, 1280)
FRAMES_PER_SCENE = 150
TOTAL_SCENES = 6
TOTAL_FRAMES = FRAMES_PER_SCENE * TOTAL_SCENES

VOICE_PROFILES = {
    "@ananya.nourish": {
        "voice": "en-IN-NeerjaNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
    },
    "@meera.glowlab": {
        "voice": "en-IN-NeerjaNeural",
        "rate": "-2%",
        "pitch": "+0Hz",
    },
    "@rohan.movewell": {
        "voice": "en-IN-PrabhatNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
    },
    "@kabir.desksetup": {
        "voice": "en-IN-PrabhatNeural",
        "rate": "-2%",
        "pitch": "+0Hz",
    },
    "@tara.earthhome": {
        "voice": "en-IN-NeerjaNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
    },
}

NICHE_COLORS = {
    "Healthy Food & Nutrition": ((8, 24, 23), (20, 54, 43), (158, 194, 105)),
    "Clean Skincare & Beauty": ((20, 24, 35), (43, 53, 61), (224, 159, 151)),
    "Home Fitness & Strength": ((11, 24, 36), (24, 51, 65), (226, 159, 83)),
    "Tech & Student Productivity": ((12, 17, 35), (28, 37, 69), (103, 199, 205)),
    "Sustainable Home & Decor": ((24, 27, 22), (48, 47, 35), (201, 175, 113)),
}


def _interpolate_color(start, end, amount):
    return tuple(
        round(start[channel] + (end[channel] - start[channel]) * amount)
        for channel in range(3)
    )


def _wrap_text(draw, text, font, max_width):
    lines = []
    current_line = ""
    for word in text.split():
        candidate = f"{current_line} {word}".strip()
        if current_line and draw.textbbox((0, 0), candidate, font=font)[2] > max_width:
            lines.append(current_line)
            current_line = word
        else:
            current_line = candidate
    if current_line:
        lines.append(current_line)
    return lines


def _draw_wrapped_text(draw, text, position, font, fill, max_width, line_gap=12):
    x, y = position
    for line in _wrap_text(draw, text, font, max_width):
        draw.text((x, y), line, font=font, fill=fill)
        y += draw.textbbox((x, y), line, font=font)[3] + line_gap
    return y


def _load_font(size):
    for font_path in (
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ):
        try:
            return ImageFont.truetype(font_path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _fallback_image(creator, content, scene_prompt, scene_index):
    top_color, bottom_color, accent = NICHE_COLORS.get(
        creator["niche"],
        ((10, 21, 28), (32, 46, 55), (173, 184, 155)),
    )
    image = Image.new("RGB", IMAGE_SIZE)
    draw = ImageDraw.Draw(image)
    for y in range(IMAGE_SIZE[1]):
        draw.line(
            (0, y, IMAGE_SIZE[0], y),
            fill=_interpolate_color(top_color, bottom_color, y / (IMAGE_SIZE[1] - 1)),
        )

    glow = Image.new("RGBA", IMAGE_SIZE, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((390, 105, 870, 585), fill=(*accent, 130))
    glow_draw.ellipse((-180, 770, 350, 1300), fill=(*accent, 70))
    image = Image.alpha_composite(image.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(72)))

    glass = Image.new("RGBA", IMAGE_SIZE, (0, 0, 0, 0))
    glass_draw = ImageDraw.Draw(glass)
    glass_draw.rounded_rectangle(
        (42, 112, 678, 1168),
        radius=38,
        fill=(8, 15, 23, 178),
        outline=(225, 238, 241, 105),
        width=2,
    )
    image = Image.alpha_composite(image, glass)
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((78, 150, 112, 184), radius=12, fill=(*accent, 255))
    title_font = _load_font(42)
    body_font = _load_font(30)
    small_font = _load_font(22)
    light = (239, 245, 245, 255)
    muted = (190, 204, 207, 255)
    y = _draw_wrapped_text(
        draw,
        creator["handle"],
        (82, 220),
        title_font,
        light,
        540,
        line_gap=16,
    )
    y = _draw_wrapped_text(
        draw,
        creator["niche"],
        (82, y + 24),
        body_font,
        muted,
        540,
        line_gap=12,
    )
    draw.line((82, y + 26, 638, y + 26), fill=(*accent, 255), width=3)
    y = _draw_wrapped_text(
        draw,
        f"SCENE {scene_index + 1} OF {TOTAL_SCENES}  |  {content['media_type'].upper()}",
        (82, y + 60),
        small_font,
        muted,
        540,
        line_gap=10,
    )
    y = _draw_wrapped_text(
        draw,
        content["caption"][:180],
        (82, y + 34),
        body_font,
        light,
        540,
        line_gap=14,
    )
    _draw_wrapped_text(
        draw,
        scene_prompt,
        (82, min(y + 34, 1000)),
        small_font,
        muted,
        540,
        line_gap=10,
    )
    return image.convert("RGB")


def _scene_keywords(scene_prompt, caption):
    stop_words = {
        "about", "after", "along", "and", "are", "beside", "between", "clear",
        "clearly", "close", "creator", "detail", "each", "from", "hands", "into",
        "natural", "niche", "shot", "show", "side", "soft", "this", "vertical",
        "with", "without", "your", "five", "second", "seconds", "scene", "reel",
        "inspired", "light", "realistic", "focus", "text", "overlay",
        "cozy", "cosy", "gentle", "simple", "practical", "quick", "honest",
        "colorful", "colourful", "easy", "quiet", "calm", "bright", "warm",
        "small", "routine", "review", "walkthrough", "walk", "through",
    }
    words = re.findall(r"[A-Za-z][A-Za-z'-]{2,}", f"{caption} {scene_prompt}".lower())
    keywords = []
    for word in words:
        word = word.strip("'-")
        if word in stop_words or len(word) < 4 or word in keywords:
            continue
        keywords.append(word)
        if len(keywords) == 3:
            break
    return keywords


def _wikimedia_candidates(query):
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": "10",
        "prop": "imageinfo",
        "iiprop": "url|size",
        "iiurlwidth": "900",
        "format": "json",
    }
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "DealSenseSimBot/1.0"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
    pages = payload.get("query", {}).get("pages", {})
    return [
        image_info
        for page in pages.values()
        for image_info in page.get("imageinfo", [])
    ]


def _download_commons_image(
    creator,
    content,
    scene_prompt,
    used_photo_ids,
    cache_path,
):
    keywords = _scene_keywords(scene_prompt, content["caption"])
    niche_fallback = {
        "Healthy Food & Nutrition": "healthy food recipe ingredients",
        "Clean Skincare & Beauty": "skincare beauty routine products",
        "Home Fitness & Strength": "home fitness exercise equipment",
        "Tech & Student Productivity": "student desk productivity technology",
        "Sustainable Home & Decor": "sustainable home decor handmade",
    }.get(creator["niche"], "lifestyle home objects")
    queries = []
    if keywords:
        query_keywords = " ".join(keywords)
        queries.append(f"filetype:bitmap {query_keywords} {niche_fallback}")
        queries.append(f"filetype:bitmap {query_keywords}")
    queries.append(f"filetype:bitmap {niche_fallback}")

    try:
        for query in queries:
            for image_info in _wikimedia_candidates(query):
                if image_info.get("width", 0) < 600:
                    continue
                image_url = image_info.get("thumburl") or image_info.get("url")
                if not image_url or image_url in used_photo_ids:
                    continue
                image_request = urllib.request.Request(
                    image_url,
                    headers={"User-Agent": "DealSenseSimBot/1.0"},
                )
                try:
                    with urllib.request.urlopen(image_request, timeout=20) as response:
                        image_bytes = response.read()
                    photo_id = hashlib.sha256(image_bytes).hexdigest()
                    if photo_id in used_photo_ids:
                        continue
                    with Image.open(BytesIO(image_bytes)) as fetched_image:
                        image = ImageOps.fit(
                            fetched_image.convert("RGB"),
                            IMAGE_SIZE,
                            method=Image.Resampling.LANCZOS,
                        )
                    used_photo_ids.add(image_url)
                    used_photo_ids.add(photo_id)
                    image.save(cache_path, format="JPEG", quality=92)
                    return image
                except (urllib.error.URLError, TimeoutError, OSError):
                    continue
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as error:
        print(f"  Wikimedia Commons request failed: {error}", flush=True)
    return None


def _get_scene_image(creator, content, scene_prompt, scene_index, used_photo_ids):
    cache_dir = SCENE_FRAME_DIR / content["content_slug"]
    cache_dir.mkdir(parents=True, exist_ok=True)
    for extension in (".jpg", ".png"):
        cache_path = cache_dir / f"scene_{scene_index + 1}{extension}"
        if not cache_path.is_file():
            continue
        try:
            image_bytes = cache_path.read_bytes()
            photo_id = hashlib.sha256(image_bytes).hexdigest()
            if photo_id in used_photo_ids:
                continue
            with Image.open(BytesIO(image_bytes)) as cached_image:
                image = ImageOps.fit(
                    cached_image.convert("RGB"),
                    IMAGE_SIZE,
                    method=Image.Resampling.LANCZOS,
                )
            used_photo_ids.add(photo_id)
            print(f"  Scene {scene_index + 1}: using cached frame.", flush=True)
            return image
        except OSError:
            continue

    cache_path = cache_dir / f"scene_{scene_index + 1}.jpg"
    image = _download_commons_image(
        creator,
        content,
        scene_prompt,
        used_photo_ids,
        cache_path,
    )
    if image is not None:
        print(f"  Scene {scene_index + 1}: cached Wikimedia Commons image.", flush=True)
        return image

    print(
        f"  Scene {scene_index + 1}: using dark niche-styled fallback frame.",
        flush=True,
    )
    return _fallback_image(creator, content, scene_prompt, scene_index)


def _run_ffmpeg(ffmpeg_exe, arguments):
    subprocess.run([ffmpeg_exe, "-y", *arguments], check=True)


def _normalize_custom_clip(ffmpeg_exe, source, output):
    video_filter = (
        "scale=720:1280:force_original_aspect_ratio=increase,"
        "crop=720:1280,fps=30,"
        "tpad=stop_mode=clone:stop_duration=5,"
        "trim=duration=5,setpts=PTS-STARTPTS,setsar=1"
    )
    _run_ffmpeg(
        ffmpeg_exe,
        [
            "-i",
            str(source),
            "-vf",
            video_filter,
            "-an",
            "-frames:v",
            str(FRAMES_PER_SCENE),
            "-r",
            "30",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-pix_fmt",
            "yuv420p",
            str(output),
        ],
    )


def _make_scene_clip(ffmpeg_exe, image_path, output, scene_index):
    if scene_index % 2 == 0:
        zoom_expression = "min(zoom+0.00055,1.08)"
    else:
        zoom_expression = "max(1.08-on*0.00055,1.0)"
    zoom_filter = (
        "scale=900:1600,"
        f"zoompan=z='{zoom_expression}':d=150:"
        "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        "s=720x1280:fps=30"
    )
    _run_ffmpeg(
        ffmpeg_exe,
        [
            "-framerate",
            "30",
            "-i",
            str(image_path),
            "-vf",
            zoom_filter,
            "-frames:v",
            str(FRAMES_PER_SCENE),
            "-t",
            "5",
            "-an",
            "-r",
            "30",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-pix_fmt",
            "yuv420p",
            str(output),
        ],
    )


def _concatenate_clips(ffmpeg_exe, clips, list_path, output_path):
    list_path.write_text(
        "".join(f"file '{clip.resolve().as_posix()}'\n" for clip in clips),
        encoding="utf-8",
    )
    _run_ffmpeg(
        ffmpeg_exe,
        [
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_path),
            "-an",
            "-frames:v",
            str(TOTAL_FRAMES),
            "-t",
            "30",
            "-r",
            "30",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-pix_fmt",
            "yuv420p",
            str(output_path),
        ],
    )


def _build_base_video(ffmpeg_exe, creator, content, storyboard, work_dir):
    slug = content["content_slug"]
    custom_dir = CUSTOM_CLIP_DIR / slug
    scene_clips = []
    if len(storyboard["scenes"]) != TOTAL_SCENES:
        raise ValueError(
            f"Expected {TOTAL_SCENES} scenes for {slug}; "
            f"found {len(storyboard['scenes'])}."
        )

    custom_clips = [
        custom_dir / f"clip_{clip_index}.mp4"
        for clip_index in range(1, TOTAL_SCENES + 1)
        if (custom_dir / f"clip_{clip_index}.mp4").is_file()
    ]
    if custom_clips:
        print(
            f"  Custom clip override: {len(custom_clips)} clip(s), cycling to six scenes.",
            flush=True,
        )
        for scene_index in range(TOTAL_SCENES):
            output_clip = work_dir / f"scene_{scene_index + 1:02d}.mp4"
            source_clip = custom_clips[scene_index % len(custom_clips)]
            _normalize_custom_clip(ffmpeg_exe, source_clip, output_clip)
            scene_clips.append(output_clip)
    else:
        used_photo_ids = set()
        for scene_index, scene_prompt in enumerate(storyboard["scenes"]):
            output_clip = work_dir / f"scene_{scene_index + 1:02d}.mp4"
            image_path = work_dir / f"scene_{scene_index + 1:02d}.jpg"
            scene_image = _get_scene_image(
                creator,
                content,
                scene_prompt,
                scene_index,
                used_photo_ids,
            )
            scene_image.save(image_path, format="JPEG", quality=92)
            _make_scene_clip(ffmpeg_exe, image_path, output_clip, scene_index)
            scene_clips.append(output_clip)

    base_video = work_dir / "base_30s.mp4"
    _concatenate_clips(
        ffmpeg_exe,
        scene_clips,
        work_dir / "concat_list.txt",
        base_video,
    )
    return base_video


def _mux_voiceover(ffmpeg_exe, base_video, temp_mp3, output_path):
    _run_ffmpeg(
        ffmpeg_exe,
        [
            "-i",
            str(base_video),
            "-i",
            str(temp_mp3),
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
            "-t",
            "30",
            "-movflags",
            "+faststart",
            str(output_path),
        ],
    )


async def _upgrade_reel(ffmpeg_exe, creator, content, original_index):
    profile = VOICE_PROFILES.get(creator["handle"])
    if profile is None:
        raise ValueError(f"No voice profile configured for {creator['handle']}.")

    REEL_DIR.mkdir(parents=True, exist_ok=True)
    output_path = REEL_DIR / f"{content['content_slug']}.mp4"
    storyboard = build_reel_storyboard(creator, content)

    with tempfile.TemporaryDirectory(prefix=f"{content['content_slug']}_", dir=REEL_DIR) as work_dir:
        work_dir = Path(work_dir)
        base_video = _build_base_video(
            ffmpeg_exe,
            creator,
            content,
            storyboard,
            work_dir,
        )
        temp_mp3 = work_dir / "voiceover.mp3"
        await edge_tts.Communicate(
            storyboard["script"],
            voice=profile["voice"],
            rate=profile["rate"],
            pitch=profile["pitch"],
        ).save(str(temp_mp3))

        temp_output = work_dir / "voiced_reel.mp4"
        _mux_voiceover(ffmpeg_exe, base_video, temp_mp3, temp_output)
        os.replace(temp_output, output_path)


def _parse_args():
    parser = argparse.ArgumentParser(
        description="Upgrade demo reels to 30-second storyboard videos with voiceovers."
    )
    parser.add_argument(
        "--slug",
        help="Process only the reel with this content slug.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Process at most this many reels after applying --slug.",
    )
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be a positive integer.")
    return args


async def upgrade_reels(slug=None, limit=None):
    all_video_items = [
        (index, creator, content)
        for index, (creator, content) in enumerate(
            (
                (creator, content)
                for creator in DEMO_CREATORS
                for content in creator["contents"]
                if content.get("video_path") is not None
            ),
            start=1,
        )
    ]
    if len(all_video_items) != 35:
        raise ValueError(
            f"Expected 35 reel/video items; found {len(all_video_items)}."
        )

    selected_items = all_video_items
    if slug is not None:
        selected_items = [
            item for item in selected_items if item[2]["content_slug"] == slug
        ]
        if not selected_items:
            raise ValueError(f"No reel/video found with content slug {slug}.")
    if limit is not None:
        if limit < 1:
            raise ValueError("limit must be a positive integer.")
        selected_items = selected_items[:limit]

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    selected_total = len(selected_items)
    for selected_index, (original_index, creator, content) in enumerate(
        selected_items,
        start=1,
    ):
        print(
            f"[{original_index}/35] ({selected_index}/{selected_total}) "
            f"{creator['handle']} - {content['content_slug']}",
            flush=True,
        )
        await _upgrade_reel(ffmpeg_exe, creator, content, original_index)


def main():
    args = _parse_args()
    asyncio.run(upgrade_reels(slug=args.slug, limit=args.limit))


if __name__ == "__main__":
    main()
