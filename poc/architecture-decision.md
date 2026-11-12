# Shipment middleware decision — POC

Status: provisional design decision; no deployment or live service contract verified.

## Decision

Keep the existing public-image delivery service unchanged. Continue the Python/SQLite shipment core as an isolated **offline synthetic prototype**, not as the final deployment architecture. A separate shipment worker and shared durable state are candidates, subject to identifying the actual ERP interface, middleware operations and target access. Before an environment-backed integration, confirm a supported runtime, state store, schedule, operational owner and approved source/carrier/Salesforce contracts.

## Evidence from the existing middleware

At inspected source revision `890194efc1dd059a551a65e238bcaa1c1f21c0a7`, the image service uses Node 24 on a pinned Linux image, built from four modules with no package install. Its HTTP server has a health endpoint, explicit allowlist, bounded image requests, startup verification and a non-root user; the Cloud Run recipe uses secret injection and a separate service. Synthetic Node tests exercise routing and failure paths. Those are useful deployment, configuration and testing patterns, not shipment adapters.

The media workflow has an experimental local lock and append-only journal for a single state directory. It can inspect unresolved media writes, but does not provide cross-machine coordination. Its live apply remains disabled. Experimental Python configuration/read adapters are offline and not connected to a real client, graph or writer. None proves ERP paging, carrier polling, Salesforce Shipment batch writes, distributed scheduling or buyer permissions. The source is a private branch with tenant-specific history; do not copy it or its configuration into public Git without a separate review.

## Options and tradeoffs

- Extend the existing Node image server: reuse its container conventions, but mix unrelated image request delivery with scheduled shipment processing and risk the working service. Its current code lacks a durable shipment workflow. Not selected.
- Separate Node shipment worker: matches the existing Node runtime and allows operational reuse, but still needs new adapters, persistent state, scheduling and tests. Worth evaluating once interface contracts and operating ownership are known.
- Separate Python shipment worker: preserves the synthetic Python prototype and its tested core, but adds a second runtime and requires its own support, container and persistent-state solution. Selected for **offline prototype only**; no live-runtime decision is inferred.

Cloud Run Jobs with Cloud Scheduler are a possible later route, not an authorized or verified deployment. [Cloud Run scheduling documentation](https://cloud.google.com/run/docs/execute/jobs-on-schedule) and [container runtime contract](https://cloud.google.com/run/docs/container-contract) describe platform behavior. Container-local files are not a durable cross-instance ledger; select and test a persistent state service and locking/reconciliation approach before relying on it. Do not expose a public endpoint merely to run jobs.

## Reuse and next bounded work

1. Preserve the current synthetic tests and inspect which generic validation, safe-error, secret-injection and test patterns are portable; verify license and sanitize any actual code reuse.
2. Obtain and verify the ERP source identity, pagination, cursor and order crosswalk; confirm carrier authentication, event mapping and correction behavior, and Salesforce Shipment schema/permissions.
3. Define durable staging and replay, per-record results, reconciliation of uncertain writes, operational alerts and multi-run coordination. SQLite in this prototype establishes none of these across instances.
4. Design and test Eastern schedules, DST/missed runs and the explicit Job A completion/readiness gate for Job B. Measure all Salesforce calls; the five-request goal remains unresolved for pagination, retries and lookups.
5. Verify buyer account isolation, multiple shipments and link rendering in an authorized sandbox; execute a clean-install test and independent verification. All live checks and acceptance are NOT RUN.
