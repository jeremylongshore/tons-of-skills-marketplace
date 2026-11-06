# Financial interpretation contract

Report supplied billing-backed amounts, telemetry/pricing estimates and contract-dependent scenarios in separate sections. Missing confidence defaults to estimated. A confirmed finding needs a direct supplied amount and a non-empty billing reference reviewed by the owner; the offline script does not retrieve or verify an invoice.

The script accepts amounts over an explicitly selected 30-day window and labels the calendar-month equivalent conversion. It does not claim that a partial export represents a complete month. Numeric values must be finite and non-negative, discounts must be between 0 and 1, and scenario modifiers cannot conflict.

Rows can overlap, so no additive headline or one-setting savings promise is emitted. Keep rates, sample coverage, contract terms, billing attribution and availability assumptions visible. An empty input means no supplied findings, not no cost issue.
