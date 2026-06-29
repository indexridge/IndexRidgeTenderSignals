#!/usr/bin/env python3
"""Set marketplace checkout links on the static pages.

This script is intentionally explicit: it only updates the small marked checkout
CTA blocks in index.html and data-packs.html plus commerce/checkout-links.json.
It should be run after the user creates a real Gumroad/Payhip product URL.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "commerce" / "checkout-links.json"
START = "<!-- CHECKOUT_CTA_START -->"
END = "<!-- CHECKOUT_CTA_END -->"


def load_config() -> dict[str, str]:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return {"gumroad_url": "", "payhip_url": "", "updated_at_utc": "", "notes": ""}


def validate_url(name: str, url: str) -> None:
    if not url:
        return
    if not (url.startswith("https://") and "." in url):
        raise SystemExit(f"{name} must be a full https:// URL")


def build_block(gumroad_url: str, payhip_url: str) -> str:
    links: list[str] = []
    if gumroad_url:
        links.append(f'<a class="button primary" href="{gumroad_url}">Buy starter pack on Gumroad</a>')
    if payhip_url:
        links.append(f'<a class="button secondary" href="{payhip_url}">Buy starter pack on Payhip</a>')
    if links:
        return "\n".join(
            [
                START,
                '<div class="actions" aria-label="Checkout links">',
                *[f"  {link}" for link in links],
                "</div>",
                '<p><strong>Paid download:</strong> Self-serve digital file only. No advice, calls, bespoke research, or guaranteed outcomes are included.</p>',
                END,
            ]
        )
    return "\n".join(
        [
            START,
            "<p><strong>Paid checkout:</strong> Gumroad product assets are prepared, but the public checkout URL is not active yet.</p>",
            END,
        ]
    )


def replace_block(path: Path, block: str) -> None:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    if not pattern.search(text):
        raise SystemExit(f"checkout block markers missing in {path}")
    path.write_text(pattern.sub(block, text), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Set Gumroad/Payhip checkout links on static pages")
    parser.add_argument("--gumroad-url", default=None, help="Published Gumroad product URL")
    parser.add_argument("--payhip-url", default=None, help="Published Payhip product URL")
    args = parser.parse_args()

    config = load_config()
    gumroad_url = args.gumroad_url if args.gumroad_url is not None else config.get("gumroad_url", "")
    payhip_url = args.payhip_url if args.payhip_url is not None else config.get("payhip_url", "")
    validate_url("gumroad_url", gumroad_url)
    validate_url("payhip_url", payhip_url)

    block = build_block(gumroad_url, payhip_url)
    for rel in ["index.html", "data-packs.html"]:
        replace_block(ROOT / rel, block)

    config.update(
        {
            "gumroad_url": gumroad_url,
            "payhip_url": payhip_url,
            "updated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "notes": "Checkout links are only active when URL values are non-empty.",
        }
    )
    CONFIG_PATH.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("OK updated checkout links", CONFIG_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
