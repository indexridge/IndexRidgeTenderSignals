#!/usr/bin/env python3
"""Fetch low-risk UK tender signals and public-data pack samples.

Uses the official Contracts Finder OCDS Search API. It does not copy tender
attachments, scrape paid platforms, enrich personal contacts, or send outreach.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import urllib.parse
import urllib.request
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
PACKS_DIR = ROOT / "packs"
OUTPUTS_DIR = ROOT / "outputs"
GUMROAD_UPLOAD_DIR = ROOT / "commerce" / "gumroad_upload"
API_URL = "https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search"
DOC_URL = "https://www.contractsfinder.service.gov.uk/apidocumentation/Notices/1/GET-Published-Notice-OCDS-Search"

DISCLAIMER = (
    "Informational public-data monitoring only; not legal, procurement, bid-writing, "
    "financial, investment, tax, compliance, planning, engineering, environmental, or "
    "regulatory advice. Verify against the official notice before acting."
)

CATEGORIES: dict[str, list[str]] = {
    "green_energy": [
        r"\bsolar\b", r"photovoltaic", r"\bPV\b", r"battery", r"\bBESS\b",
        r"energy storage", r"EV charging", r"electric vehicle", r"charge point",
        r"heat pump", r"retrofit", r"decarbonisation", r"decarbonization",
        r"net zero", r"renewable", r"energy efficiency", r"insulation", r"LED lighting",
        r"substation", r"grid connection",
    ],
    "accessibility_digital": [
        r"accessibility", r"WCAG", r"assistive", r"inclusive design", r"website",
        r"web site", r"digital platform", r"content management", r"portal", r"software",
        r"user research", r"service design",
    ],
    "sme_suitable": [r"SME", r"small business", r"suitability"],
    "facilities_works": [
        r"maintenance", r"installation", r"mechanical", r"electrical", r"building works",
        r"refurbishment", r"heating", r"ventilation", r"air-conditioning", r"chiller",
    ],
}

FIELDS = [
    "ocid", "notice_id", "published_date", "deadline", "title", "buyer", "status",
    "procurement_method", "main_category", "cpv_id", "cpv_description", "value_amount",
    "value_currency", "sme_suitable", "vcse_suitable", "categories", "matched_terms",
    "official_notice_url", "summary", "licence", "source",
]


@dataclass
class TenderSignal:
    ocid: str
    notice_id: str
    published_date: str
    deadline: str
    title: str
    buyer: str
    status: str
    procurement_method: str
    main_category: str
    cpv_id: str
    cpv_description: str
    value_amount: str
    value_currency: str
    sme_suitable: str
    vcse_suitable: str
    categories: str
    matched_terms: str
    official_notice_url: str
    summary: str
    licence: str
    source: str = "Contracts Finder OCDS Search API"


def fetch_json(days: int) -> dict:
    now = datetime.now(timezone.utc)
    published_from = (now - timedelta(days=days)).strftime("%Y-%m-%dT00:00:00")
    published_to = now.strftime("%Y-%m-%dT23:59:59")
    params = {
        "publishedFrom": published_from,
        "publishedTo": published_to,
        "stages": "planning,tender",
    }
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "IndexRidgeTenderSignalsMVP/0.1"})
    with urllib.request.urlopen(req, timeout=45) as response:
        return json.load(response)


def text_blob(release: dict) -> str:
    tender = release.get("tender") or {}
    parts = [
        tender.get("title") or "",
        tender.get("description") or "",
        ((tender.get("classification") or {}).get("description") or ""),
    ]
    for item in tender.get("additionalClassifications") or []:
        parts.append(item.get("description") or "")
    return "\n".join(parts)


def classify(release: dict) -> tuple[list[str], list[str]]:
    blob = text_blob(release)
    categories: list[str] = []
    terms: list[str] = []
    tender = release.get("tender") or {}
    suitability = tender.get("suitability") or {}
    if suitability.get("sme"):
        categories.append("sme_suitable")
        terms.append("SME suitability flag")
    for category, patterns in CATEGORIES.items():
        if category == "sme_suitable":
            continue
        for pattern in patterns:
            if re.search(pattern, blob, flags=re.IGNORECASE):
                categories.append(category)
                terms.append(pattern.replace(r"\b", ""))
                break
    return sorted(set(categories)), sorted(set(terms))


def first_document_url(tender: dict) -> str:
    for doc in tender.get("documents") or []:
        url = doc.get("url") or ""
        if url.startswith("http"):
            return url
    return ""


def buyer_name(release: dict) -> str:
    buyer = release.get("buyer") or {}
    if buyer.get("name"):
        return str(buyer["name"])
    for party in release.get("parties") or []:
        roles = party.get("roles") or []
        if "buyer" in roles and party.get("name"):
            return str(party["name"])
    return ""


def make_summary(description: str, max_len: int = 220) -> str:
    clean = re.sub(r"\s+", " ", description or "").strip()
    if len(clean) <= max_len:
        return clean
    return clean[: max_len - 1].rstrip() + "…"


def iter_signals(payload: dict) -> Iterable[TenderSignal]:
    licence = payload.get("license") or "Open Government Licence v3.0"
    for release in payload.get("releases") or []:
        tender = release.get("tender") or {}
        categories, terms = classify(release)
        if not categories:
            continue
        classification = tender.get("classification") or {}
        value = tender.get("value") or {}
        suitability = tender.get("suitability") or {}
        yield TenderSignal(
            ocid=str(release.get("ocid") or ""),
            notice_id=str(release.get("id") or ""),
            published_date=str(tender.get("datePublished") or release.get("date") or ""),
            deadline=str((tender.get("tenderPeriod") or {}).get("endDate") or ""),
            title=str(tender.get("title") or ""),
            buyer=buyer_name(release),
            status=str(tender.get("status") or ""),
            procurement_method=str(tender.get("procurementMethodDetails") or tender.get("procurementMethod") or ""),
            main_category=str(tender.get("mainProcurementCategory") or ""),
            cpv_id=str(classification.get("id") or ""),
            cpv_description=str(classification.get("description") or ""),
            value_amount=str(value.get("amount") or ""),
            value_currency=str(value.get("currency") or ""),
            sme_suitable=str(bool(suitability.get("sme"))),
            vcse_suitable=str(bool(suitability.get("vcse"))),
            categories=";".join(categories),
            matched_terms=";".join(terms),
            official_notice_url=first_document_url(tender),
            summary=make_summary(str(tender.get("description") or "")),
            licence=str(licence),
        )


def write_csv(path: Path, signals: list[TenderSignal]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(asdict(s) for s in signals)


def _write_record_json(path: Path, signals: list[TenderSignal], generated_at: str, days: int, label: str) -> None:
    rows = [asdict(signal) for signal in signals]
    path.write_text(
        json.dumps(
            {
                "generated_at_utc": generated_at,
                "source": "Contracts Finder OCDS Search API",
                "source_documentation": DOC_URL,
                "days": days,
                "record_count": len(signals),
                "dataset_label": label,
                "disclaimer": DISCLAIMER,
                "records": rows,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def _write_markdown(path: Path, signals: list[TenderSignal], generated_at: str, days: int, label: str) -> None:
    md_lines = [
        "# Tender Signals Sample Digest",
        "",
        f"Generated: {generated_at}",
        f"Dataset: {label}",
        f"Source window: last {days} days from Contracts Finder OCDS Search API",
        f"Matching records shown: {len(signals)}",
        "",
        f"> {DISCLAIMER}",
        "",
        "Source: Contracts Finder OCDS Search API. Licence metadata is included in `source_licences.json`.",
        "",
    ]
    for signal in signals[:30]:
        md_lines.extend(
            [
                f"## {signal.title or 'Untitled tender'}",
                "",
                f"- Buyer: {signal.buyer or 'not supplied'}",
                f"- Deadline: {signal.deadline or 'not supplied'}",
                f"- Categories: {signal.categories}",
                f"- CPV: {signal.cpv_id} {signal.cpv_description}".strip(),
                f"- SME suitable: {signal.sme_suitable}",
                f"- Official notice: {signal.official_notice_url or 'not supplied'}",
                f"- Summary: {signal.summary}",
                "",
            ]
        )
    path.write_text("\n".join(md_lines), encoding="utf-8")


def _split_packs(signals: list[TenderSignal]) -> tuple[list[TenderSignal], list[TenderSignal], list[TenderSignal]]:
    procurement_pack = signals
    green_pack = [s for s in signals if "green_energy" in s.categories.split(";")]
    accessibility_pack = [s for s in signals if "accessibility_digital" in s.categories.split(";")]
    return procurement_pack, green_pack, accessibility_pack


def _write_pack_files(base: Path, signals: list[TenderSignal], generated_at: str, days: int, label: str) -> dict[str, int]:
    base.mkdir(parents=True, exist_ok=True)
    write_csv(base / "tender_signals_sample.csv", signals)
    _write_record_json(base / "tender_signals_sample.json", signals, generated_at, days, label)
    _write_markdown(base / "tender_signals_sample.md", signals, generated_at, days, label)
    procurement_pack, green_pack, accessibility_pack = _split_packs(signals)
    write_csv(base / "data-pack-procurement-opportunities.csv", procurement_pack)
    write_csv(base / "data-pack-green-energy-tenders.csv", green_pack)
    write_csv(base / "data-pack-accessibility-digital-tenders.csv", accessibility_pack)
    return {
        "procurement": len(procurement_pack),
        "green_energy": len(green_pack),
        "accessibility_digital": len(accessibility_pack),
    }


def _write_zip(base: Path, zip_path: Path, title: str) -> None:
    readme = "\n".join(
        [
            f"# {title}",
            "",
            "Source: Contracts Finder OCDS Search API.",
            "Licence metadata: see source_licences.json.",
            "",
            DISCLAIMER,
            "",
            "Included files:",
            "- data-pack-procurement-opportunities.csv",
            "- data-pack-green-energy-tenders.csv",
            "- data-pack-accessibility-digital-tenders.csv",
            "- tender_signals_sample.json",
            "- source_licences.json",
            "",
        ]
    )
    (base / "README.txt").write_text(readme, encoding="utf-8")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name in [
            "README.txt",
            "data-pack-procurement-opportunities.csv",
            "data-pack-green-energy-tenders.csv",
            "data-pack-accessibility-digital-tenders.csv",
            "tender_signals_sample.json",
            "source_licences.json",
        ]:
            z.write(base / name, arcname=name)


def write_outputs(signals: list[TenderSignal], payload: dict, days: int, public_preview_limit: int) -> Path:
    PACKS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    GUMROAD_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    public_signals = signals[:public_preview_limit]

    public_counts = _write_pack_files(PACKS_DIR, public_signals, generated_at, days, "public preview sample")
    full_counts = _write_pack_files(OUTPUTS_DIR, signals, generated_at, days, "full local Gumroad upload dataset")

    licence_payload = {
        "generated_at_utc": generated_at,
        "source": "Contracts Finder OCDS Search API",
        "documentation_url": DOC_URL,
        "publisher": payload.get("publisher"),
        "licence": payload.get("license") or "Open Government Licence v3.0",
        "publication_policy": payload.get("publicationPolicy"),
        "disclaimer": DISCLAIMER,
    }
    for base in (PACKS_DIR, OUTPUTS_DIR):
        (base / "source_licences.json").write_text(json.dumps(licence_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    catalog = {
        "generated_at_utc": generated_at,
        "disclaimer": DISCLAIMER,
        "public_preview_limit": public_preview_limit,
        "full_local_records": len(signals),
        "packs": [
            {
                "name": "Procurement opportunities sample pack",
                "file": "data-pack-procurement-opportunities.csv",
                "records": public_counts["procurement"],
                "full_local_records": full_counts["procurement"],
                "description": "Matched UK public-sector tender and planning notices from official open data.",
            },
            {
                "name": "Green energy tender sample pack",
                "file": "data-pack-green-energy-tenders.csv",
                "records": public_counts["green_energy"],
                "full_local_records": full_counts["green_energy"],
                "description": "Tender notices with solar, battery, EV charging, retrofit, net-zero, energy-efficiency or related signals.",
            },
            {
                "name": "Accessibility/digital tender sample pack",
                "file": "data-pack-accessibility-digital-tenders.csv",
                "records": public_counts["accessibility_digital"],
                "full_local_records": full_counts["accessibility_digital"],
                "description": "Tender notices with website, digital platform, accessibility, WCAG, inclusive design or software signals.",
            },
        ],
    }
    (PACKS_DIR / "index.json").write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    _write_zip(PACKS_DIR, PACKS_DIR / "indexridge-public-data-pack-sample.zip", "IndexRidge public-data pack preview sample")

    # Full pack for Gumroad upload is deliberately ignored by git and not linked publicly.
    for name in [
        "data-pack-procurement-opportunities.csv",
        "data-pack-green-energy-tenders.csv",
        "data-pack-accessibility-digital-tenders.csv",
        "tender_signals_sample.json",
        "source_licences.json",
    ]:
        (GUMROAD_UPLOAD_DIR / name).write_bytes((OUTPUTS_DIR / name).read_bytes())
    gumroad_zip = GUMROAD_UPLOAD_DIR / "indexridge-uk-tender-signals-starter-pack-latest.zip"
    _write_zip(GUMROAD_UPLOAD_DIR, gumroad_zip, "IndexRidge UK Tender Signals Starter Pack")
    manifest = {
        "generated_at_utc": generated_at,
        "gumroad_upload_zip": str(gumroad_zip),
        "full_records": len(signals),
        "public_preview_records": len(public_signals),
        "days": days,
        "disclaimer": DISCLAIMER,
    }
    (GUMROAD_UPLOAD_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return gumroad_zip


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch tender signals and generate public-data packs")
    parser.add_argument("--days", type=int, default=14, help="Published date window in days")
    parser.add_argument(
        "--public-preview-limit",
        type=int,
        default=20,
        help="Maximum number of matched records to publish in public preview packs",
    )
    args = parser.parse_args()
    if args.days < 1 or args.days > 60:
        parser.error("--days must be between 1 and 60")
    if args.public_preview_limit < 1 or args.public_preview_limit > 100:
        parser.error("--public-preview-limit must be between 1 and 100")
    payload = fetch_json(args.days)
    signals = list(iter_signals(payload))
    gumroad_zip = write_outputs(signals, payload, args.days, args.public_preview_limit)
    print(
        "OK",
        f"days={args.days}",
        f"source_releases={len(payload.get('releases') or [])}",
        f"matching_records={len(signals)}",
        f"public_preview_records={min(len(signals), args.public_preview_limit)}",
        f"pack_dir={PACKS_DIR}",
        f"gumroad_upload_zip={gumroad_zip}",
    )
    if not signals:
        print("WARNING: no matching tender signals found; increase --days or adjust keywords")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
