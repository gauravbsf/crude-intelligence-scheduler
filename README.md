# Crude Intelligence India — Cloud Scheduler

This small public repository runs three read-only jobs for the owner-private Crude Intelligence India site using GitHub Actions:

- news-event price-correlation capture every five minutes; and
- official JODI crude-oil bulk-data ingestion once daily; and
- broad official crude/geopolitical news collection and controlled impact analysis once daily.

## Safety and scope

- The repository contains no Site credential or market-account secret.
- The private Site authorization token is stored only as the encrypted GitHub Actions secret `CRUDE_INTELLIGENCE_SITE_TOKEN`.
- The workflow calls only the read-only intelligence endpoint.
- The JODI workflow filters the official bulk archive to a compact 24-month payload for controlled countries and measures, then records the source SHA-256 checksum.
- Trading, order placement and account functions remain disabled.
- `crudeintel.in` is not activated by this repository.

## Schedule

The workflow is scheduled with `*/5 * * * *` (UTC) and can also be run manually for verification. GitHub may occasionally delay scheduled jobs during periods of high service load.

The JODI workflow is scheduled at `02:20 UTC` daily. Repeated source files are idempotent; a changed controlled dataset or source revision creates a new append-only vintage.

The broad news workflow is scheduled at `02:35 UTC` (`08:05 Asia/Kolkata`) daily. It calls the owner-private Site, where server-side source policy and analysis are enforced; the public scheduler repository contains no news or AI API secret.

GitHub automatically disables scheduled workflows in public repositories after 60 days without repository activity. A deliberate maintenance commit before that interval keeps the schedule active.

## Production target

`POST https://crude-intelligence-gaura.gauravkumar-ips.chatgpt.site/api/intelligence/news/run`

`POST https://crude-intelligence-gaura.gauravkumar-ips.chatgpt.site/api/ingestion/jodi`

`POST https://crude-intelligence-gaura.gauravkumar-ips.chatgpt.site/api/intelligence/news/daily/run`

Successful runs must return `ready` or `partial` and report the trigger as `cloud-scheduler:github-actions`.
