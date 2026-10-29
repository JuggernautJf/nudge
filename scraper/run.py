"""Phase 1 entry point: fetch -> normalize -> clean -> balance -> save.

Usage (from the repo root):
    python -m scraper.run                 # full run
    python -m scraper.run --target 50     # quick test run
"""
import argparse
import json
from collections import Counter
from pathlib import Path

import yaml

from scraper.clean import categorize, clean_jobs
from scraper.sources import adzuna, naukri_kaggle

ROOT = Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "data" / "processed" / "jobs.json"


def fetch_adzuna(name: str, spec: dict, cities: list[str], target: int, categories: dict) -> list[dict]:
    """Query Adzuna city by city until the category has `target` matching jobs."""
    jobs, ids = [], set()
    for query in spec["queries"]:
        for city in cities:
            for page in range(1, 4):
                results = adzuna.search(query, where=city, page=page)
                for raw in results:
                    job = adzuna.normalize(raw)
                    # Keep only jobs whose title actually matches this category.
                    if job["id"] in ids or categorize(job["title"], categories) != name:
                        continue
                    ids.add(job["id"])
                    job["category"] = name
                    jobs.append(job)
                if len(results) < 50 or len(jobs) >= target * 1.3:
                    break
            if len(jobs) >= target * 1.3:  # extra headroom for dedup losses
                return jobs
    return jobs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, help="override listings per category")
    args = parser.parse_args()

    config = yaml.safe_load((Path(__file__).parent / "categories.yaml").read_text(encoding="utf-8"))
    categories = config["categories"]
    target = args.target or config["target_per_category"]

    jobs = naukri_kaggle.load()
    print(f"Naukri CSV: {len(jobs)} rows")

    for name, spec in categories.items():
        found = fetch_adzuna(name, spec, config["cities"], target, categories)
        print(f"Adzuna {name:<28} {len(found)}")
        jobs.extend(found)

    jobs = clean_jobs(jobs, categories)

    # Balance: cap each category so no single role floods the swipe deck.
    counts, balanced = Counter(), []
    for job in jobs:
        if job["category"] != "other" and counts[job["category"]] < target:
            counts[job["category"]] += 1
            balanced.append(job)

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(balanced, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nSaved {len(balanced)} jobs -> {OUT_FILE.relative_to(ROOT)}")
    for name in categories:
        print(f"  {name:<28} {counts[name]}")


if __name__ == "__main__":
    main()
