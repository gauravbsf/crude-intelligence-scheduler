# Crude Intelligence India — Cloud Scheduler

This small public repository runs four read-only jobs for the owner-private Crude Intelligence India site using GitHub Actions:

- news-event price-correlation and governed MCX quote-history capture every five minutes; and
- official JODI crude-oil bulk-data ingestion once daily; and
- broad official crude/geopolitical news collection and controlled impact analysis once daily; and
- official CFTC NYMEX WTI positioning ingestion once weekly.

## Safety and scope

- The repository contains no Site credential or market-account secret.
- The private Site authorization token is stored only as the encrypted GitHub Actions secret `CRUDE_INTELLIGENCE_SITE_TOKEN`.
- The workflow calls only read-only intelligence and market-data capture endpoints.
- MCX snapshots are append-only research history. They cannot place orders or activate the production Technical or Hybrid score.
- The JODI workflow filters the official bulk archive to a compact 24-month payload for controlled countries and measures, then records the source SHA-256 checksum.
- The CFTC workflow uses the official keyless CFTC public data service and records the source SHA-256 checksum for revision detection.
- Trading, order placement and account functions remain disabled.
- `crudeintel.in` is not activated by this repository.

## Schedule

The workflow is scheduled with `*/5 * * * *` (UTC) and can also be run manually for verification. GitHub may occasionally delay scheduled jobs during periods of high service load.

The JODI workflow is scheduled at `02:20 UTC` daily. Repeated source files are idempotent; a changed controlled dataset or source revision creates a new append-only vintage.

The broad news workflow is scheduled at `02:35 UTC` (`08:05 Asia/Kolkata`) daily. It calls the owner-private Site, where server-side source policy and analysis are enforced; the public scheduler repository contains no news or AI API secret.

The CFTC WTI positioning workflow is scheduled for Friday at `22:30 UTC` (Saturday `04:00 Asia/Kolkata`), after the usual Friday 3:30 p.m. Eastern CFTC release window. Holiday release schedules may vary, so the Site raises stale-ledger and stale-report alerts for operator review.

GitHub automatically disables scheduled workflows in public repositories after 60 days without repository activity. A deliberate maintenance commit before that interval keeps the schedule active.

## Production target

`POST https://crude-intelligence-gaura.gauravkumar-ips.chatgpt.site/api/intelligence/news/run`

`POST https://crude-intelligence-gaura.gauravkumar-ips.chatgpt.site/api/market/history/run`

`POST https://crude-intelligence-gaura.gauravkumar-ips.chatgpt.site/api/ingestion/jodi`

`POST https://crude-intelligence-gaura.gauravkumar-ips.chatgpt.site/api/intelligence/news/daily/run`

`POST https://crude-intelligence-gaura.gauravkumar-ips.chatgpt.site/api/ingestion/cftc/run`

The CFTC workflow requires `ready`, storage `stored` or `already-stored`, a valid source SHA-256 checksum, and the trigger `cloud-scheduler:github-actions`. The other successful runs must return `ready` or `partial` and report the same trigger.
