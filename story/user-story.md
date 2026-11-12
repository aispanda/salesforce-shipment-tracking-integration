# Shipment tracking integration — delivery story

**Migration guide:** [DELIVERY.md](https://github.com/aispanda/Reusable-Delivery/blob/4d0155830d0adf0cc214a466dbfa7fb22af1a096/DELIVERY.md), commit `4d0155830d0adf0cc214a466dbfa7fb22af1a096`, route MIGRATE. Migration remains incomplete; see [migration record](../MIGRATION.md).

**Revision:** 0.2, requirements draft. **Status:** documentation in progress; implementation, acceptance and independent verification NOT RUN. **Accountable human:** Pending. **Source template:** AI delivery story Markdown v1.3 and Field Guide v1 with operational addition v1.1; project-specific links and identifiers remain outside Git; an approved retrievable restricted index and access owner are Pending. Access to the original online template must be verified by the project coordinator. **Origin:** originating project conversation and current ClickUp story, referenced in local context.

## Current state and immediate next action

The sanitized documentation is published in a public repository; this is not a working integration. Target metadata, buyer sharing, storefront behavior and carrier/ERP contracts remain unverified. Jev reviewed the sanitized package at shipment commit `a2c1507cb6a666157f5559fa3080bd916569eed9`; see [review record](https://github.com/aispanda/Reusable-Delivery/blob/4d0155830d0adf0cc214a466dbfa7fb22af1a096/VALIDATION.md#jev-review-of-guide-and-shipment-pilot). Its judgments do not establish source completeness or runtime behavior. Next: reconcile available source documents and criteria, then secure a retrievable restricted snapshot before ClickUp cutover. Executor: Codex desktop, actual exact model identifier unknown; accountable human Pending. Independent verification NOT RUN; human acceptance Pending.

## Outcome, scope and context

As an authorized business buyer, I want to see my order's shipment carrier, tracking link, status and available delivery dates so I can follow delivery. Existing self-hosted middleware initiates outbound requests to the fulfillment source, carriers and Salesforce; no inbound public webhook is needed. The initial US carriers are UPS, FedEx and USPS. Dispatch processing runs at 07:00 and 19:00 Eastern Time; carrier polling at 07:15 and 19:15 Eastern Time. The source system retains fulfillment ownership. FulfillmentOrder and ShipmentItem creation are deferred, subject to proving the required behavior is possible. A project supplies its own environment configuration and credentials outside Git.

## Perspectives

Product owner: Applicable — confirm buyer outcome and scope. Business analyst: Applicable — identity and mapping. UI/UX: Applicable — truthful package, empty and stale states. Technical: Applicable — supported APIs, configuration, reliability and recovery. QA: Applicable — verify each criterion and account isolation. Human reader: product and technical owners need decisions and evidence. AI executor: load this story, design and local authorized context; do not assume unverified platform behavior, use real data in fixtures, or claim completion without evidence.

## Acceptance criteria

The following are proposed translations of the source requirements; stable IDs are preserved. All are **NOT RUN**.

- **AC-01 Foundation:** Verify supported Shipment-to-order linkage, requested provider/status picklists, unique case-insensitive External_Tracking_Id__c Text(255), safe tracking link and permissions including existing-data impact. Prove any Order-only fallback.
- **AC-02 Dispatch:** Job A pages and stages ERP changes, resolves exactly one parent, and upserts in collections of at most 200; replay never duplicates packages, and failures remain recoverable.
- **AC-03 Carrier:** Job B polls approved carriers, applies approved mappings, updates changed shipments in collections of at most 200 and records reliable delivery time. Older transit scans do not overwrite newer Delivered events; corrections need a policy.
- **AC-04 Efficiency:** User requires no more than five Salesforce REST requests per run for up to 800 active shipments: one query plus four update chunks. Pagination, authentication, retries and parent resolution can exceed this; verify actual counts and resolve accounting/exception policy without silently waiving the target.
- **AC-05 Operations:** For any failed SaveResult within HTTP 200, retain record ID, protected payload/reference, status code and message, and send summary to the selected Slack/email/Linear/Sentry destination. Recover retries, uncertain commits and quarantined records; reconcile source and destination.
- **AC-06 Buyer:** Show each correct shipment, carrier, tracking, status and dates to authorized buyers, with safe link and truthful empty/stale states; test cross-account isolation. Prove standard UI supports package-level data before selecting it.
- **AC-07 Security and evidence:** Test least privilege, secrets, multiple packages, replay, out-of-order events, failures and access isolation. Independent verification and human acceptance remain pending.
- **AC-08 Reuse (proposed):** Given a clean checkout and permitted synthetic configuration, when an operator follows the documented setup, then the configurable jobs can be set up without real environment values in committed files; verify configuration and staged content. NOT RUN.

AC-01–07 above preserve the wording captured from the existing ClickUp description; AC-08 preserves its later proposed addition. The earlier, longer 0.1 story contains additional details; see the [comparison](../MIGRATION.md#additional-original-story-comparison). Those details remain applicable. An independent source-to-destination comparison remains pending, including intervening edits and the full restricted source history.

## Solution and assignments

The proposed design is documented in [technical design](../research/technical-design.md) and [implementation plan](../docs/implementation-plan.md). Project-specific values remain outside Git. The tracking URL resides on the shipment record subject to target-org field and rendering validation. Salesforce governs record visibility; carrier sites govern their external links. The five-request target is not proven and is not waived. Human product, integration, security and acceptance owners: Pending. Planned LLM executor: Codex desktop using `gpt-6-astra`, medium reasoning, when available and assigned; actual model and identity source must be recorded for each run. This planning session's precise model identity is unknown. Deterministic workflows, versions and operators are Pending selection. Jev is a decision model, not assumed to be an LLM.

## Execution checklist

| ID | State | Executor / output | Dependencies |
|---|---|---|---|
| S-01 | In progress | AI: Codex desktop; actual model unknown. Reconcile source and sanitized story/design. | Full source, restricted snapshot and comparison. |
| S-02 | Complete (prior draft branch only; new repository initial documentation published and verified; full migration Pending) | LLM: Codex desktop, planned `gpt-6-astra`, medium reasoning; actual model recorded at execution. Publish sanitized documentation in reviewable branch. | S-01, content and secret review, repository access. |
| S-03 | Complete for reviewed revision; affected recheck Pending if needed | AI decision model `jev-1.14.0` (API metadata): reviewed sanitized shipment commit `a2c1507cb6a666157f5559fa3080bd916569eed9`. | Exact reviewed inputs and permitted transmission. |
| S-04 | Pending | Human: integration owner Pending. Decide source and carrier contracts and operational policies. | Interfaces, sandbox and authorized credentials. |
| S-04a | Pending | AI: Codex desktop, planned `gpt-6-astra`, medium reasoning; actual identity recorded at execution. Implement bounded jobs. | S-04, explicit implementation authority and inputs. |
| S-05 | Pending | Automation: selected test runner/version Pending with accountable operator Pending. Run synthetic failure and access tests. | S-04 and fixtures. |
| S-06 | Pending | Fresh independent human or AI checker Pending; human acceptance owner Pending. Verify actual results and acceptance evidence. | S-05. |

### Immediate step contract — S-01

**Action and expected result:** Compare current source requirements and attached design with the sanitized documents; preserve stable criteria, mark assumptions, and isolate project-specific context. **Executor:** Codex desktop LLM, actual model unknown; human accountable owner Pending. **Inputs:** current ClickUp story and template v1.3, local backlog and technical design; check freshness. **Output:** this story and linked design, sanitized and versioned. **Verification:** review scope, schedule, carrier list, status and forbidden content; inspect diff. **Boundary:** no Salesforce writes, live carrier calls or claims of implementation. **Retry/recovery:** inspect partial branch changes before retry; stop at inaccessible or conflicting evidence. **Actual result:** Initial sanitized reconciliation completed for the prior draft branch. Full source comparison and migration checks remain pending; see the migration record.

## Review, repair and acceptance

Earlier Jev 1.14.0 reviewed selected revision 0.1 text. A later Jev review covered all 18 sanitized guide and shipment files at the revisions linked above; private originals and live systems were not supplied. It did not establish source completeness, portable retrieval or implementation. Preserve the earlier rejected transmission attempt as historical; the later review is a separate authorized execution. Maker's human-reader and AI-execution reviews checked scope, status, bounded steps and separate private context; unresolved deployment decisions remain explicit. Independent checker NOT RUN; human acceptance Pending.

## Impact, authority and recovery

User authorized sanitized documentation in the dedicated repository and ongoing story maintenance; public visibility was authorized and verified on GitHub. No Salesforce configuration, production deployment, actual shipment or customer communication is implied. Inspect branch state and sensitive-data scan before writing. If an operation is uncertain, read the remote state before retrying. Never commit credentials, client names, org URLs or real records; ignored local files must remain outside tracked history.

## Blockers and handoff

Middleware/ERP contracts, carrier credentials and mappings, target-org metadata and buyer access, behavior for missed runs, alert destination, request-budget exceptions and named owners are Pending. A required decision blocks only dependent work. GitHub source is the versioned documentation location; ClickUp retains current status and links. Prior attachments are historical snapshots and must not be silently deleted.

## Evidence, changes and traceability

Revision 0.1 captured the original MVP criteria and focused review. Revision 0.2 incorporates the initial three carriers, Eastern schedule, Salesforce record-based buyer access, and reusable configuration requirement. Source-specific evidence and template links are outside Git; approved portable retrieval and access ownership remain Pending. Material changes require affected reviews to be rerun. Delivery NOT RUN; independent verification NOT RUN; human acceptance Pending.
