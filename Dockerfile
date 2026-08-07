FROM ghcr.io/astral-sh/uv:0.11.8 AS uv
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

COPY --from=uv /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock README.md LICENSE ./
RUN uv sync --frozen --no-dev --no-install-project

COPY ads_mcp ./ads_mcp
RUN uv sync --frozen --no-dev --no-editable

RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app \
    && mkdir -p /var/lib/google-ads-mcp/oauth \
    && chown -R app:app /var/lib/google-ads-mcp

USER app

EXPOSE 8080
VOLUME ["/var/lib/google-ads-mcp/oauth"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/.well-known/oauth-authorization-server', timeout=3)"]

CMD ["google-ads-mcp"]
