# Shipment tracking integration · Buyer shipment visibility

**Owner** · Pending confirmation · [Execution history](execution-history.md) · [Guide: MIGRATE @ 2a4b77e](https://github.com/aispanda/Reusable-Delivery/blob/2a4b77e1772f4828f595d40c882e7c4f77bc4007/migrate/DELIVERY.md)

**Outcome** · As an authorized business buyer, I want to see my order's shipment carrier, tracking link, status and available delivery dates so I can follow delivery.

**Demo result** · 12 November 2026: an administrator used a read-only Salesforce-to-USPS check; both reported Delivered for an authorized test shipment whose Salesforce status had already been populated manually. No Salesforce update occurred. Buyer journey: NOT RUN. [Evidence at prior story revision](https://github.com/aispanda/salesforce-shipment-tracking-integration/blob/aa28b28115b9476641c2e6abe06d51fbfd7d96c2/story/user-story.md#current-state-and-immediate-next-action).

**Acceptance** · NOT RUN. Independent release verification and human technical and business acceptance remain pending. ERP dispatch, live UPS/FedEx adapters and production deployment are outside the current Salesforce-first POC; historical ERP requirements remain deferred. [Execution history](execution-history.md#review-repair-and-acceptance).

## Scope

Clearly labeled Salesforce test shipments are the source; no ERP is required. USPS is the live carrier target, while UPS and FedEx responses are simulated. Polling at 07:15 and 19:15 Eastern Time is proposed; the ERP dispatch job is deferred. Salesforce controls access to shipment records and links; the carrier controls access to its external page. Environment-specific values and credentials remain outside Git. [Design](../research/technical-design.md) · [Implementation plan](../docs/implementation-plan.md).

The implementation [PR #1](https://github.com/aispanda/salesforce-shipment-tracking-integration/pull/1) was open and draft at head `a09f219df6447c5dec232f2f80a355b86ad4c8cc` when checked on 19 November 2026. Earlier offline test results and the live read-only USPS lookup do not establish automated Salesforce synchronization, an active scheduler, buyer visibility or acceptance.

## Proposed scenario checks

- **Where / who** · Authorized development environment and intended buyer; identity and entry point pending confirmation. Verify Salesforce MCP and CLI access for the current executor before platform work.
- **Start with** · Authorized fictional order with its test shipments and a separate order without shipments; confirm isolation, access and safe reset before running. Identifiers and URLs belong in approved restricted storage.

**Demo sequence** · CHK-01 → CHK-02 → CHK-03

1. **CHK-01** · Operator runs the authorized carrier update against the selected USPS test shipment → the correct Salesforce shipment reflects the verified carrier result. AC-01–03.
2. **CHK-02** · Intended buyer opens the fictional order → each authorized shipment shows its correct carrier, tracking link, status and available dates. AC-06.
3. **CHK-03** · Buyer opens the order without shipments → a truthful empty state appears. AC-06.

| Check ID | Status | Observed result and evidence |
|---|---|---|
| CHK-01 | NOT RUN | Historical read-only comparison did not update Salesforce. |
| CHK-02 | NOT RUN | Intended buyer's rendered shipment view has not been established. |
| CHK-03 | NOT RUN | Intended buyer's empty state has not been established. |
| CHK-04 | NOT RUN | Test cross-account denial and direct access; AC-06–07. |
| CHK-05 | NOT RUN | Verify batch request count, failure and recovery handling; AC-04–05. |
| CHK-06 | NOT RUN | Reproduce the documented setup in a clean environment; AC-08. |

## Acceptance criteria

The following proposed translations and stable IDs are carried verbatim from revision 1.17. Original source comparison, including the deferred external-ID constraint and approved restricted-source retrieval, remains open. See [migration history](../MIGRATION.md).

| Criterion ID | Criterion | Coverage and evidence |
|---|---|---|
| AC-01 | **Foundation:** Verify standard Shipment-to-order linkage, carrier/status handling, safe tracking link and permissions including existing-data impact. For existing Salesforce source records, use their Salesforce identities; evaluate a unique external key if a later source creates or imports shipments. Prove any Order-only fallback. | NOT RUN; see [execution history](execution-history.md#execution-checklist). |
| AC-02 | **Salesforce source:** Given clearly labeled Salesforce test shipments associated with an appropriate demo order, the POC retrieves them as its source, preserves their identity on replay, and isolates incomplete or failed work. No ERP is required for this POC. The earlier requirement for ERP paging, parent resolution and upserts remains deferred for a future integration. | NOT RUN; see [execution history](execution-history.md#execution-checklist). |
| AC-03 | **Carrier:** The tracking job polls USPS through an authorized API for a supplied tracking number, applies approved mappings, and updates changed Salesforce shipments in collections of at most 200 with reliable delivery information when available. UPS and FedEx responses are simulated for this POC until test access is supplied and must be labeled as such. Older transit scans do not overwrite newer Delivered events; corrections need a policy. | NOT RUN; see [execution history](execution-history.md#execution-checklist). |
| AC-04 | **Efficiency:** User requires no more than five Salesforce REST requests per run for up to 800 active shipments: one query plus four update chunks. Pagination, authentication, retries and parent resolution can exceed this; verify actual counts and resolve accounting/exception policy without silently waiving the target. | NOT RUN; see [execution history](execution-history.md#execution-checklist). |
| AC-05 | **Operations:** For any failed SaveResult within HTTP 200, retain record ID, protected payload/reference, status code and message, and send summary to the selected Slack/email/Linear/Sentry destination. Recover retries, uncertain commits and quarantined records; reconcile source and destination. | NOT RUN; see [execution history](execution-history.md#execution-checklist). |
| AC-06 | **Buyer:** Show each correct shipment, carrier, tracking, status and dates to authorized buyers, with safe link and truthful empty/stale states; test cross-account isolation. Prove standard UI supports package-level data before selecting it. | NOT RUN; see [execution history](execution-history.md#execution-checklist). |
| AC-07 | **Security and evidence:** Test least privilege, secrets, multiple packages, replay, out-of-order events, failures and access isolation. Independent verification and human acceptance remain pending. | NOT RUN; see [execution history](execution-history.md#execution-checklist). |
| AC-08 | **Reuse:** Given a clean checkout of a fixed revision, one declared supported MVP environment and authorized environment-specific inputs, another AI/operator can follow the repository entry instructions to install, configure and verify the integration without undocumented help or real client values committed to Git. Retain clean-install evidence, dependency versions, manual steps and limitations. Synthetic checks alone do not prove live integration. NOT RUN. | NOT RUN; see [execution history](execution-history.md#execution-checklist). |

## Material blockers

**S-04p.4a · Guarded writes pending**
- **Goal** · Safely update only the intended shipment without overwriting a newer change.
- **Blocker** · Earlier conditional-read results did not prove an atomic update guard; live workflow writes remain disabled.
- **Current fix** · Proposed: lock and compare the shipment in one Salesforce transaction; reject stale snapshots. Verify competing writes before enabling updates.
- **Documentation** · [Salesforce locking statements](https://developer.salesforce.com/docs/platform/apex-dev/references/apex-dev/langcon-apex-locking-statements.html) · [Guard design, draft implementation](https://github.com/aispanda/salesforce-shipment-tracking-integration/blob/a09f219df6447c5dec232f2f80a355b86ad4c8cc/poc/guarded-write-design.md).

A check-only validation compiled the temporary proof and passed 10 Apex tests on 12 November. That did not deploy it or verify competing writes, actual record locking, or worker permissions. The proof compares selected current fields; it cannot detect a change that is reversed before comparison or prevent later unguarded writes. Carrier callouts must occur before the locking transaction.

**S-00w / S-04 · Runtime and worker access pending**
- **Goal** · Run the integration reliably with authorized unattended access.
- **Blocker** · Worker credentials, runtime, operational ownership and recovery policies have not been verified.
- **Current fix** · Confirm the owner and runtime, then verify worker access with a read-only probe.

**S-11 · Buyer verification pending**
- **Goal** · Demonstrate correct shipment details and isolation in the intended buyer storefront.
- **Blocker** · Intended buyer access, package-level rendering and cross-account checks remain unverified.
- **Current fix** · Confirm the fixture and intended buyer, then run CHK-02–04 in the storefront.

**S-01 / S-09 · Migration and portability pending**
- **Goal** · Preserve the source and let an authorized operator reproduce the POC.
- **Blocker** · Complete source comparison, approved restricted retrieval and clean-install evidence remain open.
- **Current fix** · Reconcile source and restricted mapping; retain missing evidence as pending.

## Execution checklist

Existing bounded task IDs, executor assignments, dependencies, results and stop boundaries are retained in the [execution history](execution-history.md#execution-checklist). Current executor model and reasoning: not exposed; no model identity is inferred. Previously completed checks retain their original scope and do not imply overall acceptance.

**Next** · S-04p.4a: verify current Salesforce access, then complete the scoped guarded-write proof on the authorized disposable fixture. Executor: Codex; exact model and reasoning not exposed. [Existing step](execution-history.md#next-step-s-04p4a--research-guarded-writes). Source reconciliation S-01 remains open independently.

## Migration record

On 19 November 2026 the story was reformatted from revision 1.17 at repository commit `aa28b28115b9476641c2e6abe06d51fbfd7d96c2`. The previous guide was `9d32dccc738cc544481a6da257c13d438115f122`; this revision selects `2a4b77e1772f4828f595d40c882e7c4f77bc4007`. New guide checks include a concise demo sequence, criterion coverage and status, bounded blockers and a tracked Files index. Existing criteria, task IDs and historical evidence are retained; buyer verification, source preservation and role-dependent checks remain open. The complete pre-format record is [execution-history.md](execution-history.md), and its immutable original is [here](https://github.com/aispanda/salesforce-shipment-tracking-integration/blob/aa28b28115b9476641c2e6abe06d51fbfd7d96c2/story/user-story.md). ClickUp synchronization is pending; this change does not claim a source cutover or migration acceptance.

## Files

- [user-story.md](user-story.md) — Outcome, criteria and current blockers.
- [execution-history.md](execution-history.md) — Preserved tasks, evidence and prior decisions.
