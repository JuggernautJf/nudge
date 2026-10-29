"""Polite Adzuna API client (India). Caches every raw response on disk."""
import hashlib
import json
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.adzuna.com/v1/api/jobs/in/search/{page}"
CACHE_DIR = Path(__file__).resolve().parents[2] / "data" / "cache" / "adzuna"
REQUEST_DELAY = 1.5  # seconds between live requests
HEADERS = {"User-Agent": "NudgeBot/0.1 (educational portfolio project)"}

_last_request = 0.0


def _cache_path(params: dict) -> Path:
    key = json.dumps({k: v for k, v in params.items() if k not in ("app_id", "app_key")}, sort_keys=True)
    return CACHE_DIR / f"{hashlib.sha1(key.encode()).hexdigest()}.json"


def search(what: str, where: str | None = None, page: int = 1, per_page: int = 50) -> list[dict]:
    """Return raw Adzuna results for one page, using the cache when possible."""
    global _last_request
    params = {
        "app_id": os.environ["ADZUNA_ID"],
        "app_key": os.environ["ADZUNA_KEY"],
        "what": what,
        "results_per_page": per_page,
        "content-type": "application/json",
        "page": page,
    }
    if where:
        params["where"] = where

    cache = _cache_path(params)
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))

    for attempt in range(4):
        wait = REQUEST_DELAY - (time.time() - _last_request)
        if wait > 0:
            time.sleep(wait)
        _last_request = time.time()

        query = {k: v for k, v in params.items() if k != "page"}
        resp = requests.get(BASE_URL.format(page=page), params=query, headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            cache.write_text(json.dumps(results, ensure_ascii=False), encoding="utf-8")
            return results
        if resp.status_code in (429, 500, 502, 503):
            time.sleep(2 ** attempt * 5)  # back off and retry
            continue
        resp.raise_for_status()
    return []


def normalize(raw: dict) -> dict:
    """Map an Adzuna result to the common Nudge job schema."""
    return {
        "id": f"adzuna_{raw.get('id')}",
        "source": "adzuna",
        "title": raw.get("title", ""),
        "company": (raw.get("company") or {}).get("display_name", ""),
        "location": (raw.get("location") or {}).get("display_name", ""),
        "description": raw.get("description", ""),
        "salary_min": raw.get("salary_min"),
        "salary_max": raw.get("salary_max"),
        "url": raw.get("redirect_url", ""),
        "posted_at": raw.get("created", ""),
        "tags": [(raw.get("category") or {}).get("label", "")],
    }
