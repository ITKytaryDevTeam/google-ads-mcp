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

"""Optional Google-account allowlist for HTTP deployments."""

import os
from collections.abc import Callable

from fastmcp.server.auth import AuthContext


def _csv_values(name: str) -> set[str]:
    """Return normalized, non-empty values from a comma-separated env var."""
    return {
        value.strip().lower()
        for value in os.environ.get(name, "").split(",")
        if value.strip()
    }


def create_google_email_access_check() -> Callable[[AuthContext], bool] | None:
    """Create an authorization check for configured Google users or domains.

    If neither allowlist is configured, no check is returned. Deployments that
    expose the server publicly should configure at least one allowlist.
    """
    allowed_emails = _csv_values("GOOGLE_ADS_MCP_ALLOWED_EMAILS")
    allowed_domains = {
        domain.removeprefix("@")
        for domain in _csv_values("GOOGLE_ADS_MCP_ALLOWED_DOMAINS")
    }

    if not allowed_emails and not allowed_domains:
        return None

    def is_allowed(ctx: AuthContext) -> bool:
        if ctx.token is None:
            return False

        claims = ctx.token.claims
        verified = claims.get("email_verified")
        if verified is not True and str(verified).lower() != "true":
            return False

        email = str(claims.get("email") or "").strip().lower()
        if not email or "@" not in email:
            return False

        domain = email.rsplit("@", 1)[1]
        return email in allowed_emails or domain in allowed_domains

    return is_allowed
