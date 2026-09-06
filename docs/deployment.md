# Deployment

## GitHub repository

Push the local `main` branch to a new repository and enable GitHub Pages with **GitHub Actions** as the source. The included Pages workflow validates dependencies, generates current rankings from `data/evidence`, builds the static site, and deploys it.

## Scheduled monitoring

The daily monitoring workflow:

1. queries GitHub for candidate open-source presentation systems;
2. checks canonical URLs for registered product snapshots;
3. uploads results as a 30-day workflow artifact.

It intentionally does not publish candidates or rewrite the registry. A maintainer reviews discoveries, verifies official facts, and creates a product snapshot through a pull request.

## Local release build

PowerShell:

```powershell
./scripts/build.ps1
```

Bash:

```bash
./scripts/build.sh
```

Generated files are placed under `public/` and are excluded from source control.

## Secrets

The discovery workflow uses GitHub's automatically provided token. Upstream evaluators that need paid model APIs should run in a separate, manually approved workflow with environment-scoped secrets. Never expose evaluation API keys to workflows triggered by untrusted pull requests.

