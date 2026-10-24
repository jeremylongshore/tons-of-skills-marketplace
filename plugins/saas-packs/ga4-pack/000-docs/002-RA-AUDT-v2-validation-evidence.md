# GA4 v2 validation evidence

**Date:** 2026-10-24

**Bead:** claude-l99e.10

## Scope and authority

The evaluated operator source is commit
`a338bab4ea70729b98f937f04eba5267adb266c5`. Documentation and generated
publication projections were appended after that source snapshot. The grades
below describe that immutable source, rather than certifying later helper changes.

A subsequent regression test reproduced two receipts with `filters: null`
producing a numeric comparison. The corrected analyzer retains diagnostic
findings and returns `inconclusive` with no deltas until filters are known.
The receipt contract now states this requirement. The new test failed before
the correction. Afterward, system Python ran 58 GA4 cases: 55 passed and three
optional SDK cases were skipped. In the SDK-enabled environment, all 58 passed. This analyzer and reference correction postdates
run 139 and is not covered by its original source-file hash manifest.

Freshie run **139** is published as tag `run-139`, Dolt commit
`mf70vsi6nk1tt23alrbujmq4jungnk7a`. The public API was queried at that immutable revision and
returned the following records:

| Skill | Score | Grade | Errors |
| --- | ---: | --- | ---: |
| `ga4-export-guardian` | 97 | A | 0 |
| `ga4-measurement-verifier` | 95 | A | 0 |
| `ga4-report-forensics` | 92 | A | 0 |

[Query the immutable public GA4 grade records](https://www.dolthub.com/api/v1alpha1/jeremylongshore/freshie-inventory/main?q=SELECT+skill_path%2Cscore%2Cgrade%2Cerror_count+FROM+skill_compliance+AS+OF+%27mf70vsi6nk1tt23alrbujmq4jungnk7a%27+WHERE+run_id%3D139+AND+skill_path+LIKE+%27plugins%2Fsaas-packs%2Fga4-pack%2F%25%27).

The current-run export has 3,491 graded artifacts and SHA-256
`04ede95b460fa54b3f17359cf1bf9e2e87a844875076e599fd743b9748efd829`.
Publication passed the 51-table allowlist, complete-run checks, real
NULL/empty-string/DATETIME/quoting canary, all-table row-count parity,
float checks on six REAL columns and per-row MD5 checks on three JSON columns.
The published delta from run 138.1 is +89,111 rows, zero removals, zero
modifications, zero schema changes and zero grade regressions.

The validator returned exit 1 for existing corpus compliance errors after
successfully writing the new run, rather than exit 2 for a failed write. Skills
have 2,798 errors in both runs 138 and 139; no overlapping skill gained errors.
All three GA4 successors have zero errors. This is not a claim that the whole
repository is error-free or that every artifact is certified.

## Author-reported local execution

The following results are retained local execution evidence, not inferred from
a diff or from the existence of tests. The test source is included in the PR.
SDK-specific cases ran with `google-analytics-data` 0.23.3 and
`google-cloud-bigquery` 3.46.2; npm was 12.0.1 and Node was 22.23.1.

- 57 GA4 cases passed, including real SDK request/response/job serialization
  against synthetic clients, bounds, incomplete evidence and no-live CLI guards.
- A combined run with 18 existing consistency-persistence cases passed all 75.
  Those include three scratch-policy integrations requiring an approved local
  policy checkout. Public runs explicitly skip unavailable optional dependencies
  or private policy; skipped cases must not be reported as passes.
- The three marketplace skill checks had zero errors; Unicode scanning found
  zero blocker, major or minor findings in 26 source files.
- Harness enrollment added exactly three new evaluation contracts and retained
  every existing pin unchanged. The normal harness and commit hooks passed.
- Full canonical generation and the final verification, projection, curated,
  lattice and scorecard checks passed before these post-publication documents.
  They are regenerated again with the published run and evidence document.

The implementation author reports that these checks used synthetic SDK clients
and scratch destinations, and did not invoke live GA4/BigQuery collection, IAM
changes, tracking changes, export setup or paid query execution. This is an
execution report, not a claim that a diff can prove the absence of all activity
outside its scope. Behavioral evaluation specifications are definitions; no
behavioral model-evaluation run is claimed.

## Package and site observations

The retained pre-documentation npm artifact at the evaluated source contains
26 source files, including all three operators, six helpers, three evaluation
contracts and the linked value decision. All five retired slots and six local
interpreter caches are absent. Its SHA-256 is `c09a831a532fa8e0b84b7c9dfc8b950d0a691b1a2827451cd479b3a40df908be`.
The archive was actually unpacked; each collector exited 2 with
`{"status":"held","code":"live-read-not-enabled"}` without its live flag.
Adding this evidence document increases the final source payload; verify that
final archive's membership separately rather than reusing this archive digest.

The isolated Astro page build completed 3,729 pages. All three new skill pages
were present and contained their own slug without meta-refresh markup; all five
retired routes were absent. All 231 existing retired-path redirect targets were
present and their source routes absent. The five GA4 mappings and original 30
Snowflake mappings passed source checks. The existing dist symlink was preserved.
This verifies built files and ingress configuration; it does not claim a live
production redirect deployment.

npm supports subdirectory ignore rules overriding an enclosing files allowlist,
which is why `skills/.npmignore` excludes caches under the explicit skills entry.
The actual tarball measurement confirms that boundary. See [npm's files
contract](https://docs.npmjs.com/cli/v11/configuring-npm/package-json/#files).

## Reproduction entry points

From the repository root, with the optional SDKs in an approved environment:

```bash
python3 -m unittest discover -s tests -p 'test_ga4_*.py' -v
python3 scripts/validate-skills-schema.py --marketplace plugins/saas-packs/ga4-pack/skills/ga4-report-forensics/SKILL.md
node --test marketplace/scripts/skill-redirects.test.mjs marketplace/scripts/retired-path-redirects.test.mjs
pnpm exec audit-harness verify
node scripts/regenerate-after-bump.mjs --check
```

The existing persistence suite is `tests/test_consistency_report_persistence.py`;
set `INTENT_OS_DISCLOSURE_ROOT` only to an approved local policy checkout for
its real-policy cases. It copies that policy to scratch destinations.

From the pack directory, `npm pack --ignore-scripts --json` produces the actual
archive for membership inspection. For isolated page verification, from
`marketplace/`, project the generated public data and run the installed Astro
CLI with an approved temporary `--outDir`. These checks neither publish an npm
package nor activate a native/provider integration.

## Retained local case outcomes

All 75 cases below completed as `ok` in the combined local run:

- `test_actual_sdk_dry_run_never_calls_result (test_ga4_export_collection.CollectionTests.test_actual_sdk_dry_run_never_calls_result)` — ok
- `test_complete_listing_preserves_observed_metadata (test_ga4_export_collection.CollectionTests.test_complete_listing_preserves_observed_metadata)` — ok
- `test_deadline_prevents_page_request (test_ga4_export_collection.CollectionTests.test_deadline_prevents_page_request)` — ok
- `test_disabled_cli_holds_before_credentials (test_ga4_export_collection.CollectionTests.test_disabled_cli_holds_before_credentials)` — ok
- `test_failed_dry_run_remains_visible_in_analysis (test_ga4_export_collection.CollectionTests.test_failed_dry_run_remains_visible_in_analysis)` — ok
- `test_listing_bound_is_explicit (test_ga4_export_collection.CollectionTests.test_listing_bound_is_explicit)` — ok
- `test_listing_failure_preserves_partial_evidence (test_ga4_export_collection.CollectionTests.test_listing_failure_preserves_partial_evidence)` — ok
- `test_metadata_permission_failure_does_not_invent_zero (test_ga4_export_collection.CollectionTests.test_metadata_permission_failure_does_not_invent_zero)` — ok
- `test_before_link_observations_and_future_dates_are_not_silently_erased (test_ga4_export_guardian.ExportGuardianTests.test_before_link_observations_and_future_dates_are_not_silently_erased)` — ok
- `test_cli_runs_without_cloud_sdk_and_rejects_duplicate_json (test_ga4_export_guardian.ExportGuardianTests.test_cli_runs_without_cloud_sdk_and_rejects_duplicate_json)` — ok
- `test_coexisting_daily_intraday_are_selected_not_summed (test_ga4_export_guardian.ExportGuardianTests.test_coexisting_daily_intraday_are_selected_not_summed)` — ok
- `test_estimate_above_cap_is_reported_even_when_actual_charge_is_unknown (test_ga4_export_guardian.ExportGuardianTests.test_estimate_above_cap_is_reported_even_when_actual_charge_is_unknown)` — ok
- `test_incomplete_inventory_cannot_establish_missing_tables (test_ga4_export_guardian.ExportGuardianTests.test_incomplete_inventory_cannot_establish_missing_tables)` — ok
- `test_invalid_dates_duplicate_tables_and_property_binding_are_held (test_ga4_export_guardian.ExportGuardianTests.test_invalid_dates_duplicate_tables_and_property_binding_are_held)` — ok
- `test_invalid_job_shapes_failed_dry_run_and_mutation_plans_are_held (test_ga4_export_guardian.ExportGuardianTests.test_invalid_job_shapes_failed_dry_run_and_mutation_plans_are_held)` — ok
- `test_lower_bound_unknown_accuracy_and_missing_budget_do_not_admit_execution (test_ga4_export_guardian.ExportGuardianTests.test_lower_bound_unknown_accuracy_and_missing_budget_do_not_admit_execution)` — ok
- `test_observed_missing_recent_and_intraday_states_are_distinct (test_ga4_export_guardian.ExportGuardianTests.test_observed_missing_recent_and_intraday_states_are_distinct)` — ok
- `test_query_budget_is_bound_to_exact_sql_and_is_not_a_bill (test_ga4_export_guardian.ExportGuardianTests.test_query_budget_is_bound_to_exact_sql_and_is_not_a_bill)` — ok
- `test_snapshot_day_uses_property_time_zone (test_ga4_export_guardian.ExportGuardianTests.test_snapshot_day_uses_property_time_zone)` — ok
- `test_unknown_settlement_bound_does_not_invent_an_sla (test_ga4_export_guardian.ExportGuardianTests.test_unknown_settlement_bound_does_not_invent_an_sla)` — ok
- `test_360_window_is_supported_but_not_assumed_for_standard (test_ga4_measurement_verifier.MeasurementVerifierTests.test_360_window_is_supported_but_not_assumed_for_standard)` — ok
- `test_below_expected_count_is_not_called_missing (test_ga4_measurement_verifier.MeasurementVerifierTests.test_below_expected_count_is_not_called_missing)` — ok
- `test_cli_json_and_duplicate_field_failure (test_ga4_measurement_verifier.MeasurementVerifierTests.test_cli_json_and_duplicate_field_failure)` — ok
- `test_clock_uncertainty_changes_deployment_attribution (test_ga4_measurement_verifier.MeasurementVerifierTests.test_clock_uncertainty_changes_deployment_attribution)` — ok
- `test_duplicate_event_rows_are_not_silently_double_counted (test_ga4_measurement_verifier.MeasurementVerifierTests.test_duplicate_event_rows_are_not_silently_double_counted)` — ok
- `test_filtered_reports_wrong_property_and_non_realtime_responses_are_held (test_ga4_measurement_verifier.MeasurementVerifierTests.test_filtered_reports_wrong_property_and_non_realtime_responses_are_held)` — ok
- `test_observed_and_absent_are_evidence_states_not_deployment_success (test_ga4_measurement_verifier.MeasurementVerifierTests.test_observed_and_absent_are_evidence_states_not_deployment_success)` — ok
- `test_overlapping_multiple_ranges_are_rejected_instead_of_summed (test_ga4_measurement_verifier.MeasurementVerifierTests.test_overlapping_multiple_ranges_are_rejected_instead_of_summed)` — ok
- `test_truncated_report_preserves_observation_but_not_absence (test_ga4_measurement_verifier.MeasurementVerifierTests.test_truncated_report_preserves_observation_but_not_absence)` — ok
- `test_window_crossing_deployment_cannot_verify_new_build (test_ga4_measurement_verifier.MeasurementVerifierTests.test_window_crossing_deployment_cannot_verify_new_build)` — ok
- `test_actual_sdk_wire_types_and_no_retry (test_ga4_realtime_collection.CollectionTests.test_actual_sdk_wire_types_and_no_retry)` — ok
- `test_disabled_cli_holds_without_sdk_or_credentials (test_ga4_realtime_collection.CollectionTests.test_disabled_cli_holds_without_sdk_or_credentials)` — ok
- `test_invalid_target_holds_before_transport (test_ga4_realtime_collection.CollectionTests.test_invalid_target_holds_before_transport)` — ok
- `test_one_bounded_read_and_no_false_absence_on_truncation (test_ga4_realtime_collection.CollectionTests.test_one_bounded_read_and_no_false_absence_on_truncation)` — ok
- `test_actual_sdk_accepts_the_generated_wire_request (test_ga4_report_collection.CollectionTests.test_actual_sdk_accepts_the_generated_wire_request)` — ok
- `test_actual_sdk_response_serialization_and_rpc_bounds (test_ga4_report_collection.CollectionTests.test_actual_sdk_response_serialization_and_rpc_bounds)` — ok
- `test_cli_default_does_not_collect (test_ga4_report_collection.CollectionTests.test_cli_default_does_not_collect)` — ok
- `test_deadline_prevents_another_request (test_ga4_report_collection.CollectionTests.test_deadline_prevents_another_request)` — ok
- `test_row_budget_returns_explicit_partial_receipt (test_ga4_report_collection.CollectionTests.test_row_budget_returns_explicit_partial_receipt)` — ok
- `test_two_pages_bind_semantics_and_offsets (test_ga4_report_collection.CollectionTests.test_two_pages_bind_semantics_and_offsets)` — ok
- `test_unsupported_query_cannot_invoke_transport (test_ga4_report_collection.CollectionTests.test_unsupported_query_cannot_invoke_transport)` — ok
- `test_cli_outputs_real_json_and_rejects_oversize_without_echoing_input (test_ga4_report_forensics.ReportForensicsTests.test_cli_outputs_real_json_and_rejects_oversize_without_echoing_input)` — ok
- `test_cli_rejects_duplicate_json_fields (test_ga4_report_forensics.ReportForensicsTests.test_cli_rejects_duplicate_json_fields)` — ok
- `test_complete_two_page_receipt_matches_one_page_without_summing_users (test_ga4_report_forensics.ReportForensicsTests.test_complete_two_page_receipt_matches_one_page_without_summing_users)` — ok
- `test_context_mismatch_prevents_numeric_comparison (test_ga4_report_forensics.ReportForensicsTests.test_context_mismatch_prevents_numeric_comparison)` — ok
- `test_contradictory_metadata_is_rejected (test_ga4_report_forensics.ReportForensicsTests.test_contradictory_metadata_is_rejected)` — ok
- `test_difference_reports_exact_direction_and_no_cross_row_user_sum (test_ga4_report_forensics.ReportForensicsTests.test_difference_reports_exact_direction_and_no_cross_row_user_sum)` — ok
- `test_duplicate_dimension_keys_and_changing_row_count_are_not_complete (test_ga4_report_forensics.ReportForensicsTests.test_duplicate_dimension_keys_and_changing_row_count_are_not_complete)` — ok
- `test_empty_rows_do_not_establish_zero_traffic (test_ga4_report_forensics.ReportForensicsTests.test_empty_rows_do_not_establish_zero_traffic)` — ok
- `test_equal_receipts_do_not_invent_a_cause_or_expose_dimension_values (test_ga4_report_forensics.ReportForensicsTests.test_equal_receipts_do_not_invent_a_cause_or_expose_dimension_values)` — ok
- `test_invalid_quality_flags_numbers_dates_and_headers_are_held (test_ga4_report_forensics.ReportForensicsTests.test_invalid_quality_flags_numbers_dates_and_headers_are_held)` — ok
- `test_large_decimal_delta_does_not_silently_round_report_values (test_ga4_report_forensics.ReportForensicsTests.test_large_decimal_delta_does_not_silently_round_report_values)` — ok
- `test_missing_page_or_stalled_page_is_inconclusive (test_ga4_report_forensics.ReportForensicsTests.test_missing_page_or_stalled_page_is_inconclusive)` — ok
- `test_sampling_and_other_row_loss_are_independent_findings (test_ga4_report_forensics.ReportForensicsTests.test_sampling_and_other_row_loss_are_independent_findings)` — ok
- `test_unknown_currency_blocks_comparison_of_money (test_ga4_report_forensics.ReportForensicsTests.test_unknown_currency_blocks_comparison_of_money)` — ok
- `test_unknown_reporting_identity_blocks_comparison (test_ga4_report_forensics.ReportForensicsTests.test_unknown_reporting_identity_blocks_comparison)` — ok
- `test_zero_baseline_never_produces_infinite_percentage (test_ga4_report_forensics.ReportForensicsTests.test_zero_baseline_never_produces_infinite_percentage)` — ok
- `test_cli_failure_output_contains_no_rejected_content (test_consistency_report_persistence.CanonicalPolicyIntegrationTests.test_cli_failure_output_contains_no_rejected_content)` — ok
- `test_real_filter_saves_only_approved_report (test_consistency_report_persistence.CanonicalPolicyIntegrationTests.test_real_filter_saves_only_approved_report)` — ok
- `test_real_rejection_fault_bypass_and_missing_policy_do_not_leak (test_consistency_report_persistence.CanonicalPolicyIntegrationTests.test_real_rejection_fault_bypass_and_missing_policy_do_not_leak)` — ok
- `test_busy_index_is_held_without_creating_a_report (test_consistency_report_persistence.PersistenceTests.test_busy_index_is_held_without_creating_a_report)` — ok
- `test_concurrent_index_replacement_is_preserved_and_reported_incomplete (test_consistency_report_persistence.PersistenceTests.test_concurrent_index_replacement_is_preserved_and_reported_incomplete)` — ok
- `test_destination_cannot_be_the_audited_tree (test_consistency_report_persistence.PersistenceTests.test_destination_cannot_be_the_audited_tree)` — ok
- `test_identical_retry_never_overwrites_or_adds_an_index_entry (test_consistency_report_persistence.PersistenceTests.test_identical_retry_never_overwrites_or_adds_an_index_entry)` — ok
- `test_index_symlink_is_rejected_without_following_it (test_consistency_report_persistence.PersistenceTests.test_index_symlink_is_rejected_without_following_it)` — ok
- `test_index_write_failure_preserves_report_and_reports_incomplete (test_consistency_report_persistence.PersistenceTests.test_index_write_failure_preserves_report_and_reports_incomplete)` — ok
- `test_missing_lanes_and_unsubstantiated_repair_shape_are_rejected (test_consistency_report_persistence.PersistenceTests.test_missing_lanes_and_unsubstantiated_repair_shape_are_rejected)` — ok
- `test_missing_policy_is_held_before_any_destination_write (test_consistency_report_persistence.PersistenceTests.test_missing_policy_is_held_before_any_destination_write)` — ok
- `test_moved_record_in_cluster_still_blocks_identical_retry (test_consistency_report_persistence.PersistenceTests.test_moved_record_in_cluster_still_blocks_identical_retry)` — ok
- `test_numbered_report_preserves_lanes_authority_repairs_and_index_prefix (test_consistency_report_persistence.PersistenceTests.test_numbered_report_preserves_lanes_authority_repairs_and_index_prefix)` — ok
- `test_policy_hold_writes_no_report_or_index_bytes (test_consistency_report_persistence.PersistenceTests.test_policy_hold_writes_no_report_or_index_bytes)` — ok
- `test_symlink_file_or_directory_in_numbered_tree_is_held (test_consistency_report_persistence.PersistenceTests.test_symlink_file_or_directory_in_numbered_tree_is_held)` — ok
- `test_accepted_output_without_durable_receipts_is_held (test_consistency_report_persistence.PolicyTransportTests.test_accepted_output_without_durable_receipts_is_held)` — ok
- `test_success_exit_with_dropped_payload_does_not_authorize_a_write (test_consistency_report_persistence.PolicyTransportTests.test_success_exit_with_dropped_payload_does_not_authorize_a_write)` — ok
- `test_temp_parent_inside_destination_or_audited_tree_is_held_before_adapter (test_consistency_report_persistence.PolicyTransportTests.test_temp_parent_inside_destination_or_audited_tree_is_held_before_adapter)` — ok
