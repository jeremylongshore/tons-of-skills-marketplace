"""Regression checks for ROOT resolution in the ``sync-marketplace`` chain.

Issue #1436. Both generators in the chain derived the repository root as
``resolve(dirname(new URL(import.meta.url).pathname), '..')``. ``URL.pathname``
is platform-independent and keeps a leading slash before a Windows drive letter,
so ``/C:/repo/scripts/x.mjs`` is read as drive-relative and ROOT resolves to
``C:\\C:\\repo``. The code is correct on POSIX and only wrong on Windows, which
is why CI stayed green.

One half failed loudly and one half did not, and the silent half is the reason
these checks exist. ``generate-plugin-package-jsons.mjs`` globbed nothing on the
bad ROOT, printed ``Wrote 0 package.json files.`` and exited 0 -- on a tree
holding 439 plugins. Only ``generate-readme-toc.mjs``, further down the chain,
raised ENOENT.

These run on Linux CI, where the original defect is by definition
unreproducible. So the static half pins the corrected form in both scripts, and
the behavioural half provokes the *consequence* -- an empty discovery -- in a way
that is platform-independent: run the generator from a location where
``../plugins`` does not exist and require it to fail rather than succeed quietly.

Stdlib ``unittest`` and no third-party imports, so the "Test in-repo Python
suites" step in ``.github/workflows/validate-plugins.yml`` can run it directly.
It lives in ``tests/`` rather than ``tests/ci/`` for the same reason: nothing in
CI invokes ``tests/ci/``, and a regression test that never executes is not
coverage.
"""

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_JSON_GENERATOR = REPO_ROOT / "scripts" / "generate-plugin-package-jsons.mjs"
TOC_GENERATOR = REPO_ROOT / "scripts" / "generate-readme-toc.mjs"

# Exactly the two scripts `npm run sync-marketplace` invokes after
# sync-marketplace.cjs. The wider `.pathname` usage elsewhere in scripts/ is
# deliberately out of scope here -- see the issue thread.
CHAIN_GENERATORS = (PACKAGE_JSON_GENERATOR, TOC_GENERATOR)

PATHNAME_FORM = "new URL(import.meta.url).pathname"
CORRECT_FORM = "fileURLToPath(import.meta.url)"

NODE = shutil.which("node")


class RootDerivationTests(unittest.TestCase):
    """Static half: pin the corrected form in both chain scripts."""

    def test_chain_generators_derive_root_with_file_url_to_path(self) -> None:
        for generator in CHAIN_GENERATORS:
            with self.subTest(generator=generator.name):
                source = generator.read_text(encoding="utf-8")

                root_lines = [
                    line for line in source.splitlines() if line.startswith("const ROOT =")
                ]
                self.assertEqual(
                    len(root_lines),
                    1,
                    f"{generator.name}: expected exactly one ROOT binding",
                )
                self.assertIn(
                    CORRECT_FORM,
                    root_lines[0],
                    f"{generator.name}: ROOT must be derived with fileURLToPath. "
                    "URL.pathname resolves to a doubled drive letter on Windows (#1436).",
                )
                self.assertIn(
                    "fileURLToPath",
                    source,
                    f"{generator.name}: fileURLToPath is not imported",
                )

    def test_chain_generators_do_not_reintroduce_the_pathname_form(self) -> None:
        """The prose may name the broken form; the code may not use it.

        Both files document why `URL.pathname` is wrong, so a bare substring
        search would match the explanation and never fail. Comment lines are
        dropped first so this asserts on code.
        """
        for generator in CHAIN_GENERATORS:
            with self.subTest(generator=generator.name):
                code_lines = [
                    line
                    for line in generator.read_text(encoding="utf-8").splitlines()
                    if not line.lstrip().startswith(("//", "*", "/*"))
                ]
                offenders = [line.strip() for line in code_lines if PATHNAME_FORM in line]

                self.assertEqual(
                    offenders,
                    [],
                    f"{generator.name}: URL.pathname is back in executable code",
                )


@unittest.skipIf(NODE is None, "node is not on PATH")
class EmptyDiscoveryTests(unittest.TestCase):
    """Behavioural half: an empty discovery must not report success."""

    def test_generator_fails_closed_on_zero_discovery(self) -> None:
        """The silent half of #1436: zero plugins found must not be exit 0.

        Before the fix this printed a success summary and exited 0, so the
        `sync-marketplace` step reported done having written nothing.

        The script derives ROOT from its own location and imports only node
        builtins, so relocating it is a faithful way to produce a wrong ROOT on
        any platform -- including the Linux runner, where the drive-letter
        defect cannot occur at all.
        """
        with tempfile.TemporaryDirectory() as tmp:
            scripts_dir = Path(tmp) / "scripts"
            scripts_dir.mkdir(parents=True)
            relocated = scripts_dir / PACKAGE_JSON_GENERATOR.name
            shutil.copy2(PACKAGE_JSON_GENERATOR, relocated)

            result = subprocess.run(
                [NODE, str(relocated), "--dry-run"],
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertNotEqual(
            result.returncode,
            0,
            "generator exited 0 having discovered no plugins; that is the silent "
            f"failure #1436 is about.\nstdout: {result.stdout}\nstderr: {result.stderr}",
        )
        self.assertIn(
            "Resolved ROOT:",
            result.stdout + result.stderr,
            "the refusal must name the resolved ROOT -- when this fires, the "
            "resolved path is the diagnosis",
        )
        self.assertNotIn(
            "Wrote 0 package.json files.",
            result.stdout,
            "the generator reported a successful write summary on an empty discovery",
        )

    def test_generator_still_discovers_this_repository(self) -> None:
        """The other direction, so the guard cannot be satisfied by refusing always.

        A check that is happiest when the tool is broken is measuring the wrong
        thing: this asserts the corrected ROOT actually finds the plugin tree.
        """
        result = subprocess.run(
            [NODE, str(PACKAGE_JSON_GENERATOR), "--dry-run"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(
            result.returncode,
            0,
            f"dry run failed against the real repository.\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}",
        )

        discovered = [
            line
            for line in result.stdout.splitlines()
            if line.startswith("Plugins with package.json already:")
        ]
        self.assertTrue(discovered, f"no discovery summary in output:\n{result.stdout}")

        count = int(discovered[0].split(":")[1].strip())
        self.assertGreater(
            count,
            0,
            "discovered 0 plugins in a repository that has them -- the ROOT regression is back",
        )


if __name__ == "__main__":
    unittest.main()
