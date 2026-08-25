# Docker

The published image includes all extras (`mysql`, `mongodb`, `sentry`) and runs as a non-root user (`uid 1000`).

## Image

```
ghcr.io/astrum-studio/meilisync:<tag>
```

| Tag | When it is published |
| --- | --- |
| `latest` | Git tags `vX.Y.Z` (releases) |
| `0.1.5`, `0.1`, `0` | Semver from the same Git tag |
| `dev`, `main` | Branch builds |
| `sha-<git sha>` | Every successful image build |

Pull the latest release:

```bash
docker pull ghcr.io/astrum-studio/meilisync:latest
```

Images are built for `linux/amd64` and `linux/arm64`.

Optional Docker Hub publishing is described in [Publishing](publishing.md).

## Compose (production)

```yaml
services:
  meilisync:
    image: ghcr.io/astrum-studio/meilisync:latest
    restart: unless-stopped
    volumes:
      - ./config.yml:/app/config.yml:ro
      - ./data:/app/data
```

Point `progress.path` at a file inside `/app/data` so it survives recreates:

```yaml
progress:
  type: file
  path: data/progress.json
```

The image runs as uid **1000**. A bind-mounted `./data` must be writable by that user:

```bash
mkdir -p data
chown -R 1000:1000 data
```

## Compose (build locally)

```yaml
services:
  meilisync:
    build:
      context: .
      dockerfile: Dockerfile
    restart: unless-stopped
    volumes:
      - ./config.yml:/app/config.yml:ro
      - ./data:/app/data
```

The repository ships `docker-compose.yml` (image) and `docker-compose.dev.yml` (local build).

```bash
docker compose -f docker-compose.dev.yml up --build
```

## Config path

The process working directory is `/app`. `meilisync start` looks for `/app/config.yml` unless you override the command:

```yaml
command: ["meilisync", "-c", "/config/config.yml", "start"]
```

## Environment

The image does not take database credentials from environment variables. Put them in `config.yml` (and keep that file out of git).
