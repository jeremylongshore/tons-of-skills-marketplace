# Cost Checks and Explicit-Input Estimation

## Read the Actual Billing Surface

Use the current project's billing/usage dashboard and approved SQL catalog queries
for database size. A bucket COUNT is not stored bytes; a Data API RPC named
`get_db_size` does not exist unless your application explicitly defines and protects
it. Do not create an unreviewed privileged RPC or export service-role credentials
merely to generate a cost report. Inventory object size through approved bounded
pagination when needed, without printing private object names or contents.

[Current pricing](https://supabase.com/pricing) and
[compute usage](https://supabase.com/docs/guides/platform/manage-your-usage/compute)
are mutable. Capture source/date, currency, units, billing interval and applicable
organization-level credits. Separate compute active hours from usage included with
a plan; do not apply one shared credit to every project independently.

## Calculator With Caller-Supplied Rates and Units

This arithmetic helper supplies NO Supabase plan prices, universal allowances or
pricing API. Each line's quantity and included quantity must be measured in the
SAME named unit for the SAME billing interval; `pricePerUnit` uses the supplied
currency per that unit (for example per invocation, not per million invocations
unless quantities are also expressed in millions). Fixed fees must include all
intended fees; this result covers only the input lines, not the full invoice.

```typescript
export type UsageLine = {
  name: string;
  unit: string;
  quantity: number;
  included: number;
  pricePerUnit: number;
};

export function estimateProvidedCosts(input: {
  currency: string;
  interval: string;
  rateSource: string;
  fixedFees: number;
  credit: number;
  lines: UsageLine[];
}) {
  if (
    !/^[A-Z]{3}$/.test(input.currency) ||
    typeof input.interval !== 'string' ||
    !input.interval.trim() ||
    typeof input.rateSource !== 'string' ||
    !input.rateSource.trim() ||
    !Array.isArray(input.lines) ||
    input.lines.length > 100
  )
    throw new Error('Invalid scope');
  const finiteNonnegative = (n: number) => typeof n === 'number' && Number.isFinite(n) && n >= 0;
  if (!finiteNonnegative(input.fixedFees) || !finiteNonnegative(input.credit)) {
    throw new Error('Invalid fees/credit');
  }
  const names = new Set<string>();
  const lines = input.lines.map((line) => {
    if (
      typeof line.name !== 'string' ||
      !line.name ||
      names.has(line.name) ||
      typeof line.unit !== 'string' ||
      !line.unit ||
      ![line.quantity, line.included, line.pricePerUnit].every(finiteNonnegative)
    ) {
      throw new Error('Invalid line');
    }
    names.add(line.name);
    const charge = Math.max(0, line.quantity - line.included) * line.pricePerUnit;
    if (!Number.isFinite(charge)) throw new Error('Charge overflow');
    return { name: line.name, unit: line.unit, charge };
  });
  const beforeCredit = input.fixedFees + lines.reduce((sum, line) => sum + line.charge, 0);
  if (!Number.isFinite(beforeCredit)) throw new Error('Total overflow');
  return {
    currency: input.currency,
    interval: input.interval,
    rateSource: input.rateSource,
    lines,
    beforeCredit,
    appliedCredit: Math.min(input.credit, beforeCredit),
    estimatedInputScopeTotal: Math.max(0, beforeCredit - input.credit),
  };
}
```

Only pass a credit to this helper after allocating it to the appropriate eligible
input scope. For example, a compute credit must not accidentally discount unrelated
storage/egress: calculate the eligible compute scope separately, then combine its
post-credit result with other charges. Account for tax, discounts, tiered rates,
region-specific charges, minimums and other invoice adjustments separately. Floating
point arithmetic is illustrative, not accounting-grade decimal rounding.

For local tests, use explicitly synthetic rates and quantities. A passing arithmetic
test is not evidence that the supplied rates are current or that the estimate equals
an invoice. Keep provider credentials, customer identifiers and invoice documents
out of public fixtures and stdout.
