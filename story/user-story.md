# Shipment tracking integration — delivery story

**Migration guide:** [DELIVERY.md](https://github.com/aispanda/Reusable-Delivery/blob/4d0155830d0adf0cc214a466dbfa7fb22af1a096/DELIVERY.md), commit `4d0155830d0adf0cc214a466dbfa7fb22af1a096`, route MIGRATE. Migration remains incomplete; see [migration record](../MIGRATION.md).

**Revision:** 0.3, requirements and reusable-MVP execution plan. **Status:** documentation in progress; implementation, acceptance and independent verification NOT RUN. **Accountable human:** Pending. **Source template:** AI delivery story Markdown v1.3 and Field Guide v1 with operational addition v1.1; project-specific links and identifiers remain outside Git; an approved retrievable restricted index and access owner are Pending. Access to the original online template must be verified by the project coordinator. **Origin:** originating project conversation and current ClickUp story, referenced in local context.

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
- **AC-08 Reuse:** Given a clean checkout of a fixed revision, one declared supported MVP environment and authorized environment-specific inputs, another AI/operator can follow the repository entry instructions to install, configure and verify the integration without undocumented help or real client values committed to Git. Retain clean-install evidence, dependency versions, manual steps and limitations. Synthetic checks alone do not prove live integration. NOT RUN.

AC-01–07 above preserve the wording captured from the existing ClickUp description; AC-08 expands its later proposed addition into the reusable-MVP outcome explicitly requested by the user. The earlier, longer 0.1 story contains additional details; see the [comparison](../MIGRATION.md#additional-original-story-comparison). Those details remain applicable. An independent source-to-destination comparison remains pending, including intervening edits and the full restricted source history.

## Solution and assignments

The proposed design is documented in [technical design](../research/technical-design.md) and [implementation plan](../docs/implementation-plan.md). Project-specific values remain outside Git. The tracking URL resides on the shipment record subject to target-org field and rendering validation. Salesforce governs record visibility; carrier sites govern their external links. The five-request target is not proven and is not waived. Human product, integration, security and acceptance owners: Pending. Planned LLM executor: Codex desktop using `gpt-6-astra`, medium reasoning, when available and assigned; actual model and identity source must be recorded for each run. This planning session's precise model identity is unknown. Deterministic workflows, versions and operators are Pending selection. Jev is a decision model, not assumed to be an LLM.

## Execution checklist

Target: one supported reproducible MVP setup path for the agreed shipment-tracking scope, not a universal installer. Success in the original environment alone does not establish reuse.

**Executor convention:** Astra means Codex desktop with planned exact model `gpt-6-astra`, medium reasoning. Record actual model and metadata source per attempt; no silent substitution. Each row has one executor type. Named humans and automation runner/version/operator remain Pending until explicitly assigned; missing assignment blocks dispatch. Independent checking uses a fresh executor/session separate from the maker.

**Bounded loop:** refresh evidence → select one eligible row → expand its immediate contract → execute → verify → record → recompute. Before dispatch record exact input revisions and documentation sections, output paths, named verifier/operator, authorized effects, proportionate time/cost/retry limits, and recovery/resume condition. Preserve completed evidence; do not restart completed work merely because tasks were split. Stop dependent work on missing inputs/access/authority while continuing independent authorized work. All added rows are Pending / NOT RUN; planned outputs are not existing artifacts.

Inputs: [technical design](../research/technical-design.md), [design notes](../research/design-notes.md), [implementation plan](../docs/implementation-plan.md), [verification matrix](../research/verification-matrix.md), [migration record](../MIGRATION.md), [configuration example](../.env.example), and [repository entry](../README.md). Each platform/API claim needs an official documentation link, relevant section/version and verified applicability. Repair missing or damaged source references before dependent implementation; public technical constants are not private instance values.

Historical records retained:
| ID | State | Executor / output | Dependencies |
|---|---|---|---|
| S-01 | In progress | AI: Codex desktop; actual model unknown. Reconcile source and sanitized story/design. | Full source, restricted snapshot and comparison. |
| S-02 | Complete (prior draft branch only; new repository initial documentation published and verified; full migration Pending) | LLM: Codex desktop, planned `gpt-6-astra`, medium reasoning; actual model recorded at execution. Publish sanitized documentation in reviewable branch. | Initial source reconciliation, content and secret review, repository access. Full S-01 reconciliation remains in progress. |
| S-03 | Complete for reviewed revision; affected recheck Pending if needed | AI decision model `jev-1.14.0` (API metadata): reviewed sanitized shipment commit `a2c1507cb6a666157f5559fa3080bd916569eed9`. | Exact reviewed inputs and permitted transmission. |

Remaining bounded tasks:
| ID | State | One executor | Action / output | Dependencies / documentation / criteria | Completion check / stop condition |
|---|---|---|---|---|---|
| S-04 | Pending | Human: integration owner, person Pending | Select one supported MVP runtime/environment; resolve ERP/carrier contracts and scheduling/recovery policies. | Design and actual authorized contracts; AC-01–07 | Record decisions, official sources and remaining assumptions; stop dependent work without owner/contract evidence. |
| S-04b | Pending | AI: Astra | Verify prerequisites and define environment/configuration contract. | S-04; design, official API/metadata documentation, authorized read-only discovery; AC-01/07/08 | Record supported versions, access, schema and required inputs with evidence; stop if discovery access is missing. |
| S-04c | Pending | AI: Astra | Define build/test layout, pin dependencies and select deterministic runner/version and accountable operator. | S-04 runtime; implementation plan and verification matrix; AC-07/08 | Reproducible dependency specification and synthetic bootstrap checks; stop before unapproved installation effects or spending. |
| S-04a.1 | Pending | AI: Astra | Implement configurable adapters and input validation. | S-04b/c; .env.example and verified API contracts; AC-01–03/07/08 | Synthetic contract/configuration checks pass; examples contain placeholders only; stop on unresolved contracts. |
| S-04a.2 | Pending | AI: Astra | Implement Job A: paging, durable cursor, parent resolution and idempotent upsert. | S-04a.1; design Job A/recovery; AC-02/05 | Replay, ambiguous-parent, partial and uncertain-write synthetic checks; stop on unresolved key semantics and inspect partial effects before retry. |
| S-04a.3 | Pending | AI: Astra | Implement Job B: polling, status precedence and changed-only updates. | S-04a.1 and approved carrier mappings; design Job B; AC-03/04 | Unknown/stale/corrected events and no-change checks; record request counts; stop on unresolved precedence or budget exceptions rather than waive AC-04. |
| S-04a.4 | Pending | AI: Astra | Implement scheduling/readiness, bounded retries, reconciliation and safe alerting. | S-04a.2/3; S-04 decisions; design operations; AC-02–05/07 | Controlled overlap/outage/restart checks match policy; stop before live schedules or notifications without authority. |
| S-05 | Pending | Automation: runner/version and accountable operator selected in S-04c | Run synthetic regression suite. | S-04a.1–4; approved fixtures/identities; verification matrix; AC-01–07 | Per-criterion expected/actual evidence including applicable API response codes; failures mean Rework, not completion; synthetic success is not live-platform proof. |
| S-07 | Pending | AI: Astra | Package one setup path: install/configure/verify, troubleshooting and rollback/cleanup instructions. | S-04b/c, implemented components, S-05 findings; README/build plan; AC-08 | One repo entry gives exact commands, versions, required inputs, secret retrieval, expected results and limits; extend existing docs as useful; stop unsupported success claims. |
| S-08 | Pending | Human: environment/access owner, person Pending | Provide an isolated representative validation environment and approved access. | S-04 environment contract; S-07 instructions; AC-06–08 | Verify intended executor access, fixture ownership, permitted effects/cost and cleanup; stop if unavailable. |
| S-09 | Pending | AI: Astra, fresh execution session | Install/configure from a clean checkout using only repository instructions and declared inputs. | S-05/07/08; fixed candidate commit; AC-08 | Capture versions, commands, results and assistance. Undocumented required help fails reproducibility and returns S-07 to Rework; no production effects or secret-bearing logs. |
| S-10 | Pending | Automation: recorded verification runner/version and accountable operator | Run representative environment integration checks. | S-09; approved sandbox fixtures/identities and verification matrix; AC-01–07 | Record API behavior, replay/failure, request counts and account isolation; manual UI checks stay for S-11. Stop unauthorized data/effects; label mocks explicitly. |
| S-11 | Pending | Human: QA verifier, person Pending | Verify buyer experience, mobile behavior and documented recovery/cleanup. | S-10/07; buyer scenarios and original draft DoD | Retain multiple-package/empty/stale/mobile/access/recovery observations; stop on unavailable fixtures or unsafe cleanup; no claimed unrun checks. |
| S-06 | Pending | AI: Astra, fresh independent checker session separate from maker | Audit release evidence and clean-install reproducibility. | S-09–11; frozen criteria, source mapping and exact candidate; AC-01–08 | Findings trace to actual evidence; missing/failed checks stay open; affected repairs rechecked. Cannot grant human acceptance or certify unseen sources. |
| S-12 | Pending | Human: technical acceptance owner, person Pending | Review supported setup, contracts, recovery and residual technical risks. | S-06; original draft DoD and evidence | Record explicit scoped decision; stop awaiting named owner/decision, never infer approval. |
| S-13 | Pending | Human: business acceptance owner, person Pending | Review buyer outcome and MVP limitations. | S-06/11; original draft DoD and evidence | Record explicit scoped decision separately from technical acceptance; stop awaiting named owner/decision. |
| S-14 | Pending | AI: Astra | Prepare versioned reusable release and final handoff. | S-06/12/13; accepted criteria/dispositions, publication authority and privacy check | Entry, tested revision, setup/configuration/verification/recovery docs and evidence agree; read back published links; stop unresolved required checks. No production deployment implied. |

S-04a was one broad implementation row; its work is now S-04a.1–4. S-05 depends on implementation, not just the human decisions. S-06 remains independent verification; S-12/13 separate human acceptance. The numbering preserves earlier IDs; dependencies, not numerical order, determine eligibility.

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

Revision 0.3: user requested a reusable MVP asset with explicit bounded shipment-story tasks. AC-08 now requires a verified clean-environment setup path; all acceptance checks remain NOT RUN. AC-01–07 wording is unchanged. This plan does not authorize live API writes, installation costs, notifications or production deployment. Recheck reuse, dependencies, handoff and acceptance evidence for this revision. The general delivery template is unchanged.
