# Deploy on Coolify

Coolify acts as the external reverse proxy: its built-in Traefik terminates
TLS (Let's Encrypt, automatic) and routes the public domain to the `web`
container. The API stays internal. The ~28 MB of dataset + checkpoint are **not**
in git or the image — they download on first boot from `ARTIFACTS_URL` into a
persistent volume (the ETR model is refit on first use, see below).

## 1. Upload the artifacts tarball

A tarball with the minimal runtime set is at `/tmp/aether-artifacts.tar.gz`
(~28 MB). Regenerate any time with:

```sh
make artifacts-tarball     # see Makefile target below, or run the tar by hand
```

Contents (extracts relative to `/app`):

```
data/metadata.sqlite
data/splits.json
data/mace_features/{train,val,test}_emb.npz
logs/checkpoints/mace_ft_stageA_v2_seed42/last.ckpt
```

The ETR model (`etr_emb.pkl`, ~193 MB) is **not** bundled: the API refits it
from the `_emb.npz` files and HMAC-signs the cache on the first `/screen` call
(~1-2 min, then served from the `aether-data` volume). This keeps the download
tiny and means a tampered pickle can never ship in the tarball.

Upload it to any HTTP-reachable object storage and get a download URL:

- **Cloudflare R2** (free tier, no egress fees) — recommended
- **AWS S3 / Backblaze B2** — presigned URL or public object
- Any static file host returning the raw `.tar.gz`

The URL must return the raw gzip bytes (not an HTML download page). Test:

```sh
curl -fsSL "$ARTIFACTS_URL" | tar -tz | head
```

Compute its sha256 (required — the API refuses to extract an unverified
tarball, and the URL must be `https://`):

```sh
curl -fsSL "$ARTIFACTS_URL" | sha256sum
```

## 2. Create the resource in Coolify

1. **+ New** → **Docker Compose** (Git-based) → select this repo + branch.
2. Set **Docker Compose Location** to `docker-compose.coolify.yml`.
3. **Environment Variables** → add:
   - `ARTIFACTS_URL` = the tarball download URL from step 1 (must be `https://`).
   - `ARTIFACTS_SHA256` = the sha256 from step 1. Boot aborts on mismatch.
   - `ETR_CACHE_KEY` = a long random secret (`openssl rand -hex 32`). Signs the
     ETR model cache (HMAC) so a tampered `etr_emb.pkl` is never unpickled.
   - `API_KEY` *(optional)* = set to require `X-API-Key` on `/screen`. Leave
     unset for the open public demo. If set, also forward the header at the
     proxy (see Notes).
   - `ENABLE_DOCS` *(optional)* = `1` to expose `/api/docs`. Default off.
4. **Domains** → on the `web` service, set your domain, internal port `80`.
   Coolify provisions the TLS cert automatically.
5. **Deploy.**

First deploy: the API container downloads + extracts the tarball before it
passes its healthcheck (`start_period: 300s` allows for this). `web` waits for
`api` to be healthy. Watch the API logs for `[entrypoint] artifacts ready.`

## 3. Redeploys

The `aether-data` and `aether-checkpoints` volumes are persistent, so the
download happens **only once**. Later redeploys reuse them and start fast.
To force a re-download, delete those volumes in Coolify and redeploy.

## Endpoints once live

- `https://<domain>/` — web UI
- `https://<domain>/api/stats` — proxied API (rate-limited 10 r/s)
- `https://<domain>/api/docs` — FastAPI Swagger (only if `ENABLE_DOCS=1`)

## Notes / limits

- App-level auth is **opt-in**: unset `API_KEY` = open demo (nginx rate-limit is
  the only control); set `API_KEY` = `/screen` requires a matching `X-API-Key`.
  When enabled, inject the header at the proxy so the SPA keeps working, e.g. add
  `proxy_set_header X-API-Key "<key>";` to the `/api/` block in
  `services/web/nginx.conf`, or add Coolify Basic Auth on the domain instead.
- The API listens only on the internal compose network (`expose`, never
  published), so it is not directly reachable from the internet.
- `results/` (model comparison data) is baked into the API image, so
  `/api/comparison` works without the tarball.
- If the proxy runs on a separate host than the containers, that's still fine —
  Coolify wires its proxy to the container network regardless.
