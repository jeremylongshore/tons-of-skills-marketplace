"""Execute the notification workflow shell against an inert loopback server."""

import json
import os
import socket
import subprocess
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


class SecretNotificationTests(unittest.TestCase):
    def setUp(self):
        self.requests = []
        self.http_status = 200
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                body = self.rfile.read(int(self.headers["Content-Length"]))
                owner.requests.append((self.headers["Content-Type"], json.loads(body)))
                self.send_response(owner.http_status)
                self.end_headers()
                self.wfile.write(b"ok" if owner.http_status == 200 else b"synthetic rejection")

            def log_message(self, *_args):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=lambda: self.server.serve_forever(poll_interval=0.01))
        self.thread.start()
        self.addCleanup(self.stop_server)
        self.url = f"http://127.0.0.1:{self.server.server_port}/synthetic-webhook"
        workflow = yaml.safe_load((ROOT / ".github/workflows/secret-scan.yml").read_text())
        self.shell = workflow["jobs"]["trufflehog"]["steps"][2]["run"]
        self.shell = self.shell.replace("${{ github.repository }}", "synthetic/repository").replace(
            "${{ github.run_id }}", "123"
        )

    def stop_server(self):
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()

    def run_notification(self, webhook=None):
        with tempfile.TemporaryDirectory(prefix="ci-notification-") as directory:
            # Do not inherit proxy settings, curl configuration, or real secrets.
            return subprocess.run(
                ["bash", "-e", "-c", self.shell],
                cwd=directory,
                env={
                    "PATH": os.defpath,
                    "HOME": directory,
                    "CURL_HOME": directory,
                    "SLACK_WEBHOOK": self.url if webhook is None else webhook,
                },
                capture_output=True,
                text=True,
                timeout=10,
            )

    def test_success_posts_unchanged_json(self):
        result = self.run_notification()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            self.requests,
            [
                (
                    "application/json",
                    {
                        "text": ":rotating_light: Weekly trufflehog scan found *verified* credentials in main. "
                        "See https://github.com/synthetic/repository/actions/runs/123"
                    },
                )
            ],
        )

    def test_http_rejections_fail(self):
        for status in (400, 500):
            with self.subTest(status=status):
                self.http_status = status
                self.requests.clear()
                result = self.run_notification()
                self.assertEqual(result.returncode, 22, result.stderr)
                self.assertEqual(len(self.requests), 1)

    def test_missing_webhook_still_skips_without_post(self):
        result = self.run_notification("")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("skipping notification", result.stdout)
        self.assertEqual(self.requests, [])

    def test_transport_failure_still_fails(self):
        # A bound but non-listening socket reserves the port without accepting traffic.
        with socket.socket() as reserved:
            reserved.bind(("127.0.0.1", 0))
            result = self.run_notification(f"http://127.0.0.1:{reserved.getsockname()[1]}/synthetic-webhook")
        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertEqual(self.requests, [])
