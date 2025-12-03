# Azure Deployment Notes (BeatOven)

This directory documents the minimal Azure resources expected when using the GitHub Actions workflow in `.github/workflows/deploy-azure.yml`.

## Target Resources
- **Container Registry**: Stores the Docker image built from the repo. Use Azure Container Registry (recommended) or GitHub Container Registry with the login server provided as `REGISTRY_LOGIN_SERVER`.
- **App Service Plan**: Hosts the Web App for Containers. Choose a Linux plan sized for your traffic profile.
- **Web App for Containers**: Runs the BeatOven container image. Name is provided via `AZURE_WEBAPP_NAME`.

## Required Secrets (set in GitHub)
- `AZURE_CREDENTIALS`: JSON output from `az ad sp create-for-rbac` for workflow authentication.
- `AZURE_RESOURCE_GROUP`: Resource group containing the web app and registry.
- `AZURE_WEBAPP_NAME`: Target Web App for Containers name.
- `REGISTRY_LOGIN_SERVER`: Container registry server (e.g., `myregistry.azurecr.io`).
- `REGISTRY_USERNAME` / `REGISTRY_PASSWORD`: Credentials for the registry (service principal, ACR admin, or GHCR PAT as appropriate).

## Deployment Flow
1. Workflow logs in to Azure using `AZURE_CREDENTIALS`.
2. Tests run to keep deployments deterministic.
3. Docker image builds from the root `Dockerfile` and is pushed to the registry.
4. Web App is pointed to the new image tag and restarted for zero-drift rollout.

## Observability Hooks
- Azure App Service captures container stdout/stderr for immediate logging.
- Hook Azure Monitor or Application Insights to the Web App for metrics/tracing when ready.

Ensure network access and configuration (e.g., VNet, firewall) align with your environment before enabling production traffic.
