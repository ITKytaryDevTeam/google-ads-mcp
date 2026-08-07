# Copyright 2026 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for the Google identity allowlist."""

import os
import unittest
from types import SimpleNamespace

from ads_mcp.access import create_google_email_access_check


class TestGoogleEmailAccessCheck(unittest.TestCase):
    def setUp(self):
        self.keys = [
            "GOOGLE_ADS_MCP_ALLOWED_EMAILS",
            "GOOGLE_ADS_MCP_ALLOWED_DOMAINS",
        ]
        self.original = {
            key: os.environ.pop(key) for key in self.keys if key in os.environ
        }

    def tearDown(self):
        for key in self.keys:
            os.environ.pop(key, None)
        os.environ.update(self.original)

    @staticmethod
    def context(email, verified=True):
        token = SimpleNamespace(
            claims={"email": email, "email_verified": verified}
        )
        return SimpleNamespace(token=token)

    def test_no_allowlist_disables_check(self):
        self.assertIsNone(create_google_email_access_check())

    def test_allows_verified_email_case_insensitively(self):
        os.environ["GOOGLE_ADS_MCP_ALLOWED_EMAILS"] = "User@Kytary.cz"
        check = create_google_email_access_check()
        self.assertTrue(check(self.context("user@kytary.cz")))

    def test_allows_verified_domain(self):
        os.environ["GOOGLE_ADS_MCP_ALLOWED_DOMAINS"] = (
            "@kytary.cz, audiopartner.com"
        )
        check = create_google_email_access_check()
        self.assertTrue(check(self.context("user@audiopartner.com")))

    def test_rejects_unverified_or_unlisted_email(self):
        os.environ["GOOGLE_ADS_MCP_ALLOWED_DOMAINS"] = "kytary.cz"
        check = create_google_email_access_check()
        self.assertFalse(check(self.context("user@kytary.cz", verified=False)))
        self.assertFalse(check(self.context("user@example.com")))

    def test_rejects_missing_token(self):
        os.environ["GOOGLE_ADS_MCP_ALLOWED_DOMAINS"] = "kytary.cz"
        check = create_google_email_access_check()
        self.assertFalse(check(SimpleNamespace(token=None)))


if __name__ == "__main__":
    unittest.main()
