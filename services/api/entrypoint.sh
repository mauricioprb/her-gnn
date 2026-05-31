#!/bin/sh

set -e

DATA_MARKER=/app/data/metadata.sqlite

if [ ! -f "$DATA_MARKER" ]; then
    if [ -z "$ARTIFACTS_URL" ]; then
        echo "FATAL: runtime artifacts missing and ARTIFACTS_URL not set." >&2
        echo "       Set ARTIFACTS_URL to a .tar.gz of data/ + logs/checkpoints/." >&2
        exit 1
    fi
    if [ -z "$ARTIFACTS_SHA256" ]; then
        echo "FATAL: ARTIFACTS_SHA256 not set; refusing to fetch unverified artifacts." >&2
        echo "       Set it to the sha256 of the .tar.gz at ARTIFACTS_URL." >&2
        exit 1
    fi
    echo "[entrypoint] artifacts absent; downloading + verifying from ARTIFACTS_URL ..."
    tmp=$(mktemp)
    .venv/bin/python - "$ARTIFACTS_URL" "$tmp" "$ARTIFACTS_SHA256" <<'PY'
import hashlib, sys, tarfile, urllib.request

url, dst, expected = sys.argv[1], sys.argv[2], sys.argv[3].lower()
if not url.startswith("https://"):
    sys.exit("FATAL: ARTIFACTS_URL must use https://")
with urllib.request.urlopen(url, timeout=120) as resp:  # noqa: S310 (scheme checked)
    data = resp.read()
digest = hashlib.sha256(data).hexdigest()
if digest != expected:
    sys.exit(f"FATAL: artifact checksum mismatch (got {digest}, want {expected})")
with open(dst, "wb") as f:
    f.write(data)
with tarfile.open(dst) as t:
    t.extractall("/app", filter="data")
print("[entrypoint] checksum OK, extracted safely")
PY
    rm -f "$tmp"
    echo "[entrypoint] artifacts ready."
fi

exec "$@"
