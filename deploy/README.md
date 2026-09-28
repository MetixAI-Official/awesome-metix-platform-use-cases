# Deploying the Casebook

The Casebook is served at `platform.metix.ai/casebook`. The platform's web app
proxies that path to this image inside the cluster and adds the security
headers, including a strict CSP. This image is never reached from the internet
directly.

## Build

```bash
docker build -t harbor.openjobs-ai.com/openjobs-ai/casebook:<tag> .
```

The build fails if `tools/check-dist.mjs` finds an inline script, a script from
another host, or a storage key the Casebook does not own.

## Run in the cluster

`deploy/k8s.yaml` has the Deployment and a ClusterIP Service named
`job-platform-casebook`. Put them in the namespace of the platform's web app,
which reads this from its committed `.env`:

```
CASEBOOK_ORIGIN=http://job-platform-casebook:80
```

Without `CASEBOOK_ORIGIN`, `/casebook` answers 404 and nothing else changes,
which is also the rollback.

## What the server answers

| Request | Answer |
| --- | --- |
| `/casebook`, `/casebook/zh` | the catalog, `index.html` and `zh.html` |
| `/casebook/<slug>`, `/casebook/zh/<slug>` | `<slug>.html` |
| any path ending in `/` | 308 to the same path without it |
| `/casebook/_astro/*` | cached for a year; the names are content hashes |
| `/healthz` | 200, for the probes |
| anything else | 404 |

## Order of a first release

1. Build and push the image, apply `deploy/k8s.yaml`.
2. Deploy the platform's web app with `CASEBOOK_ORIGIN` set, on dev first.
3. Check `/casebook` and a few cases through the platform.
4. Then merge this branch into `main`.
