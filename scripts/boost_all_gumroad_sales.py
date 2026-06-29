#!/usr/bin/env python3
"""Truthful cross-product Gumroad sales boost for IndexRidge.

Actions:
- Lists every Gumroad product with pagination.
- Ensures a universal first-20-redemptions 20% offer code, WEEK1.
- Updates published product copy/tags/summaries with clearer buyer-fit,
  limitations, cross-links, and the honest discount note.
- Writes a non-secret manifest for verification.

No ads, outbound email, analytics, fake scarcity, fake testimonials, or
misleading revenue/accuracy/completeness claims are created here.
"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import urllib.parse
import urllib.request
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "commerce" / "sales_boost_manifest.json"
TOKEN_SERVICE = "gumroad-api"
TOKEN_ACCOUNT = "IndexRidge"
OFFER_CODE = "WEEK1"
OFFER_PERCENT = 20
OFFER_MAX_PURCHASES = 20
GUMROAD_PROFILE_URL = "https://indexridge.gumroad.com/"
FREE_SAMPLE_URL = "https://indexridge.gumroad.com/l/indexridge-free-sentinel-2-ndvi-geotiff-mini-sample"
FULL_BUNDLE_URL = "https://indexridge.gumroad.com/l/indexridge-sentinel-2-geotiff-starter-catalog-bundle"
TENDER_URL = "https://indexridge.gumroad.com/l/indexridge-uk-tender-signals-starter-pack"
APP_KIT_URL = "https://indexridge.gumroad.com/l/app-launch-control-kit"
GEO_PORTAL_URL = "https://indexridge.github.io/geospectral-data-portal/"
TENDER_SITE_URL = "https://indexridge.github.io/IndexRidgeTenderSignals/"
SUPPORT_EMAIL = "IndexRidge@outlook.com"
AI_DISCLOSURE = (
    "AI-assisted automation was involved in selecting, processing, collating, "
    "packaging, and publishing this dataset. It has not been checked, validated, "
    "or approved by a human operator before publication. Treat it as an "
    "unverified analytical sample and validate independently before use."
)
FORBIDDEN = [
    r"\bAhmir\b",
    r"\bArif\b",
    r"/Users/",
    r"ahmirarif",
    r"389770078606",
    r"AIDAVVQA3NGHG4TLQ3D4X",
    r"arn:aws:iam::",
]


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_token() -> str:
    env = os.environ.get("GUMROAD_ACCESS_TOKEN")
    if env:
        return env.strip()
    return subprocess.check_output(
        ["security", "find-generic-password", "-s", TOKEN_SERVICE, "-a", TOKEN_ACCOUNT, "-w"],
        text=True,
    ).strip()


def request_json(method: str, url: str, *, token: str | None = None, form: Iterable[tuple[str, str]] | dict[str, str] | None = None, timeout: int = 120) -> dict[str, Any]:
    data = None
    headers: dict[str, str] = {}
    if form is None and token:
        headers["Authorization"] = f"Bearer {token}"
    if form is not None:
        raw_items = list(form.items()) if isinstance(form, dict) else list(form)
        items: list[tuple[str, str]] = [(str(key), str(value)) for key, value in raw_items]
        if token:
            items.insert(0, ("access_token", token))
        data = urllib.parse.urlencode(items).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode())


def gumroad_request(method: str, endpoint: str, *, token: str, form: Iterable[tuple[str, str]] | dict[str, str] | None = None) -> dict[str, Any]:
    url = f"https://api.gumroad.com/v2/{endpoint.lstrip('/')}"
    result = request_json(method, url, token=token, form=form)
    if not result.get("success"):
        raise RuntimeError(f"Gumroad {method} {endpoint} failed: {result}")
    return result


def quote_product_id(product_id: str) -> str:
    return urllib.parse.quote(product_id, safe="")


def all_products(token: str) -> list[dict[str, Any]]:
    products: list[dict[str, Any]] = []
    url: str | None = "https://api.gumroad.com/v2/products"
    while url:
        full_url = url if url.startswith("http") else "https://api.gumroad.com" + url
        payload = request_json("GET", full_url, token=token)
        if not payload.get("success"):
            raise RuntimeError(f"Gumroad product list failed: {payload}")
        products.extend(payload.get("products") or [])
        url = payload.get("next_page_url")
    # Fetch full product objects to get files/custom fields consistently.
    full: list[dict[str, Any]] = []
    for product in products:
        payload = gumroad_request("GET", f"products/{quote_product_id(product['id'])}", token=token)
        full.append(payload["product"])
    return full


def assert_safe_text(label: str, text: str) -> None:
    hits = [pattern for pattern in FORBIDDEN if re.search(pattern, text, flags=re.I)]
    if hits:
        raise RuntimeError(f"Forbidden text in {label}: {hits}")


def discount_url(short_url: str) -> str:
    return short_url.rstrip("/") + f"/{OFFER_CODE}"


def discount_note() -> str:
    return (
        f"Use code <strong>{OFFER_CODE}</strong> for {OFFER_PERCENT}% off eligible paid IndexRidge Gumroad products "
        f"while the first {OFFER_MAX_PURCHASES} redemptions remain. Gumroad applies the final price at checkout; if a direct link does not apply it automatically, enter the code manually."
    )


def product_kind(product: dict[str, Any]) -> str:
    slug = product.get("custom_permalink") or ""
    tags = {str(t).lower() for t in product.get("tags") or []}
    name = str(product.get("name") or "").lower()
    if slug == "indexridge-uk-tender-signals-starter-pack":
        return "tender"
    if slug == "app-launch-control-kit":
        return "app_kit"
    if product.get("price") == 0 or "free" in tags or name.startswith("free "):
        return "free_geo"
    if "bundle" in tags or "bundle" in name:
        return "geo_bundle"
    if "geotiff" in tags or "sentinel-2" in tags or "geotiff" in name:
        return "geo_single"
    return "generic"


def geo_index_label(product: dict[str, Any]) -> str:
    text = (product.get("name") or "") + " " + " ".join(product.get("tags") or [])
    for label in ["NDVI", "NDMI", "NDWI", "NDBI"]:
        if label.lower() in text.lower():
            return label
    return "Sentinel-2"


def html_list(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"


def description_for(product: dict[str, Any]) -> str:
    kind = product_kind(product)
    name = product.get("name") or "IndexRidge product"
    short_url = product.get("short_url") or ""
    price = int(product.get("price") or 0)
    if kind == "tender":
        body = f"""<h2>UK public-sector tender signals in one self-serve download</h2>
<p>IndexRidge UK Tender Signals Starter Pack is a compact CSV/JSON data pack for scanning recent UK public-sector procurement opportunities without manually searching every notice.</p>
<h3>Included files</h3>
{html_list([
  'Procurement opportunities CSV',
  'Green-energy tender CSV',
  'Accessibility/digital tender CSV',
  'Full tender signals JSON',
  'Source licence metadata',
  'README with usage notes and disclaimer',
])}
<h3>Useful for</h3>
{html_list([
  'Quickly spotting recent public-sector tender opportunities.',
  'Reviewing green-energy, EV charging, retrofit, accessibility/digital, facilities, and SME-suitable signals.',
  'Importing official open procurement data into spreadsheets, CRMs, dashboards, or internal research workflows.',
])}
<h3>Intro discount</h3><p>{discount_note()}</p>
<h3>Source</h3><p>Generated from the official Contracts Finder OCDS Search API. Source/licence metadata is included in the download.</p>
<h3>Important limitations</h3>
<p><strong>Informational public-data monitoring only.</strong> This is not legal, procurement, bid-writing, financial, investment, tax, compliance, planning, engineering, environmental, or regulatory advice.</p>
<p>No guarantee is made that records are complete, accurate, current, suitable, commercially useful, or likely to lead to revenue, tender suitability, bid success, compliance, or any outcome. Records may be incomplete, delayed, duplicated, incorrectly classified, or missing context. Verify all information against the relevant official notice before acting.</p>
<p>Tender attachments, PDFs, images, logos, screenshots, paid-platform data, proprietary commentary, personal contact enrichment, and outbound lead lists are not included.</p>
<p>Self-serve digital download. Support is limited to file-access issues and obvious export errors through the marketplace platform; no calls, procurement advice, bid-writing, eligibility checks, bespoke research, or ongoing service are included.</p>"""
    elif kind == "app_kit":
        body = f"""<h2>App Store launch prep checklist and template pack</h2>
<p>App Launch Control Kit is a local-first checklist/template pack for indie iOS developers preparing an App Store submission or resubmission.</p>
<h3>Included</h3>
{html_list([
  'App Store launch-readiness checklist',
  'Screenshot capture and QA checklist',
  'Privacy, support, and terms page prompts',
  'Subscription / in-app purchase review checklist',
  'App Review response templates',
  "Release notes / What's New templates",
  'Small local readiness-audit script',
])}
<h3>Good for</h3>
{html_list([
  'Solo iOS developers preparing a first submission.',
  'Indie apps facing App Review clarification or rejection.',
  'Teams that want a local checklist before uploading screenshots, privacy pages, or review notes.',
])}
<h3>Intro discount</h3><p>{discount_note()}</p>
<h3>Important limitations</h3>
<p>This is a workflow aid and template pack. It is not legal advice, tax advice, financial advice, or a guarantee of App Store approval, downloads, subscriptions, revenue, or review outcome. Apple rules and reviewer decisions can change. You remain responsible for final review of your own app and listing.</p>
<p>Self-serve digital download only. No calls, bespoke review, developer support, App Store Connect access, or legal/compliance review are included.</p>"""
    elif kind == "free_geo":
        body = f"""<h2>Free tiny Sentinel-2 NDVI GeoTIFF sample</h2>
<p>Use this free mini sample to check that QGIS, GDAL, rasterio, Python notebooks, or a GIS dashboard can open the IndexRidge-style GeoTIFF package before buying a paid bundle.</p>
<h3>Good for</h3>
{html_list([
  'Testing file download and GIS loading workflow.',
  'Checking rasterio/QGIS compatibility before buying a paid IndexRidge pack.',
  'Reviewing the README/disclaimer/source-metadata style used in paid products.',
])}
<h3>Next paid options</h3>
{html_list([
  f'<a href="{discount_url(FULL_BUNDLE_URL)}">Full 8-AOI GeoTIFF starter bundle with code {OFFER_CODE}</a>',
  f'<a href="{GEO_PORTAL_URL}">Browse the public GeoTIFF catalog</a>',
])}
<h3>Important limitations</h3>
<p>{AI_DISCLOSURE}</p>
<p>This is a tiny analytical sample, not complete coverage, not official data, and not a regulatory, legal, insurance, planning, financial, agricultural-advisory, or operational decision product. Validate independently before relying on any output.</p>"""
    elif kind == "geo_bundle":
        member_hint = "eight" if "8" in name or "Catalog" in name else "four"
        savings = "less than buying all included £19 individual samples separately"
        body = f"""<h2>{name}</h2>
<p>A discounted ZIP bundle of {member_hint} Sentinel-derived regional GeoTIFF sample AOI products for GIS, QGIS, GDAL, rasterio, Python notebooks, dashboard prototypes, and raster ETL smoke tests.</p>
<h3>Why buy the bundle</h3>
{html_list([
  f'One download containing multiple ready-to-load sample AOIs; {savings}.',
  'Covers multiple index/workflow types such as NDVI, NDMI, NDWI, and NDBI where included.',
  'Useful for testing a data pipeline against different raster themes before commissioning broader work.',
])}
<h3>Intro discount</h3><p>{discount_note()}</p>
<h3>Try before buying</h3>
{html_list([
  f'<a href="{FREE_SAMPLE_URL}">Download the free NDVI mini sample</a>',
  f'<a href="{GEO_PORTAL_URL}">View the public IndexRidge GeoTIFF catalog</a>',
])}
<h3>Important limitations</h3>
<p>{AI_DISCLOSURE}</p>
<p>These are regional sample AOI products, not full-planet, continent, country, city, field, or continuously updated coverage. They are analytical workflow-test data products, not official government, legal, insurance, planning, financial, agricultural-advisory, environmental-compliance, or regulatory datasets. Validate independently before operational or commercial reliance.</p>
<p>Source imagery: Copernicus Sentinel-2 L2A via Microsoft Planetary Computer STAC. No AWS/S3/Data Exchange path or third-party marketplace approval is claimed.</p>"""
    elif kind == "geo_single":
        label = geo_index_label(product)
        body = f"""<h2>{label} GeoTIFF sample for GIS workflow testing</h2>
<p>{name} is a ready-to-load Sentinel-2 derived regional sample AOI package for QGIS, ArcGIS Pro, GDAL, rasterio, Python notebooks, GIS dashboards, and raster ETL smoke tests.</p>
<h3>Included</h3>
{html_list([
  'Compressed regional GeoTIFF raster.',
  'JSON source/processing report with source item, acquisition time, CRS, bounds, dimensions, and metrics.',
  'Buyer README and licence/disclaimer text.',
])}
<h3>Good for</h3>
{html_list([
  'Testing GIS/raster tooling with a small real-world Sentinel-derived package.',
  'Prototyping dashboards, ETL jobs, notebooks, and remote-sensing workflows.',
  'Evaluating the delivery format before buying a bundle or requesting broader coverage.',
])}
<h3>Intro discount</h3><p>{discount_note()}</p>
<h3>More cost-effective options</h3>
{html_list([
  f'<a href="{FREE_SAMPLE_URL}">Try the free NDVI mini sample first</a>',
  f'<a href="{discount_url(FULL_BUNDLE_URL)}">Get the full 8-AOI bundle with code {OFFER_CODE}</a>',
  f'<a href="{GEO_PORTAL_URL}">View the public IndexRidge GeoTIFF catalog</a>',
])}
<h3>Important limitations</h3>
<p>{AI_DISCLOSURE}</p>
<p>This is a regional sample AOI product, not full-country/full-city/full-field coverage, not continuously updated monitoring, and not official government, legal, insurance, planning, financial, agricultural-advisory, environmental-compliance, or regulatory data. Satellite-derived indices can be affected by cloud, haze, shadows, atmospheric conditions, acquisition timing, sensor limits, and processing assumptions. Validate independently before operational or commercial reliance.</p>
<p>Source imagery: Copernicus Sentinel-2 L2A via Microsoft Planetary Computer STAC. No AWS/S3/Data Exchange path or third-party marketplace approval is claimed.</p>"""
    else:
        body = f"""<h2>{name}</h2>
<p>Self-serve IndexRidge digital download.</p>
<h3>Intro discount</h3><p>{discount_note()}</p>
<h3>Important limitations</h3><p>No guarantee of sales, revenue, completeness, accuracy, suitability, or any operational outcome is made. Verify the product contents and source materials before relying on them.</p>"""
    if price > 0:
        body += f"\n<h3>Checkout shortcut</h3><p><a href=\"{discount_url(short_url)}\">Open this product with code {OFFER_CODE}</a></p>"
    assert_safe_text(f"description:{name}", body)
    return body


def tags_for(product: dict[str, Any]) -> list[str]:
    kind = product_kind(product)
    tags = [str(t) for t in (product.get("tags") or [])]
    additions = {
        "tender": ["uk-tenders", "procurement", "public-sector", "contracts-finder", "open-data", "csv", "b2b", "green-energy", "accessibility", "data-pack"],
        "app_kit": ["app-store", "ios", "launch-checklist", "app-review", "indie-dev", "templates", "software-development", "checklist"],
        "free_geo": ["free", "geospatial", "remote sensing", "ndvi", "sentinel-2", "geotiff", "qgis", "rasterio", "sample data"],
        "geo_bundle": ["geospatial", "remote sensing", "sentinel-2", "geotiff", "gis", "qgis", "rasterio", "ndvi", "ndmi", "ndwi", "ndbi", "bundle", "sample data"],
        "geo_single": ["geospatial", "remote sensing", "sentinel-2", "geotiff", "gis", "qgis", "rasterio", "sample data", "satellite data"],
    }.get(kind, ["digital product"])
    merged: list[str] = []
    for tag in tags + additions:
        if tag and tag not in merged:
            merged.append(tag)
    return merged[:13]


def summary_for(product: dict[str, Any]) -> str:
    kind = product_kind(product)
    original = product.get("custom_summary") or ""
    if kind == "tender":
        return "Self-serve UK tender signals CSV/JSON starter pack from official open procurement data; no advice or bid support."
    if kind == "app_kit":
        return "Checklist/template pack for indie iOS App Store submission prep; no legal advice or approval guarantee."
    if kind == "free_geo":
        return "Free tiny Sentinel-2 NDVI GeoTIFF sample for checking QGIS, GDAL, and rasterio workflows before buying paid bundles."
    if kind == "geo_bundle":
        return original or "Discounted Sentinel-derived GeoTIFF sample AOI bundle for QGIS, rasterio, dashboards, and GIS workflow testing."
    if kind == "geo_single":
        return original or "Ready-to-load Sentinel-derived GeoTIFF sample AOI for QGIS, rasterio, dashboards, and GIS workflow testing."
    return original[:140]


def category_for(product: dict[str, Any]) -> str:
    # Preserve Gumroad's current category label unless it is missing. Some
    # dashboard categories are not accepted by the public API as path strings.
    return product.get("category") or "business-and-money/marketing-and-sales/analytics"


def receipt_for(product: dict[str, Any]) -> str:
    kind = product_kind(product)
    name = product.get("name") or "this IndexRidge product"
    if kind == "tender":
        return f"Thanks for purchasing {name}. Download the ZIP, read README.txt and source_licences.json first, and verify all opportunities against the official notice before acting. This is informational public-data monitoring only, not legal/procurement/bid-writing/financial/compliance advice or a guarantee of completeness, bid success, revenue, or any outcome."
    if kind == "app_kit":
        return f"Thanks for purchasing {name}. Download the ZIP and read START_HERE.md first. This is a workflow aid and template pack, not legal advice and not a guarantee of App Store approval, downloads, subscriptions, revenue, or review outcome."
    if kind.startswith("geo"):
        return f"Thanks for downloading {name}. Read the README and licence/disclaimer before use. {AI_DISCLOSURE} This is an analytical sample, not official/regulatory advice or a guarantee of accuracy/completeness/suitability."
    return f"Thanks for purchasing {name}. Please read the included README/disclaimer before use."


def update_product(token: str, product: dict[str, Any]) -> dict[str, Any]:
    fields: list[tuple[str, str]] = [
        ("name", product.get("name") or "IndexRidge product"),
        ("description", description_for(product)),
        ("custom_permalink", product.get("custom_permalink") or ""),
        ("price", str(int(product.get("price") or 0))),
        ("price_currency_type", product.get("currency") or "gbp"),
        ("category", category_for(product)),
        ("custom_summary", summary_for(product)),
        ("custom_receipt", receipt_for(product)),
        ("display_product_reviews", "false"),
        ("should_show_sales_count", "false"),
    ]
    for tag in tags_for(product):
        fields.append(("tags[]", tag))
    payload = gumroad_request("PUT", f"products/{quote_product_id(product['id'])}", token=token, form=fields)
    return payload["product"]


def ensure_offer_code(token: str, anchor_product_id: str) -> dict[str, Any]:
    endpoint = f"products/{quote_product_id(anchor_product_id)}/offer_codes"
    existing = gumroad_request("GET", endpoint, token=token).get("offer_codes") or []
    for code in existing:
        if (code.get("name") or code.get("code")) == OFFER_CODE:
            return {"action": "existing", **code}
    created = gumroad_request(
        "POST",
        endpoint,
        token=token,
        form={
            "name": OFFER_CODE,
            "offer_type": "percent",
            "amount_off": str(OFFER_PERCENT),
            "max_purchase_count": str(OFFER_MAX_PURCHASES),
            "universal": "true",
        },
    )
    return {"action": "created", **created["offer_code"]}


def main() -> int:
    token = get_token()
    before = all_products(token)
    published = [p for p in before if p.get("published") and not p.get("deleted")]
    if not published:
        raise RuntimeError("No published Gumroad products found")
    paid = [p for p in published if int(p.get("price") or 0) > 0]
    offer = ensure_offer_code(token, paid[0]["id"])
    updated: list[dict[str, Any]] = []
    before_files = {p["id"]: len(p.get("files") or []) for p in published}
    for product in published:
        updated_product = update_product(token, product)
        updated.append(updated_product)
    after = all_products(token)
    after_by_id = {p["id"]: p for p in after}
    file_mismatches = []
    for product_id, count in before_files.items():
        after_count = len(after_by_id.get(product_id, {}).get("files") or [])
        if after_count != count:
            file_mismatches.append({"id": product_id, "before": count, "after": after_count})
    if file_mismatches:
        raise RuntimeError("Product file count changed unexpectedly: " + json.dumps(file_mismatches))
    manifest = {
        "ok": True,
        "updated_at_utc": now(),
        "offer_code": {
            "name": OFFER_CODE,
            "percent_off": OFFER_PERCENT,
            "max_purchase_count": OFFER_MAX_PURCHASES,
            "api_action": offer.get("action"),
            "id": offer.get("id"),
            "times_used": offer.get("times_used"),
            "universal": offer.get("universal"),
        },
        "products_updated": [
            {
                "id": p.get("id"),
                "name": p.get("name"),
                "kind": product_kind(p),
                "price_cents": p.get("price"),
                "currency": p.get("currency"),
                "published": p.get("published"),
                "short_url": p.get("short_url"),
                "discount_url": discount_url(p.get("short_url") or "") if int(p.get("price") or 0) > 0 else p.get("short_url"),
                "files_count": len(p.get("files") or []),
                "tags": p.get("tags"),
                "custom_summary": p.get("custom_summary"),
            }
            for p in sorted(updated, key=lambda x: (product_kind(x), x.get("name") or ""))
        ],
        "public_pages_to_update": {
            "geospectral_catalog": GEO_PORTAL_URL,
            "tender_signals": TENDER_SITE_URL,
        },
        "notes": "No ads, outbound outreach, analytics, fake scarcity, fake testimonials, or revenue guarantees were created.",
    }
    assert_safe_text("sales_boost_manifest", json.dumps(manifest))
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "products_updated": len(updated),
        "offer_code": manifest["offer_code"],
        "manifest": str(MANIFEST),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
