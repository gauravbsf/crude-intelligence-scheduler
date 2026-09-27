# Crude Intelligence India — Cloud Scheduler

This small public repository runs the owner-private Crude Intelligence India news-correlation ingestion every five minutes using GitHub Actions.

## Safety and scope

- The repository contains no Site credential or market-account secret.
- The private Site authorization token is stored only as the encrypted GitHub Actions secret `CRUDE_INTELLIGENCE_SITE_TOKEN`.
- The workflow calls only the read-only intelligence endpoint.
- Trading, order placement and account functions remain disabled.
- `crudeintel.in` is not activated by this repository.

## Schedule

The workflow is scheduled with `*/5 * * * *` (UTC) and can also be run manually for verification. GitHub may occasionally delay scheduled jobs during periods of high service load.

GitHub automatically disables scheduled workflows in public repositories after 60 days without repository activity. A deliberate maintenance commit before that interval keeps the schedule active.

## Production target

`POST https://crude-intelligence-gaura.gauravkumar-ips.chatgpt.site/api/intelligence/news/run`

Successful runs must return `ready` or `partial` and report the trigger as `cloud-scheduler:github-actions`.
