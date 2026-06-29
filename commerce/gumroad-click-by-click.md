# Gumroad click-by-click setup

Use this after creating/logging into the Gumroad account.

## Create the product

1. Go to `https://gumroad.com/`.
2. Click **Start selling** or **Login**.
3. Complete account setup if prompted.
4. From the Gumroad dashboard, click **New product**.
5. Choose **Digital product** / **I want to sell a digital product**.
6. Product name: `IndexRidge UK Tender Signals Starter Pack`.
7. Price: `£9`.
8. Product URL/slug: `indexridge-uk-tender-signals-starter-pack` if available.
9. Upload the file:
   `/Users/ahmirarif/Developer/IndexRidgeTenderSignals/commerce/gumroad_upload/indexridge-uk-tender-signals-starter-pack-latest.zip`
10. Add the short and full descriptions from `commerce/gumroad-product-listing.md`.
11. Add tags from `commerce/gumroad-product-listing.md`.
12. Add the cover image from `commerce/assets/tender-signals-cover.png`.
13. Make sure the product is a **one-time purchase**, not a membership/subscription, for the first launch.
14. Disable any setting that implies coaching, consulting, calls, or bespoke support.
15. Check tax/payment/payout settings in Gumroad. Do not publish until payout/tax identity details are correct.
16. Preview the product page.
17. Confirm the disclaimer appears in the description.
18. Publish the product.
19. Copy the public product URL.
20. Send/paste the URL back to Hermes, or run `scripts/set_checkout_links.py` with the URL.

## Post-publish check

Open the Gumroad product page in a private/incognito browser window and confirm:

- price is £9;
- the ZIP is attached;
- description contains the no-advice/no-guarantee disclaimer;
- no subscription promise is made;
- no customer-call/bespoke-service support is offered;
- product page does not claim official affiliation, complete coverage, guaranteed leads, revenue, compliance, or bid success.
