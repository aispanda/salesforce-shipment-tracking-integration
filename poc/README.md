# Shipment tracking — local POC core

This is a synthetic development starting point, not a working ERP, carrier or Salesforce integration. No network jobs, scheduler, Salesforce updates, storefront or alerts are included. Do not use real shipment data in this local prototype.

Requires Python 3.11 or later; uses only the Python standard library. From this directory:

```sh
python3 -m unittest discover -s tests -v
```

The prototype provides source-scoped stable keys, a local SQLite work ledger, offline source adapter contracts, collection chunking and conservative ordering of already-normalized carrier events. The paged synthetic adapter stages each page and its checkpoint in one SQLite transaction, resumes an unfinished snapshot after restart, and rejects a stale local writer or a repeated cursor within one bounded run. `stage_pages` returns whether the synthetic snapshot has reached its end; `max_pages` limits a run. Each source ID must uniquely identify a synthetic stream. A completed snapshot cannot yet be restarted or incrementally polled; recurring windows, ERP cursor semantics, multi-process/multi-host coordination and cross-run cursor cycles need a real design. See [the middleware decision](architecture-decision.md). The sample event statuses are illustrative, not approved carrier mappings. SQLite here is a single-host POC storage choice; concurrency, retention, encryption and production suitability have not been established.

Both synthetic ingest paths require an explicit source ID and scope their package keys consistently. The unpaged path commits each record independently; replay is idempotent but an error can leave earlier records staged. A failure can be recorded while work is pending, but cannot reopen a completed item. Repeated completion is idempotent; an explicit recovery/reopen operation is not implemented. Equal-time carrier events retain the prior event in this prototype, including conflicting statuses; an approved conflict and correction policy is still needed before live use.

Before a real integration can run, identify the existing middleware and ERP interface, verify Salesforce metadata and access, establish carrier contracts and mappings, choose recovery and alert policies, and validate buyer isolation. The five-request goal is unverified: chunking does not account for reads, authentication, pagination or retries. No acceptance criterion is claimed as passed.
