# Framework lenses and evidence questions

These are candidate review topics, not an exhaustive checklist or automatic
applicability determination. Choose the current applicable authority, version,
level, jurisdiction and dates. Distinguish a document's promise, implementation
configuration and evidence that a control actually operated.

## GDPR and related privacy rules

Establish territorial/material scope, processing activity, controller/processor
roles and data flows. Review purpose-specific lawful-basis records, disclosures,
rights handling, processor arrangements, retention, security, breach procedures,
transfers, and conditions for impact assessments and a DPO. Do not assign consent
as the basis for every activity or infer a blanket cookie requirement from GDPR
alone; identify applicable electronic-communications rules separately. EU and UK
regimes need their own current authority. Review role-specific notification duties
rather than applying one deadline to every party.

Primary starting points: [EU GDPR](https://eur-lex.europa.eu/eli/reg/2016/679/oj),
[EDPB guidance](https://www.edpb.europa.eu/our-work-tools/general-guidance/guidelines-recommendations-best-practices_en),
[ICO guidance](https://ico.org.uk/for-organisations/).

## CCPA/CPRA

Determine the entity's actual applicability, roles, data practices and relevant
exceptions. Examine collection notices, rights intake and fulfillment, sale/share
and sensitive-information practices where applicable, preference signals, provider
contracts and retention disclosures. A missing sale/share link is not enough to
conclude noncompliance without the relevant practices and obligations. Do not
hardcode thresholds or infer applicability from a California visitor alone.

Primary starting point: [CPPA FAQ](https://cppa.ca.gov/faq.html) and the linked law
and regulations; informational summaries do not replace the applicable text.

## Accessibility and ADA questions

Specify WCAG version, level and tested pages/states/complete processes. Review
text alternatives, keyboard operation, focus, semantics, labels, errors, contrast,
reflow, captions and applicable criterion exceptions. Decorative images may need
empty alternatives; adding ARIA everywhere is not a conformance method. Inspection
and automated results need appropriate manual/assistive-technology evaluation.
A WCAG sample result is not automatically a determination under the ADA or every
jurisdiction's accessibility law; identify the actual legal/contractual benchmark.

Primary starting point: [W3C evaluation methodology](https://www.w3.org/WAI/test-evaluate/conformance/wcag-em/).

## PCI DSS

Map payment account data flows, integrations, merchant/service-provider roles,
provider responsibilities, assessed environments and the applicable standard.
Ask for the appropriate validation route and evidence from the relevant payment
stakeholders/assessor. Hosted checkout or a processor script does not establish
merchant compliance or automatically determine an SAQ. Examine applicable storage,
logging, access, integration, change and vulnerability-management controls without
requesting actual card numbers or exercising payment flows.

Primary starting point: [PCI SSC PCI DSS](https://www.pcisecuritystandards.org/standards/pci-dss/).

## CAN-SPAM

Establish the message's primary purpose and sender responsibilities. Inspect
representative supplied messages, accurate headers/subjects, advertising
disclosure, valid postal address, opt-out presentation and actual suppression
records. Check the current applicable timing rule against evidence; a link alone
does not prove requests are honored. Distinguish this US regime from separate
consent/list-acquisition duties under other laws; do not invent a blanket CAN-SPAM
ban on every purchased list.

Primary starting point: [FTC business guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business).

## COPPA

Assess the audience, service characteristics, operator knowledge and actual data
collection. A colorful page is not an applicability finding and a product label
alone is not proof of exemption. Verify current rule provisions and effective
compliance dates before evaluating notice, parental consent, parent rights,
retention, security and third-party disclosures. An age gate alone does not prove
compliance; do not collect real children's information to test it.

Primary starting point: [FTC COPPA rule hub](https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa).

## SOC 2 readiness

Establish the actual service/system boundary, commitments, selected Trust Services
Categories, criteria and examination purpose. Request scoped policies, control
owners and operation evidence. For an existing report inspect its type, period,
opinion, exceptions, subservice treatment and complementary user controls rather
than treating the report title as universal coverage. A readiness checklist is
not a SOC 2 report, certification or proof that controls operated effectively.

Primary starting point: [AICPA SOC resources](https://www.aicpa-cima.com/resources/landing/system-and-organization-controls-soc-suite-of-services).
