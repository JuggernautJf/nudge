"""Cleaning, PII scrubbing, de-duplication and category tagging."""
import html
import re
import warnings

from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
PHONE_RE = re.compile(r"(?:\+?91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}\b")
BOILERPLATE_RE = re.compile(r"(equal opportunity employer.*?$)", re.I | re.M)
MIN_DESCRIPTION_CHARS = 100  # Adzuna descriptions are snippets (~500 chars)


def clean_text(text: str) -> str:
    text = BeautifulSoup(html.unescape(text or ""), "html.parser").get_text(" ")
    text = EMAIL_RE.sub("[email]", text)
    text = PHONE_RE.sub("[phone]", text)
    text = BOILERPLATE_RE.sub("", text)
    return re.sub(r"\s+", " ", text).strip()


def categorize(title: str, categories: dict) -> str:
    t = f" {title.lower()} "
    # Check non-voice before voice so "non voice" isn't tagged as voice.
    for name, spec in sorted(categories.items(), key=lambda kv: "nonvoice" not in kv[0]):
        if any(k in t for k in spec["keywords"]):
            return name
    return "other"


def clean_jobs(jobs: list[dict], categories: dict) -> list[dict]:
    seen, out = set(), []
    for job in jobs:
        job["title"] = clean_text(job["title"])
        job["company"] = clean_text(job["company"])
        job["location"] = clean_text(job["location"])
        job["description"] = clean_text(job["description"])
        if not job["title"] or len(job["description"]) < MIN_DESCRIPTION_CHARS:
            continue
        key = (job["title"].lower(), job["company"].lower(), job["location"].lower())
        if key in seen:
            continue
        seen.add(key)
        job["category"] = job.get("category") or categorize(job["title"], categories)
        out.append(job)
    return out
