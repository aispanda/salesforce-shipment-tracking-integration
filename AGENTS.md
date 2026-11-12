# Instructions for AI executors

Start with `story/user-story.md`, `research/design-notes.md`, `research/technical-design.md` and `docs/implementation-plan.md`. The repository is a reusable POC design; it is not evidence that any integration has been built or that a target org supports a proposed feature.

Use a bounded loop: refresh current evidence and authority; select one eligible step; record its input, accountable owner and executor, expected output, verification and stop boundary; execute; check the actual result; record evidence and status; choose the next step. Continue independent authorized work when a dependency is blocked. Never treat a successful API call as proof that every record succeeded.

Record each executor as Human, deterministic Automation with tool/workflow and version, or AI with client and exact model/version. Planned implementation executor is GPT-6 Astra with medium reasoning, if available and assigned; report actual identity and its source, and mark unknown when not exposed. Do not claim a human, model, approval, test or implementation that did not occur. Preserve acceptance IDs; do not waive criteria to pass a check.

Keep client names, instance URLs, secrets, tracking data and private identifiers outside Git. Use local ignored configuration or a secret manager. Inspect every diff and scan before committing; never assume ignore rules erase Git history. Do not put real credentials, records or customer data into test fixtures, logs, prompts or example files.

Verify actual Salesforce schema, buyer access, carrier and source contracts, and available middleware before making environment-specific changes. Use synthetic data first. Stop before actions beyond the user's authorization, a destructive operation, or an unresolved prerequisite that could invalidate the work. Keep implementation, independent checking and human acceptance distinct.
