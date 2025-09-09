# Binrc Helm Charts

This repository serves as a Helm chart repository for the Binrc community, hosted at [https://charts.binrc.com/](https://charts.binrc.com/).

## Usage

To use the charts, add the repository to Helm:

```bash
helm repo add binrc https://charts.binrc.com/
helm repo update
```

Install a chart, e.g., HeadCNI:

```bash
helm install headcni binrc/headcni  # Latest version
helm install headcni binrc/headcni --version 1.0.0  # Specific version
```

## Available Charts

| Chart Name | Versions Available       | Description                                      |
|------------|--------------------------|--------------------------------------------------|
| headcni    | 1.0.0 (latest) | Kubernetes CNI plugin integrating Headscale and Tailscale |

## Source Code

- [HeadCNI Source](https://github.com/binrchq/headcni-helm)

## Support

- Issues: [GitHub Issues](https://github.com/binrchq/headcni-helm/issues)
- Email: [hello@binrc.com](mailto:hello@binrc.com)

## Hosting

Charts are hosted on the `gh-pages` branch and served via [https://charts.binrc.com/](https://charts.binrc.com/).
