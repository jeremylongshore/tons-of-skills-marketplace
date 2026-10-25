"""The opt-in signing trial cannot publish or replace production signing."""

import pathlib
import unittest

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]


class CosignTrialContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = yaml.safe_load((ROOT / ".github/workflows/emit-evidence.yml").read_text())
        cls.production = cls.workflow["jobs"]["emit"]
        cls.trial = cls.workflow["jobs"]["cosign-v3-trial"]

    def test_trial_requires_explicit_main_dispatch_and_does_not_cancel_production(self):
        events = self.workflow.get("on", self.workflow.get(True))
        self.assertEqual(set(events), {"push", "workflow_dispatch"})
        option = events["workflow_dispatch"]["inputs"]["cosign_v3_trial"]
        self.assertEqual(option["type"], "boolean")
        self.assertIs(option["default"], False)
        opt_in = "github.event_name == 'workflow_dispatch' && inputs.cosign_v3_trial"
        self.assertEqual(self.trial["if"], "github.ref == 'refs/heads/main' && " + opt_in)
        self.assertEqual(self.production["if"], "github.ref == 'refs/heads/main' && !(" + opt_in + ")")
        self.assertEqual(
            self.workflow["concurrency"]["group"],
            "${{ " + opt_in + " && format('cosign-v3-trial-{0}', github.run_id) || 'emit-evidence' }}",
        )

    def test_trial_has_no_write_or_publish_step(self):
        self.assertEqual(
            self.trial["permissions"],
            {"checks": "read", "contents": "read", "id-token": "write"},
        )
        for step in self.trial["steps"]:
            self.assertNotIn("gh release", step.get("run", ""))
        uploads = [s for s in self.trial["steps"] if s.get("uses", "").startswith("actions/upload-artifact@")]
        self.assertEqual(len(uploads), 1)
        self.assertEqual(uploads[0]["with"]["if-no-files-found"], "error")
        receipt = next(s["run"] for s in self.trial["steps"] if s["name"].startswith("Record trial"))
        self.assertIn('consumer_verification:"not_run"', receipt)
        self.assertIn("published:false", receipt)

    def test_exact_producer_payload_sign_verify_and_assembly_steps_are_reused(self):
        names = [
            "Await completed protected-branch contexts for this SHA",
            "Emit gate-result/v1 EvidenceBundle(s)",
            "Sign each EvidenceBundle (cosign keyless -> production Rekor)",
            "Verify each EvidenceBundle signature (cosign verify-blob; fail-closed)",
            "Assemble report-manifest.json (fail-closed on shape mismatch)",
        ]
        production = {s["name"]: s for s in self.production["steps"]}
        trial = {s["name"]: s for s in self.trial["steps"]}
        for name in names:
            with self.subTest(step=name):
                self.assertEqual(trial[name], production[name])
        self.assertIn('--certificate-identity "$cert_identity"', trial[names[3]]["run"])
        self.assertNotIn("--insecure", trial[names[3]]["run"])

    def test_both_production_installers_remain_v2_and_trial_pins_v3(self):
        def pin(job):
            return next(
                s["with"]["cosign-release"]
                for s in job["steps"]
                if s.get("uses", "").startswith("sigstore/cosign-installer@")
            )

        publication = yaml.safe_load((ROOT / ".github/workflows/emit-publication-evidence.yml").read_text())
        self.assertEqual(pin(self.production), "v2.5.2")
        self.assertEqual(pin(publication["jobs"]["emit"]), "v2.5.2")
        self.assertEqual(pin(self.trial), "v3.0.6")


if __name__ == "__main__":
    unittest.main()
