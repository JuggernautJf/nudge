"""Loader for the Kaggle "Naukri.com job postings" CSV (optional source).

Drop the CSV into data/raw/naukri/. Column names vary between dataset
versions, so we look for the first matching candidate for each field.
"""
from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "naukri"

COLUMNS = {
    "title": ["jobtitle", "job_title", "title"],
    "company": ["company", "company_name"],
    "location": ["joblocation_address", "location", "job_location"],
    "description": ["jobdescription", "job_description", "description"],
    "skills": ["skills", "key_skills"],
    "posted_at": ["postdate", "posted_date", "date"],
    "url": ["url", "job_url"],
}


def _pick(df: pd.DataFrame, candidates: list[str]) -> pd.Series:
    lower = {c.lower(): c for c in df.columns}
    for name in candidates:
        if name in lower:
            return df[lower[name]].fillna("").astype(str)
    return pd.Series([""] * len(df), index=df.index)


def load() -> list[dict]:
    files = list(RAW_DIR.glob("*.csv"))
    if not files:
        return []
    jobs = []
    for f in files:
        df = pd.read_csv(f, encoding_errors="replace", low_memory=False)
        cols = {field: _pick(df, cands) for field, cands in COLUMNS.items()}
        for i in range(len(df)):
            jobs.append({
                "id": f"naukri_{f.stem}_{i}",
                "source": "naukri_kaggle",
                "title": cols["title"].iat[i],
                "company": cols["company"].iat[i],
                "location": cols["location"].iat[i],
                "description": cols["description"].iat[i],
                "salary_min": None,
                "salary_max": None,
                "url": cols["url"].iat[i],
                "posted_at": cols["posted_at"].iat[i],
                "tags": [s.strip() for s in cols["skills"].iat[i].split(",") if s.strip()],
            })
    return jobs
