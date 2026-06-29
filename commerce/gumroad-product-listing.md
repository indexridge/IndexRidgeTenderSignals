# Gumroad product listing draft

Use this to create the first Gumroad listing.

## Product type

Digital product / file download.

## Product name

IndexRidge UK Tender Signals Starter Pack

## Suggested URL slug

`indexridge-uk-tender-signals-starter-pack`

## Suggested launch price

- Start: **£9** one-off.
- Optional: allow discount/coupon for early buyers.
- Do not promise future updates unless you intend to update the Gumroad file regularly.

## Upload file

Local file prepared by the fetch script:

`/Users/ahmirarif/Developer/IndexRidgeTenderSignals/commerce/gumroad_upload/indexridge-uk-tender-signals-starter-pack-latest.zip`

This local upload ZIP is intentionally git-ignored and not linked publicly.

## Short description

A downloadable UK public-sector tender signals pack generated from official open procurement data. Includes CSV/JSON files filtered into practical niches such as green energy, EV charging, retrofit, accessibility/digital, facilities works, and SME-suitable opportunities.

## Full description

IndexRidge UK Tender Signals Starter Pack is a self-serve public-data download for people who want to scan UK public-sector procurement opportunities without manually searching every notice.

Included files:

- Procurement opportunities CSV
- Green-energy tender CSV
- Accessibility/digital tender CSV
- Full tender signals JSON
- Source licence metadata
- README with usage notes and disclaimer

Typical fields include notice title, buyer, deadline, procurement method, CPV classification, SME suitability flag, generated category tags, official notice URL, and a short factual summary.

Source: official Contracts Finder OCDS Search API.

Important limitations:

- Informational public-data monitoring only.
- Not legal, procurement, bid-writing, financial, investment, tax, compliance, planning, engineering, environmental, or regulatory advice.
- No guarantee of completeness, accuracy, lead quality, revenue, tender suitability, or bid success.
- Records may be incomplete, delayed, duplicated, incorrectly classified, or missing context.
- Users must verify all information against the relevant official notice before acting.
- Tender attachments, PDFs, images, logos, screenshots, paid-platform data, and proprietary commentary are not included.

## Category/tags

Suggested tags:

- procurement
- UK tenders
- public sector
- open data
- CSV
- B2B leads
- green energy
- EV charging
- accessibility
- data pack

## Thumbnail/cover

Use the local PNG cover:

`/Users/ahmirarif/Developer/IndexRidgeTenderSignals/commerce/assets/tender-signals-cover.png`

Fallback SVG source:

`/Users/ahmirarif/Developer/IndexRidgeTenderSignals/commerce/assets/tender-signals-cover.svg`

## Refund wording

Suggested conservative wording:

Digital download. Because the file is delivered immediately, refunds are discretionary unless there is a duplicate purchase or a clear file-access problem. This does not affect statutory rights where applicable.

## Support wording

This is a self-serve data product. Support is limited to file-access issues and obvious data-export errors. It does not include procurement advice, bid-writing support, eligibility checks, bespoke research, or customer calls.

## After product creation

Copy the Gumroad product URL and run:

```bash
cd /Users/ahmirarif/Developer/IndexRidgeTenderSignals
python3 scripts/set_checkout_links.py --gumroad-url 'https://YOUR-GUMROAD-URL'
git add index.html data-packs.html commerce/checkout-links.json
git commit -m 'Add Gumroad checkout link'
git push origin main
```

Then verify the live page before sharing it.
