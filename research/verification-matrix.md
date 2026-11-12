# POC verification matrix

This matrix defines future tests; all are NOT RUN. Use synthetic fixtures, an approved sandbox and authorized test identities. Record input, expected and actual result, timestamp, executor/tool version and durable evidence. Treat model opinions as review, not test evidence.

| Check | Input / condition | Expected outcome |
| --- | --- | --- |
| Replay | Same package and source revision processed twice | One Salesforce shipment for the stable key. |
| Multiple packages | One order, two package IDs, different statuses | Both packages are represented separately. |
| Parent matching | Zero or multiple eligible matches | No guessed parent; record is retained for repair. |
| Partial results | One success and one failure in a successful HTTP response | Persist success, retain and alert on the failure. |
| Timeout | Write may have committed before response loss | Reconcile or safely replay without duplication. |
| Older event | Older transit scan after newer Delivered | Do not overwrite with stale data; retain auditable evidence. |
| Correction | Valid later carrier correction | Apply only under the approved correction policy, otherwise quarantine. |
| Carrier outage | Provider unavailable | Preserve last verified event and flag stale data; retry per policy. |
| Buyer isolation | Two buyer accounts and direct access attempt | Each sees only authorized records. |
| Empty and multiple | No shipment; two packages with different states | Display truthful empty state and each correct package state. |
| Schedule | Eastern schedule, DST, overlap or missed run | Run according to approved policy; no simultaneous unsafe writers. |
| Request target | 800 active shipments, then pagination/retry | Measure Salesforce requests; record any overrun and unresolved acceptance decision. |
| Configuration | Clean checkout with synthetic configuration | No client-specific URLs, credentials or real data are committed; setup instructions identify required local values. |

The actual middleware, source and carrier contracts, access model, supported UI, alert destination, retry and correction policy must be established before dependent tests can pass.
