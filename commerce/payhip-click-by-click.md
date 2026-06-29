# Payhip click-by-click setup

Use Payhip if you want a lower-fee direct checkout/storefront and are willing to drive traffic from the IndexRidge pages. If you need marketplace/discovery first, Gumroad is the better first launch because Gumroad has more marketplace-style discovery.

## Create the account

1. Go to `https://payhip.com/`.
2. Click **Get started** or **Start selling**.
3. Enter email/password or use the sign-in option offered.
4. Verify your email if Payhip asks.
5. Open the Payhip dashboard.
6. Complete seller profile/account setup.
7. Go to **Account** / **Settings**.
8. Add payout details.
9. Review tax/VAT settings and platform terms before selling.
10. Keep the plan on the free tier initially unless Payhip's current fee math makes a paid plan worthwhile.

## Create the digital product

1. In the dashboard, click **Products**.
2. Click **Add product**.
3. Select **Digital product** / **Digital download**.
4. Product title: `IndexRidge UK Tender Signals Starter Pack`.
5. Price: `£9`.
6. Upload file:
   `/Users/ahmirarif/Developer/IndexRidgeTenderSignals/commerce/gumroad_upload/indexridge-uk-tender-signals-starter-pack-latest.zip`
7. Add product description from `commerce/gumroad-product-listing.md`.
8. Add tags/categories if Payhip offers them:
   - procurement
   - UK tenders
   - public sector
   - open data
   - CSV
   - B2B leads
   - green energy
   - accessibility
9. Upload cover image from `commerce/assets/tender-signals-cover.png`.
10. Set delivery type to **instant file download**.
11. Do not enable coaching, custom service, appointments, memberships, or calls for the first product.
12. If Payhip offers a license key/serial-number feature, leave it off.
13. If Payhip offers a limit on downloads, keep it reasonable; do not make claims that require manual support.
14. Add refund/support wording:
    `Self-serve digital download. Support is limited to file-access issues and obvious export errors. No procurement advice, bid-writing, eligibility checks, bespoke research, or calls are included.`
15. Add the mandatory disclaimer:
    `Informational public-data monitoring only; not legal, procurement, bid-writing, financial, investment, tax, compliance, planning, engineering, environmental, or regulatory advice. No guarantee of completeness, accuracy, tender suitability, bid success, revenue, or compliance. Verify against official notices before acting.`
16. Save as draft.
17. Preview the product page.
18. Confirm the page does not claim official affiliation, complete coverage, guaranteed leads, guaranteed revenue, compliance, or bid success.
19. Publish the product.
20. Copy the Payhip product URL.
21. Send/paste the URL back to Hermes, or run:

```bash
cd /Users/ahmirarif/Developer/IndexRidgeTenderSignals
python3 scripts/set_checkout_links.py --payhip-url 'https://YOUR-PAYHIP-URL'
git add index.html data-packs.html commerce/checkout-links.json
git commit -m 'Add Payhip checkout link'
git push origin main
```

## Which Payhip plan?

Start with the free plan unless current Payhip pricing makes a paid plan cheaper for your actual sales volume. A paid plan only makes sense once monthly transaction fees exceed the subscription cost.
