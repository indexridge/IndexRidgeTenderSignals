# IndexRidge Tender Signals

Public beta MVP for two low-interaction products:

1. **UK tender/procurement micro-alerts** — niche public-sector tender monitoring for renewable energy, EV charging, retrofit, digital/accessibility, and SME-suitable opportunities.
2. **Downloadable public-data packs** — CSV/JSON/ZIP sample packs generated from approved official/open data sources.

Gumroad checkout is active for the first one-off starter data pack. No signup form, analytics, ads, outbound outreach, calls, bespoke support, or subscription product is active.

## Low-risk operating rules

- Use official/open public sources only, preferably Open Government Licence sources.
- Store factual notice fields, generated tags/summaries, source links, and attribution.
- Do not copy tender attachments, PDFs, images, logos, maps, screenshots, paid-platform data, or proprietary commentary.
- Do not claim official status, complete coverage, guaranteed leads, guaranteed revenue, bid success, compliance, or due-diligence suitability.
- Do not provide legal/procurement/bid-writing/financial/investment/tax/compliance advice.
- Do not add payment, newsletter signup, analytics, ads, or outbound outreach without explicit approval.

## Current MVP source

- Contracts Finder OCDS Search API
- Documentation: `https://www.contractsfinder.service.gov.uk/apidocumentation/Notices/1/GET-Published-Notice-OCDS-Search`
- Licence: Open Government Licence v3.0 / licence metadata returned by the official feed

## Run

```bash
cd /Users/ahmirarif/Developer/IndexRidgeTenderSignals
python3 scripts/fetch_tender_signals.py --days 14
```

Generated public files are written to `packs/`:

- `tender_signals_sample.csv`
- `tender_signals_sample.json`
- `tender_signals_sample.md`
- `data-pack-procurement-opportunities.csv`
- `data-pack-green-energy-tenders.csv`
- `data-pack-accessibility-digital-tenders.csv`
- `indexridge-public-data-pack-sample.zip`
- `index.json`
- `source_licences.json`

The script also prepares a private, git-ignored Gumroad upload ZIP at:

```text
commerce/gumroad_upload/indexridge-uk-tender-signals-starter-pack-latest.zip
```

Public files in `packs/` are preview samples; the Gumroad upload ZIP is not linked publicly.

## Verification

There is no canonical suite. Use targeted ad-hoc verification for local/public-page changes: Python compile, data fetch, CSV schema/category checks, source licence checks, GitHub Pages `built`, live HTTP 200, expected homepage/data-pack/privacy/terms markers, and clean git tracking status.

## Monetisation status

- First paid product: Gumroad one-off starter data pack.
- Gumroad URL: `https://indexridge.gumroad.com/l/indexridge-uk-tender-signals-starter-pack`
- Product price: £9.
- Current public checkout is self-serve only; no subscription, outreach, ads, calls, bespoke support, or managed procurement service is active.
- Keep source coverage conservative and do not claim completeness.

## Commerce setup docs

- Gumroad product listing draft: `commerce/gumroad-product-listing.md`
- Gumroad click-by-click setup: `commerce/gumroad-click-by-click.md`
- Payhip click-by-click setup: `commerce/payhip-click-by-click.md`
- Unbiased platform comparison: `commerce/marketplace-comparison.md`
- Checkout link updater: `scripts/set_checkout_links.py`
