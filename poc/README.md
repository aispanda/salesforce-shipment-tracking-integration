# Shipment tracking — local POC core

This is a development POC, not a complete Salesforce integration. It includes experimental USPS Tracking 3.2 and Salesforce Shipment REST clients and a narrow Delivered-only workflow in addition to the synthetic core. No scheduler, storefront or alerts are included. Keep credentials and actual shipment data in restricted local configuration, never in Git.

Requires Python 3.11 or later; uses only the Python standard library. From this directory:

```sh
python3 -m unittest discover -s tests -v
```

The prototype provides source-scoped stable keys, a local SQLite work ledger, offline source adapter contracts, collection chunking and conservative ordering of already-normalized carrier events. The paged synthetic adapter stages each page, its checkpoint and seen cursor history in one SQLite transaction, resumes an unfinished snapshot after restart, and rejects a stale local writer or a repeated cursor across bounded runs. `stage_pages` returns whether the synthetic snapshot has reached its end; `max_pages` limits a run. Each source ID must uniquely identify a synthetic stream. For a checkpoint created by an older version, only the current cursor can be seeded; earlier cursor history is unavailable, so earlier cycles cannot be detected retroactively. A completed snapshot cannot yet be restarted or incrementally polled; recurring windows, ERP cursor semantics, multi-process/multi-host coordination and cursor-history retention need a real design. See [the middleware decision](architecture-decision.md). The sample event statuses are illustrative, not approved carrier mappings. SQLite here is a single-host POC storage choice; concurrency, retention, encryption and production suitability have not been established.

Both synthetic ingest paths require an explicit source ID and scope their package keys consistently. The unpaged path commits each record independently; replay is idempotent but an error can leave earlier records staged. A failure can be recorded while work is pending, but cannot reopen a completed item. Repeated completion is idempotent; an explicit recovery/reopen operation is not implemented. Equal-time carrier events retain the prior event in this prototype, including conflicting statuses; an approved conflict and correction policy is still needed before live use.

Before the Salesforce-first integration can run, connect the existing middleware to Salesforce, establish carrier mappings, choose recovery and alert policies, and validate buyer isolation. An ERP interface is a deferred extension. The five-request goal is unverified: chunking does not account for reads, authentication, pagination or retries. No end-to-end acceptance criterion is claimed as passed.

The USPS client obtains an OAuth token and posts up to 35 distinct tracking numbers per request. It rejects redirects and responses that do not match the requested numbers. It returns carrier data without applying a Salesforce status mapping or writing any Salesforce records. One live USPS request was verified; test-environment behavior, partial errors, production controls, mappings and automated synchronization need further validation. ERP is deferred for the Salesforce-first POC.

The Salesforce client accepts a separately supplied instance URL and token and exposes bounded reads by explicit Shipment IDs and status updates of up to 200 records. It follows only same-origin query locators and reports individual write outcomes without error messages. It has only synthetic tests, has not been run against a Salesforce org, and does not resolve concurrent changes or ambiguous writes. Do not use it to update real records until authorization, field ownership, ordering, reconciliation and the end-to-end workflow are verified.

`sync_delivered` joins the two clients for explicitly supplied test Shipment IDs. It only plans transitions to Delivered for eligible USPS records; unsupported and unknown statuses are skipped. Workflow writes are disabled until concurrency protection is implemented and verified. The workflow has synthetic tests but no live Salesforce verification, durable reconciliation or recurring schedule. UPS and FedEx fixtures can be selected through an explicit simulation configuration; simulated plans are returned separately from live plans.


## Offline carrier and polling examples

`shipment_poc.simulation.SimulatedCarrier` returns only explicitly supplied UPS or FedEx fixture statuses, labels every response `simulated: true`, and rejects missing fixtures. These are illustrative normalized values, not carrier API schemas or approved mappings, and are used by the planning workflow only when an explicit simulation configuration is supplied. That branch does not call the live USPS client and returns labeled `simulated_plans` separately from `planned`. No carrier is contacted. Fixture selection is source-scoped, but this is not an authorization boundary: callers must independently scope shipment records and access.

`shipment_poc.simulation.polling_windows` calculates the proposed 07:15 and 19:15 America/New_York polling times for a calendar date and returns UTC instants. It requires IANA time-zone data accessible to Python (on systems without it, install the `tzdata` package). It does not schedule or run anything. Missed-run behavior, overlap, readiness and deployment remain undecided and untested.

Run the fully local example from `poc/`:

```sh
python3 -m shipment_poc.simulate_run --simulate --day 2026-11-01
```

The command uses hard-coded synthetic shipment records and fixtures and prints the calculated UTC windows, labeled simulated plans, and zero writes. It makes no network requests. It does not start a scheduler; real scheduling, missed-run behavior, retries, and multi-run coordination still need a design and authorization. Do not treat fixture values as carrier status mappings.

The workflow simulation configuration requires `mode: simulation`, a selected `source`, and a `sources` map containing that source's UPS/FedEx fixtures. A missing source, carrier fixture or tracking fixture fails instead of falling back to live APIs. The Salesforce reader passed to the workflow can still perform reads; the example passes an in-memory reader. Access isolation for real readers and data is unverified. Applying changes is disabled for both paths.

### Guarded-write proof still required

The smallest useful sandbox proof needs explicitly authorized, clearly labeled disposable Shipment records and a test identity with only the required read/update access; keep their IDs and environment values outside Git. Confirm the conditional header actually reaches the target API, then read a fixture, change it with a separate authorized writer, and attempt an update using the stale condition. Observe whether the stale update is rejected and the intervening change preserved. Repeat with unchanged data, rapid same-second changes and failure/rollback cases; verify per-record outcomes, partial failure and the chosen batch/request budget. A simple rejected stale write alone cannot establish strong concurrency safety, especially because Salesforce documents timestamp validation as weak and other writers may not cooperate. Reconcile all writer behavior and uncertainty before enabling writes. An Apex/Graph design, if selected, needs its own permissions, deployment and test evidence; unattended worker authentication is a separate unresolved gate. No such update proof has been run.

## Read-only developer check

This optional check uses an authenticated Salesforce CLI session as the developer's identity, reads one explicitly configured USPS test Shipment, asks USPS for its current status, and compares the two. It makes no Salesforce writes. It is a development verification aid, not an unattended worker or a buyer-access test. Obtain authorization for the org, fixture and carrier query before running it.

1. Install Python 3.11+ and Salesforce CLI; authenticate the CLI to the intended development org under an appropriate user. Verify the org and test record access before proceeding.
2. Outside the repository, create a private USPS credentials JSON with `consumer_key` and `consumer_secret` values from the authorized USPS app. On POSIX systems restrict the file to its owner (`chmod 600`). Never commit it or print its contents.
3. Copy `dev-check.example.json` to a private path outside the repository. Set the Salesforce CLI executable, authenticated org alias, approved USPS test Shipment ID and private USPS credentials path. If `sf` is not on your PATH, configure its actual executable path locally. Keep the configuration out of Git.
4. From `poc/`, run `python3 -m shipment_poc.dev_check --config /path/to/private/dev-check.json`. The output reports Salesforce and USPS status, whether they match, and `writes: 0`. A match does not prove that this code performed an update or that buyers can see the shipment.

The check contacts the USPS production API and uses the permissions of the authenticated CLI user. Dedicated worker OAuth, unattended operation, status mapping, guarded writes, recovery, and clean deployment into an empty org remain unverified.
