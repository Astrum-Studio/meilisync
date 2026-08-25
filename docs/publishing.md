# Publishing

Releases are driven by Git tags. CI builds the sdist/wheel with **uv + hatchling**, publishes to **PyPI**, pushes a **GHCR** image, and deploys **MkDocs** to GitHub Pages.

## One-time GitHub / PyPI setup

### GitHub Pages

Repo **Settings → Pages → Build and deployment → Source: GitHub Actions**.

After the first successful `docs` workflow on `main`, the site is at:

[https://astrum-studio.github.io/meilisync/](https://astrum-studio.github.io/meilisync/)

### PyPI trusted publishing

No long-lived PyPI token is stored in GitHub.

1. Create the project on [PyPI](https://pypi.org/) (name `meilisync` if you own it, otherwise change `project.name` in `pyproject.toml`).
2. **PyPI → Manage → Publishing → GitHub**
    - Owner: `Astrum-Studio`
    - Repository: `meilisync`
    - Workflow: `publish.yml`
    - Environment: `pypi`
3. In GitHub: **Settings → Environments → `pypi`** (create it). Optionally require reviewers.

The `publish` workflow uses OIDC (`id-token: write`) and `pypa/gh-action-pypi-publish`.

### GitHub Container Registry

GHCR works with `GITHUB_TOKEN`. No extra secrets.

The image is public if the package is set to public: **Packages → meilisync → Package settings → Change visibility**.

First push happens automatically from `.github/workflows/docker.yml`.

### Docker Hub (optional)

If you also want `docker.io/<user>/meilisync`:

1. Create a [Docker Hub](https://hub.docker.com/) access token
2. GitHub **Settings → Secrets → `DOCKERHUB_TOKEN`**
3. GitHub **Settings → Variables → `DOCKERHUB_USERNAME`**

When the variable is set, the Docker workflow logs in and adds Hub tags next to GHCR.

## Cut a release

1. Update `CHANGELOG.md`.
2. Bump the version (writes `meilisync/version.py` via Hatch):

    ```bash
    uv run hatch version 0.1.6
    # or: uv run hatch version minor
    ```

3. Commit, tag, push:

    ```bash
    git add meilisync/version.py CHANGELOG.md
    git commit -m "release: 0.1.6"
    git tag v0.1.6
    git push origin dev
    git push origin v0.1.6
    ```

The tag `v0.1.6` triggers:

| Workflow | Result |
| --- | --- |
| `publish.yml` | `uv build` → PyPI + GitHub Release with wheels |
| `docker.yml` | `ghcr.io/astrum-studio/meilisync:0.1.6` and `:latest` |
| `ci.yml` | lint, tests, `uv build` |

The version in the built wheel comes from Hatch reading `meilisync/version.py`. Keep the Git tag in sync (`v` + that version).

## Local package build

```bash
uv build
uvx twine check dist/*
```

Artifacts land in `dist/`. Do not upload them by hand unless CI is unavailable.

## Local image build

```bash
docker build -t meilisync:local .
docker run --rm meilisync:local meilisync version
```
