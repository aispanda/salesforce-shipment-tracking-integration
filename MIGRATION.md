# Migration record — draft

Guide revision: d486dcf684f12fd911c06d2ec2b680d66a4aac3e, route MIGRATE. The guide was read at this single commit. Its prior guide SHA is not applicable: the prior story used the ClickUp Markdown template v1.3 and Field Guide v1, not a commit-pinned delivery guide.

This local package is derived from the prior sanitized draft. The dedicated repository was created after the user confirmed the separate repository request; public visibility was authorized and verified on GitHub. Publication and readback are recorded separately; do not infer completion from repository creation. The existing draft PR and its sources remain unchanged. ClickUp synchronization is pending publication, access-controlled capture of its current full description, and refresh/reconciliation before replacement. Previous attachments remain historical. An ignored local file is not itself approved restricted storage. Access-controlled storage owner and retrieval procedure: Pending.

## Criteria comparison and reconciliation needed

The source ClickUp story contains AC-01–07, plus proposed AC-08, all NOT RUN. The earlier sanitized draft retained IDs and intended scope but was not a verbatim copy. In that earlier draft, AC-01 abbreviated the specified external field name, type and uniqueness constraints; AC-04 omitted the one-query/four-update example; AC-05 summarized record-level error fields and alert options. The local migration draft now restores the wording captured from ClickUp for AC-01–07 and the proposed AC-08. Independent comparison with the full restricted source, including intervening edits, is still required before migration can be considered complete. Proposed AC-08 remains proposed; no criterion has been waived. The five-request budget remains unresolved and unproven.

## Retained scope and history

US carriers UPS, FedEx and USPS; Job A 07:00/19:00 and Job B 07:15/19:15 America/New_York; Salesforce Shipment link and buyer access checks. The separate fictional demo remains outside this MVP. An earlier Jev review covered selected 0.1 material; it is historical, and the later revision has not received that recheck. Documentation exists; implementation, independent verification and acceptance NOT RUN. Prior attachments and source files remain in place.

## Next actions

1. Initial sanitized package published to the private repository; ten files read back byte-for-byte at commit `7ba679820dcdc8b53d302f1aac5c072357576589`. Further revisions require their own readback.
2. Secure and verify an authorized restricted source snapshot and mapping. Compare every source criterion to this draft and reconcile differences; keep exact constraints and label proposals.
3. Refresh concurrent GitHub and ClickUp state, publish only reviewed sanitized content, then read back files, links, privacy and visibility.
4. Refresh and reconcile ClickUp immediately before replacing its description with the two verified GitHub links. Preserve original text and attachments. Recheck affected reviews separately.

This file is a working migration record; it does not claim migration completion, implementation, acceptance, or an exhaustive secret scan.

## Source-to-destination map

| Source or concern | Destination | Preservation status |
|---|---|---|
| Existing task description and source story | [Story](story/user-story.md) | IDs AC-01–07 restored from captured task wording; AC-08 proposed. Full independent comparison and intervening edits Pending. Original remains in ClickUp. |
| Backlog and technical design | [Technical design](research/technical-design.md), [plan](docs/implementation-plan.md) | Sanitized draft retained; complete source-by-source comparison Pending. |
| Research and component discovery | [Research notes](research/design-notes.md) | Sanitized synthesis; primary source references and org-specific observations require verification and restricted provenance. |
| Test plans and earlier review | [Verification matrix](research/verification-matrix.md), story review section | Tests NOT RUN. Earlier focused review retained as historical; revised requirements recheck Pending. Raw reports remain in original sources. |
| Separate demonstration | Story scope and research notes | Distinct post-MVP scope; not evidence of the integration. Original source remains in place. |
| Existing prior draft package | Prior private draft remains unchanged; this package supersedes it only as a migration draft | No deletion or merge performed. |

## Private values and retrieval

Client identity → project-specific organization label; Salesforce instance hostname → `SALESFORCE_LOGIN_URL`; ERP endpoint → `ERP_BASE_URL`; carrier and ERP credentials → keys in [.env.example](.env.example), populated through an approved secrets manager. These are parameter names, not actual values. Source links, field mappings, fixture identifiers and org-specific observations require a restricted source index with its access owner and retrieval procedure; both are Pending. The existing ignored local index is only a pointer to original workspace material and is not verified approved storage. A new laptop cannot yet independently retrieve that context. Never commit the mapping or real values.
