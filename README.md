# Reusable shipment tracking proof of concept

This repository contains a synthetic offline prototype and a plan for a reusable Salesforce shipment tracking integration; live synchronization is not yet verified. The POC reads sample shipments from Salesforce, aims to fetch live USPS tracking, and simulates UPS and FedEx. ERP ingestion is deferred. Never place a real org hostname, token, password, account number, tracking number, exported data, log or private configuration in this repository.

Read [the implementation plan](docs/implementation-plan.md) before building. Copy `.env.example` to `.env` locally and supply values through your deployment's secret manager. `.env` and local configuration files are ignored; ignoring files does not remove secrets already committed or prevent intentional force-add. Inspect staged files and scan for secrets before committing or publishing.

The proposed US carrier polling schedule uses `America/New_York` at 07:15 and 19:15; it has not been verified. The exact source contracts and target-org behavior must be verified. Salesforce controls buyer visibility of its Shipment record; carrier sites control their own links.

Read the [delivery story](story/user-story.md) and [research notes](research/design-notes.md). Keep project-specific originals and their mapping in an approved access-controlled location outside the repository. Ignored local files are only an accidental-add safeguard, not secure storage; never commit real secrets.

AI executors: read [AGENTS.md](AGENTS.md) and the [verification matrix](research/verification-matrix.md) before execution.
