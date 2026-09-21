"""Security-contract regressions for the remediated Mistral skills."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MISTRAL_SKILLS = ROOT / "plugins" / "saas-packs" / "mistral-pack" / "skills"
COMMON_ERRORS = MISTRAL_SKILLS / "mistral-common-errors" / "SKILL.md"
INCIDENT_RUNBOOK = MISTRAL_SKILLS / "mistral-incident-runbook" / "SKILL.md"


class MistralCommonErrorsSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = COMMON_ERRORS.read_text(encoding="utf-8")

    def test_401_and_429_have_fail_closed_non_replay_guidance(self) -> None:
        self.assertIn("Repeated `401` calls will not repair a revoked key", self.text)
        self.assertIn("Aggressive retries after `429` amplify queued demand", self.text)
        self.assertIn("Never blindly retry stateful work", self.text)

        freeze = self.text.index("Freeze automatic retries")
        reproduce = self.text.index("Reproduce once with synthetic data only when approved")
        self.assertLess(freeze, reproduce)

    def test_diagnostics_are_content_free_and_do_not_authorize_network_calls(self) -> None:
        for required in (
            "sanitized error",
            "Never request or reproduce a key",
            "does not authorize network calls",
            "exposes no content or credentials",
        ):
            with self.subTest(required=required):
                self.assertIn(required, self.text)

        self.assertNotIn("```bash", self.text)
        self.assertNotIn("curl ", self.text)


class MistralIncidentEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = INCIDENT_RUNBOOK.read_text(encoding="utf-8")

    def test_incident_evidence_stays_content_free_and_approval_bounded(self) -> None:
        for required in (
            "Content-free telemetry",
            "Never paste keys into incident channels",
            "The commander must approve revocation",
            "Record the approver and exact containment scope",
            "Purging queues can destroy reconciliation evidence",
        ):
            with self.subTest(required=required):
                self.assertIn(required, self.text)

        self.assertNotIn("kubectl logs", self.text)
        self.assertNotIn("```bash", self.text)

    def test_containment_and_reconciliation_precede_replay(self) -> None:
        contain = self.text.index("Choose bounded containment")
        reconcile = self.text.index("Reconcile files, jobs, runs, conversations")
        recover = self.text.index("Recover through synthetic canary")
        self.assertLess(contain, reconcile)
        self.assertLess(reconcile, recover)
        self.assertIn("Blind replay can duplicate paid/stateful work", self.text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
