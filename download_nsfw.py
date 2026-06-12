"""
Download NSFW fan art for female Marvel Rivals characters.
Uses Bing image search (safe search off) to find and download images.
"""

import json
import re
import time
from pathlib import Path
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).parent
MEDIA_DIR = BASE_DIR / "media" / "marvel-rivals"
CHARACTERS_FILE = BASE_DIR / "characters.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Cookie": "SRCHHPGUSR=ADLT=OFF",
}


def sanitize_filename(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', "_", name)


def download_image(url: str, filepath: Path) -> bool:
    if filepath.exists():
        print(f"    Already exists: {filepath.name}")
        return True
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30, stream=True)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        if "image" not in content_type:
            return False
        content_length = resp.headers.get("content-length")
        if content_length and int(content_length) < 5000:
            return False
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
        size_kb = filepath.stat().st_size / 1024
        if size_kb < 5:
            filepath.unlink()
            return False
        print(f"    Downloaded: {filepath.name} ({size_kb:.0f} KB)")
        return True
    except Exception:
        if filepath.exists():
            filepath.unlink()
        return False


def bing_image_search_nsfw(query: str, count: int = 25) -> list[str]:
    """Search Bing Images with safe search off."""
    encoded_query = quote_plus(query)
    search_url = (
        f"https://www.bing.com/images/search?q={encoded_query}"
        f"&form=HDRSC2&first=1&tsc=ImageHoverTitle&adlt=off"
    )

    try:
        resp = requests.get(search_url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"    Search failed: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    image_urls = []

    for a_tag in soup.select("a.iusc"):
        m_attr = a_tag.get("m", "")
        match = re.search(r'"murl":"(https?://[^"]+)"', m_attr)
        if match:
            url = match.group(1).replace("\\u0026", "&")
            if any(ext in url.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                image_urls.append(url)

    return image_urls[:count]


def fetch_nsfw_for_character(character_name: str) -> int:
    """Download NSFW fan art for a single character."""
    print(f"\n{'='*60}")
    print(f"Processing: {character_name}")
    print(f"{'='*60}")

    char_slug = sanitize_filename(character_name.lower().replace(" ", "-"))
    char_dir = MEDIA_DIR / char_slug / "fan-art-nsfw"
    char_dir.mkdir(parents=True, exist_ok=True)

    queries = [
        f"Marvel Rivals {character_name} nsfw fan art",
        f"Marvel Rivals {character_name} nude fan art",
        f"Marvel Rivals {character_name} r34",
        f"{character_name} Marvel nsfw art",
    ]

    all_urls = []
    for query in queries:
        urls = bing_image_search_nsfw(query)
        all_urls.extend(urls)
        print(f"  Query '{query}': found {len(urls)} images")
        time.sleep(1.5)

    seen = set()
    unique_urls = []
    for url in all_urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)

    print(f"  Total unique URLs: {len(unique_urls)}")

    downloaded = 0
    for i, url in enumerate(unique_urls[:30], 1):
        ext = ".jpg"
        if ".png" in url.lower():
            ext = ".png"
        elif ".webp" in url.lower():
            ext = ".webp"

        filename = f"{char_slug}_nsfw_{i:03d}{ext}"
        filepath = char_dir / filename
        if download_image(url, filepath):
            downloaded += 1
        time.sleep(0.3)

    print(f"  Downloaded {downloaded} NSFW images for {character_name}")
    return downloaded


def main():
    with open(CHARACTERS_FILE) as f:
        data = json.load(f)

    characters = data["female_characters"]

    print("=" * 60)
    print("Marvel Rivals - NSFW Fan Art Downloader")
    print(f"Characters to process: {len(characters)}")
    print(f"Output directory: {MEDIA_DIR}")
    print("=" * 60)

    results = {}
    for character in characters:
        results[character] = fetch_nsfw_for_character(character)
        time.sleep(3)

    print(f"\n\n{'='*60}")
    print("FINAL RESULTS")
    print(f"{'='*60}")
    total = 0
    for char, count in results.items():
        total += count
        print(f"  {char:20s}: {count:3d} NSFW images")
    print(f"{'='*60}")
    print(f"  {'TOTAL':20s}: {total:3d} NSFW images")


if __name__ == "__main__":
    main()
