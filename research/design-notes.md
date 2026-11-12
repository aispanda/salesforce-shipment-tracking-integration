# Research and design evidence

This is a sanitized synthesis of the MVP backlog, low-level design and earlier component discovery. It is not proof of behavior in any particular org or implementation. Public primary references to consult include Salesforce Shipment object and field references, OrderSummary, sObject Collections upsert/update, OAuth client credentials, Commerce order expressions, and current UPS, FedEx and USPS tracking API documentation. Vendor capabilities and versions require current verification before implementation.

## Observations and limitations

- The standard shipment model includes order relationships and tracking fields; verify exact availability, writability, picklist values, field type, permissions and object support in the target org. A direct Order-only relationship is not established by the research and must be verified.
- A prior Builder inspection showed a standard tracking component using an order-status expression. That observation does not prove that it can display carrier status per package or that a Shipment update changes the displayed progress. Test a supported component with an authorized multi-package fixture.
- The requested external ID is case-insensitive unique Text(255). A stable source package identity is a proposed key; tracking numbers may change or be reused. Confirm identity and legacy data migration before enforcing requiredness.
- Salesforce collection requests can group up to 200 records. A successful HTTP response can include individual failures. The requested budget of five requests for up to 800 records is an ideal one-read/four-update scenario, not a verified universal limit; pagination, retries and lookups complicate it.
- FedEx documentation described up to 30 tracking numbers per tracking request at the time of research. Carrier endpoint, authorization, contract, current limits and code mapping require verification for all three providers. Do not treat illustrative carrier status codes as universally equivalent.
- Buyer access to the Salesforce record and a carrier-hosted URL are distinct. Test account isolation in the actual storefront; do not assume an external link is access-controlled by Salesforce.

## Evidence and review scope

Source-specific observation links and identifiers remain in the original restricted sources; an approved retrievable index and access owner are Pending. An ignored local pointer alone is not secure storage. The prior decision-model review covered selected story text only, not live records or implementation. The earlier review predates later requirements; a separate review of the sanitized shipment package at commit `a2c1507cb6a666157f5559fa3080bd916569eed9` is recorded in the story. It did not inspect private originals or live systems; runtime verification remains NOT RUN. Separate demo and split-fulfillment research are background; they do not establish the POC's implementation or acceptance.
