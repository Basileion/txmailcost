# TxMailCost

Published transactional email API pricing (Amazon SES, Resend, Postmark, SendGrid, Mailgun, MailerSend, Mailtrap, SMTP2GO), normalized to a monthly bill by volume.

- Data: `data/vendors.json` (every plan row has a source URL + check date; never invent numbers)
- Build: `python3 scripts/build.py && python3 scripts/workbook.py` -> `dist/`
- Publish: `dist/` is pushed to the `gh-pages` branch (GitHub Pages). Set `SITE`/`BASE` env vars to retarget (e.g. `SITE=https://txmailcost.pages.dev BASE=` for Cloudflare Pages).
- Weekly upkeep: re-read the 8 pricing pages, update `vendors.json`, add a row to the changes list in `build.py`, rebuild.
