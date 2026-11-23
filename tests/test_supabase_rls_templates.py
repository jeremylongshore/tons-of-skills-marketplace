"""Exercise the documented RLS template on a private, disposable PostgreSQL server.

Requires local PostgreSQL server binaries; never uses PGHOST or an existing server.
"""

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins/saas-packs/supabase-pack/skills/supabase-policy-guardrails/SKILL.md"
USER_A = "00000000-0000-4000-8000-000000000001"
USER_B = "00000000-0000-4000-8000-000000000002"


@pytest.fixture
def database(tmp_path):
    candidates = sorted(Path("/usr/lib/postgresql").glob("*/bin/initdb"))
    initdb = shutil.which("initdb") or (str(candidates[-1]) if candidates else None)
    if not initdb or os.geteuid() == 0:
        pytest.skip("Requires PostgreSQL server binaries and a non-root test user")
    bindir = Path(initdb).parent
    data, sock = tmp_path / "data", tmp_path / "socket"
    sock.mkdir(mode=0o700)
    env = {k: v for k, v in os.environ.items() if not k.startswith("PG")}
    env["LC_ALL"] = "C"
    subprocess.run([initdb, "-D", str(data), "-A", "trust", "--no-locale"], env=env, check=True, capture_output=True)
    control = [str(bindir / "pg_ctl"), "-D", str(data)]
    subprocess.run(
        control + ["-l", str(tmp_path / "server.log"), "-o", f"-k {sock} -c listen_addresses=''", "-w", "start"],
        env=env,
        check=True,
        capture_output=True,
    )

    def query(sql):
        return subprocess.run(
            [str(bindir / "psql"), "-X", "-h", str(sock), "-d", "postgres", "-v", "ON_ERROR_STOP=1", "-At", "-c", sql],
            env=env,
            capture_output=True,
            text=True,
            timeout=20,
        )

    try:
        blocks = re.findall(r"```sql\n(.*?)\n```", SKILL.read_text(), re.S)
        setup = (
            """
CREATE SCHEMA auth;
CREATE FUNCTION auth.uid() RETURNS uuid LANGUAGE sql STABLE AS
$$ SELECT nullif(current_setting('fixture.user_id', true), '')::uuid $$;
CREATE ROLE fixture_user NOLOGIN NOSUPERUSER NOBYPASSRLS;
GRANT USAGE ON SCHEMA auth TO fixture_user;
CREATE TABLE public.posts (id integer PRIMARY KEY, author_id uuid NOT NULL, body text);
GRANT SELECT, INSERT, UPDATE, DELETE ON public.posts TO fixture_user;
"""
            + blocks[0]
            + "\nSELECT public.rls_public_read_auth_write('posts', 'author_id');"
        )
        result = query(setup)
        assert result.returncode == 0, result.stderr
        yield query
    finally:
        subprocess.run(control + ["-m", "fast", "-w", "stop"], env=env, check=True, capture_output=True)


def session(user):
    return f"SET ROLE fixture_user; SET fixture.user_id = '{user}'; "


def test_public_insert_binds_owner(database):
    own = database(session(USER_A) + f"INSERT INTO posts VALUES (1, '{USER_A}', 'own');")
    assert own.returncode == 0, own.stderr
    forged = database(session(USER_A) + f"INSERT INTO posts VALUES (2, '{USER_B}', 'forged');")
    assert forged.returncode != 0
    assert "row-level security" in forged.stderr
    assert database("SELECT count(*) FROM posts").stdout.strip() == "1"


def test_public_read_does_not_grant_cross_owner_mutation(database):
    assert database(f"INSERT INTO posts VALUES (1, '{USER_A}', 'original');").returncode == 0
    read = database(session(USER_B) + "SELECT body FROM posts WHERE id=1;")
    assert read.returncode == 0 and read.stdout.strip().endswith("original")
    changed = database(session(USER_B) + "UPDATE posts SET body='changed' WHERE id=1;")
    assert changed.returncode == 0 and "UPDATE 0" in changed.stdout
    moved = database(session(USER_A) + f"UPDATE posts SET author_id='{USER_B}' WHERE id=1;")
    assert moved.returncode != 0 and "row-level security" in moved.stderr
    anonymous = database(session("") + f"INSERT INTO posts VALUES (2, '{USER_A}', 'anonymous');")
    assert anonymous.returncode != 0 and "row-level security" in anonymous.stderr
    assert database("SELECT body FROM posts").stdout.strip() == "original"
