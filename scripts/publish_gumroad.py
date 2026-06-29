#!/usr/bin/env python3
"""Publish/update IndexRidge UK Tender Signals Starter Pack on Gumroad.

Operational guardrails:
- Uses the IndexRidge Gumroad token from macOS Keychain service `gumroad-api` or GUMROAD_ACCESS_TOKEN.
- Creates/updates only the `indexridge-uk-tender-signals-starter-pack` product.
- Uploads the prepared buyer ZIP from `commerce/gumroad_upload/`.
- Does not print access tokens or canonical Gumroad file URLs.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import urllib.parse
import urllib.request
import zipfile
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "commerce" / "gumroad_product_manifest.json"
UPLOAD_DIR = ROOT / "commerce" / "gumroad_upload"
ZIP_PATH = UPLOAD_DIR / "indexridge-uk-tender-signals-starter-pack-latest.zip"
PRODUCT_NAME = "IndexRidge UK Tender Signals Starter Pack"
CUSTOM_PERMALINK = "indexridge-uk-tender-signals-starter-pack"
EXPECTED_SHORT_URL = f"https://indexridge.gumroad.com/l/{CUSTOM_PERMALINK}"
PRICE_CENTS = 900
CURRENCY = "gbp"
CATEGORY = "business-and-money/marketing-and-sales/analytics"
SUMMARY = "A self-serve UK public-sector tender signals CSV/JSON pack generated from official open procurement data."
FORBIDDEN_PATTERNS = [
    r"\bAhmir\b",
    r"\bArif\b",
    r"/Users/",
    r"ahmirarif",
    r"GUMROAD_ACCESS_TOKEN",
    r"gumroad-api",
    r"PAYHIP_API_KEY",
    r"STRIPE",
    r"389770078606",
    r"AIDAVVQA3NGHG4TLQ3D4X",
    r"arn:aws:iam::",
]


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_token() -> str:
    env_token = os.environ.get("GUMROAD_ACCESS_TOKEN")
    if env_token:
        return env_token.strip()
    return subprocess.check_output(
        ["security", "find-generic-password", "-s", "gumroad-api", "-a", "IndexRidge", "-w"],
        text=True,
    ).strip()


def request_json(method: str, url: str, token: str | None = None, form: Iterable[tuple[str, str]] | dict[str, str] | None = None, timeout: int = 120) -> dict[str, Any]:
    data = None
    headers: dict[str, str] = {}
    if form is not None:
        data = urllib.parse.urlencode(form).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if token and form is None:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode())


def assert_buyer_zip_safe(path: Path) -> None:
    hits: list[str] = []
    with zipfile.ZipFile(path) as zf:
        bad_member = zf.testzip()
        if bad_member:
            raise RuntimeError(f"ZIP verification failed at {bad_member}")
        names = set(zf.namelist())
        expected = {
            "README.txt",
            "data-pack-procurement-opportunities.csv",
            "data-pack-green-energy-tenders.csv",
            "data-pack-accessibility-digital-tenders.csv",
            "tender_signals_sample.json",
            "source_licences.json",
        }
        missing = expected - names
        if missing:
            raise RuntimeError("Buyer ZIP missing expected files: " + ", ".join(sorted(missing)))
        for name in names:
            if not name.lower().endswith((".txt", ".md", ".json", ".html", ".csv")):
                continue
            text = zf.read(name).decode("utf-8", "ignore")
            for pattern in FORBIDDEN_PATTERNS:
                if re.search(pattern, text, flags=re.IGNORECASE):
                    hits.append(f"{name}: {pattern}")
    if hits:
        raise RuntimeError("Forbidden personal/account text found in buyer ZIP: " + "; ".join(hits))


def package_info() -> dict[str, Any]:
    if not ZIP_PATH.exists():
        raise FileNotFoundError(f"Missing Gumroad upload ZIP: {ZIP_PATH}")
    assert_buyer_zip_safe(ZIP_PATH)
    data = ZIP_PATH.read_bytes()
    with zipfile.ZipFile(ZIP_PATH) as zf:
        members = zf.namelist()
    return {
        "path": str(ZIP_PATH),
        "bytes": ZIP_PATH.stat().st_size,
        "sha256": hashlib.sha256(data).hexdigest(),
        "members": members,
    }


def upload_file(token: str, package: dict[str, Any]) -> str:
    presign = request_json(
        "POST",
        "https://api.gumroad.com/v2/files/presign",
        form={
            "access_token": token,
            "filename": Path(package["path"]).name,
            "file_size": str(package["bytes"]),
        },
    )
    if not presign.get("success"):
        raise RuntimeError(f"Gumroad file presign failed: {presign}")
    file_bytes = Path(package["path"]).read_bytes()
    part_size = 100 * 1024 * 1024
    completed: list[tuple[int, str]] = []
    for part in presign["parts"]:
        part_number = int(part["part_number"])
        chunk = file_bytes[(part_number - 1) * part_size : part_number * part_size]
        req = urllib.request.Request(part["presigned_url"], data=chunk, method="PUT")
        with urllib.request.urlopen(req, timeout=300) as response:
            etag = response.headers.get("ETag")
        if not etag:
            raise RuntimeError(f"Gumroad upload part {part_number} returned no ETag")
        completed.append((part_number, etag))
    fields: list[tuple[str, str]] = [
        ("access_token", token),
        ("upload_id", presign["upload_id"]),
        ("key", presign["key"]),
    ]
    for part_number, etag in completed:
        fields.append(("parts[][part_number]", str(part_number)))
        fields.append(("parts[][etag]", etag))
    complete = request_json("POST", "https://api.gumroad.com/v2/files/complete", form=fields)
    if not complete.get("success"):
        raise RuntimeError(f"Gumroad file complete failed: {complete}")
    return complete["file_url"]


def description_html() -> str:
    return """<h2>UK public-sector tender signals in one self-serve download</h2>
<p>IndexRidge UK Tender Signals Starter Pack is a compact CSV/JSON data pack for scanning recent UK public-sector procurement opportunities without manually searching every notice.</p>
<h3>Included files</h3>
<ul>
  <li>Procurement opportunities CSV</li>
  <li>Green-energy tender CSV</li>
  <li>Accessibility/digital tender CSV</li>
  <li>Full tender signals JSON</li>
  <li>Source licence metadata</li>
  <li>README with usage notes and disclaimer</li>
</ul>
<h3>Useful for</h3>
<ul>
  <li>Quickly spotting recent public-sector tender opportunities.</li>
  <li>Reviewing green-energy, EV charging, retrofit, accessibility/digital, facilities, and SME-suitable signals.</li>
  <li>Importing official open procurement data into spreadsheets, CRMs, dashboards, or internal research workflows.</li>
</ul>
<h3>Source</h3>
<p>Generated from the official Contracts Finder OCDS Search API. Source/licence metadata is included in the download.</p>
<h3>Important limitations</h3>
<p><strong>Informational public-data monitoring only.</strong> This is not legal, procurement, bid-writing, financial, investment, tax, compliance, planning, engineering, environmental, or regulatory advice.</p>
<p>No guarantee is made that records are complete, accurate, current, suitable, commercially useful, or likely to lead to revenue, tender suitability, bid success, compliance, or any outcome. Records may be incomplete, delayed, duplicated, incorrectly classified, or missing context. Verify all information against the relevant official notice before acting.</p>
<p>Tender attachments, PDFs, images, logos, screenshots, paid-platform data, proprietary commentary, personal contact enrichment, and outbound lead lists are not included.</p>
<p>Self-serve digital download. Support is limited to file-access issues and obvious export errors via the marketplace platform; no calls, procurement advice, bid-writing, eligibility checks, bespoke research, or ongoing service are included.</p>"""


def product_fields(file_url: str) -> list[tuple[str, str]]:
    fields: list[tuple[str, str]] = [
        ("name", PRODUCT_NAME),
        ("description", description_html()),
        ("custom_permalink", CUSTOM_PERMALINK),
        ("price", str(PRICE_CENTS)),
        ("price_currency_type", CURRENCY),
        ("category", CATEGORY),
        ("custom_summary", SUMMARY),
        (
            "custom_receipt",
            "Thanks for purchasing IndexRidge UK Tender Signals Starter Pack. Download the ZIP, read README.txt and source_licences.json first, and verify all opportunities against the official notice before acting. This is informational public-data monitoring only, not legal/procurement/bid-writing/financial/compliance advice or a guarantee of completeness, bid success, revenue, or any outcome.",
        ),
        ("display_product_reviews", "false"),
        ("should_show_sales_count", "false"),
        ("files[][url]", file_url),
    ]
    for tag in ["uk-tenders", "procurement", "public-sector", "open-data", "csv", "b2b", "green-energy", "accessibility"]:
        fields.append(("tags[]", tag))
    return fields


def list_products(token: str) -> list[dict[str, Any]]:
    result = request_json("GET", "https://api.gumroad.com/v2/products", token=token)
    if not result.get("success"):
        raise RuntimeError(f"Gumroad product list failed: {result}")
    return result.get("products") or []


def find_existing(token: str) -> dict[str, Any] | None:
    for product in list_products(token):
        if product.get("custom_permalink") == CUSTOM_PERMALINK or product.get("name") == PRODUCT_NAME:
            return product
    return None


def create_product(token: str, file_url: str) -> dict[str, Any]:
    result = request_json("POST", "https://api.gumroad.com/v2/products", form=[("access_token", token), *product_fields(file_url)])
    if not result.get("success"):
        raise RuntimeError(f"Gumroad product create failed: {result}")
    return result["product"]


def update_product(token: str, product_id: str, file_url: str) -> dict[str, Any]:
    product_path = urllib.parse.quote(product_id, safe="")
    result = request_json("PUT", f"https://api.gumroad.com/v2/products/{product_path}", form=[("access_token", token), *product_fields(file_url)])
    if not result.get("success"):
        raise RuntimeError(f"Gumroad product update failed: {result}")
    return result["product"]


def publish_product(token: str, product_id: str) -> dict[str, Any]:
    product_path = urllib.parse.quote(product_id, safe="")
    result = request_json("PUT", f"https://api.gumroad.com/v2/products/{product_path}/enable", form={"access_token": token})
    if not result.get("success"):
        raise RuntimeError(f"Gumroad publish failed: {result}")
    return result.get("product", result)


def fetch_product(token: str, product_id: str) -> dict[str, Any]:
    product_path = urllib.parse.quote(product_id, safe="")
    result = request_json("GET", f"https://api.gumroad.com/v2/products/{product_path}", token=token)
    if not result.get("success"):
        raise RuntimeError(f"Gumroad product fetch failed: {result}")
    return result["product"]


def main() -> int:
    package = package_info()
    token = get_token()
    file_url = upload_file(token, package)
    existing = find_existing(token)
    if existing:
        product = update_product(token, existing["id"], file_url)
        action = "updated"
    else:
        product = create_product(token, file_url)
        action = "created"
    product = publish_product(token, product["id"])
    product = fetch_product(token, product["id"])
    manifest = {
        "ok": True,
        "action": action,
        "updated_at_utc": now(),
        "product_id": product.get("id"),
        "name": product.get("name"),
        "published": product.get("published"),
        "short_url": product.get("short_url") or EXPECTED_SHORT_URL,
        "price_cents": product.get("price"),
        "currency": product.get("currency") or CURRENCY,
        "files_count": len(product.get("files") or []),
        "package": package,
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
