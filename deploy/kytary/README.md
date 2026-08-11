# Kytary production deployment

This deployment runs one Google Ads MCP instance in Coolify and publishes it
through the existing `servisacek` Cloudflare Tunnel. FastMCP handles Google
OAuth directly; there is no second OAuth proxy.

## Public endpoints

- MCP: `https://google-ads-mcp.kytaryai.org/mcp`
- OAuth callback: `https://google-ads-mcp.kytaryai.org/auth/callback`
- Local host port: `127.0.0.1:8025`

## Google prerequisites

1. Enable the Google Ads API in the selected Google Cloud project.
2. Create an OAuth 2.0 Web application. Add the callback above as an exact
   authorized redirect URI and the public origin as an authorized JavaScript
   origin.
3. Use an Internal consent screen when all users belong to the Workspace;
   otherwise configure the required test/production users.
4. Obtain a Google Ads developer token with at least Explorer access. If the
   accounts are reached through a manager account, also provide its digits-only
   customer ID as `GOOGLE_ADS_LOGIN_CUSTOMER_ID`.

The OAuth scope is the Google Ads `adwords` scope because Google does not offer
a read-only Ads scope. This server only exposes the three upstream read tools.

## Coolify

Deploy the repository with `deploy/kytary/compose.yaml`. Its build context is
the repository root, matching Coolify's Compose project directory. For a local
deployment, preserve the same resolution with
`docker compose --project-directory . -f deploy/kytary/compose.yaml up`.
Keep exactly one replica and configure all values from `env.example` as
secrets. Generate the two application secrets independently, for example:

```shell
openssl rand -hex 32
openssl rand -hex 32
```

The named volume at `/var/lib/google-ads-mcp/oauth` is mandatory. It preserves
OAuth client registrations and encrypted token state through container
restarts. Never rotate either application secret without planning to invalidate
existing connector sessions.

The container publishes only on loopback port 8025. The production allowlist
accepts verified Google identities in `kytary.cz` and `audiopartner.com`; use
`GOOGLE_ADS_MCP_ALLOWED_EMAILS` in Coolify as an additional comma-separated
exact-user allowlist if needed.

## Cloudflare Tunnel

Insert the hostname rule from `cloudflared-config-snippet.yml` before the final
catch-all ingress rule, create the hostname route for the `servisacek` tunnel,
then reload the tunnel service. Do not enable Cloudflare Access in front of the
endpoint because MCP clients need FastMCP's OAuth discovery and callback flow.

## Acceptance checks

1. Container health is `healthy` and survives a restart with its volume.
2. OAuth and protected-resource metadata return HTTP 200.
3. An unauthenticated request to `/mcp` returns HTTP 401.
4. Claude can authenticate with an allowed Workspace account.
5. `customers_list_accessible_customers` succeeds.
6. A small `search_search` GAQL query succeeds for an authorized customer.
