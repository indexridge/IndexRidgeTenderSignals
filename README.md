# IndexRidge Tender Signals

Public beta MVP for two low-interaction products:

1. **UK tender/procurement micro-alerts** — niche public-sector tender monitoring for renewable energy, EV charging, retrofit, digital/accessibility, and SME-suitable opportunities.
2. **Downloadable public-data packs** — CSV/JSON/ZIP sample packs generated from approved official/open data sources.

No paid checkout, signup, analytics, ads, or outreach are active in this beta.

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

## Verification

There is no canonical suite. Use targeted ad-hoc verification for local/public-page changes: Python compile, data fetch, CSV schema/category checks, source licence checks, GitHub Pages `built`, live HTTP 200, expected homepage/data-pack/privacy/terms markers, and clean git tracking status.

## Monetisation gate

Before making this paid:

- Add at least one payment platform account/product approved by the user.
- Add support/refund/cancellation wording.
- Decide whether the first paid offer is a tender-alert subscription, a one-off data-pack download, or both.
- Review source coverage and do not claim completeness.
