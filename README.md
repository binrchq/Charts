# binrc Helm Charts

Official Helm Charts repository for binrc products - Monorepo architecture.

**Repository URL**: https://charts.binrc.com

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Charts](https://img.shields.io/badge/charts-1-blue.svg)](#available-charts)

---

## 📦 Quick Start

Add the binrc Helm repository:

```bash
helm repo add binrc https://charts.binrc.com
helm repo update
```

Search available charts:

```bash
helm search repo binrc
```

---

## 📚 Available Charts

| Chart | Version | App Version | Description | Status |
|-------|---------|-------------|-------------|--------|
| [headcni](./charts/headcni) | 1.0.0 | 1.0.0 | Kubernetes CNI plugin with Tailscale integration | ✅ Stable |

---

## 🚀 Usage Examples

### Install HeadCNI

```bash
helm install headcni binrc/headcni \
  --namespace kube-system \
  --set config.headscale.url=https://your-headscale.com \
  --set config.headscale.authKey=your-auth-key \
  --create-namespace
```

### View Chart Information

```bash
# Show chart metadata
helm show chart binrc/headcni

# Show default values
helm show values binrc/headcni

# Show README
helm show readme binrc/headcni
```

---

## 📖 Documentation

- **Website**: https://charts.binrc.com
- **Getting Started**: [docs/getting-started.md](docs/getting-started.md)
- **Contributing**: [docs/contributing.md](docs/contributing.md)

---

## 🏗️ Repository Structure

```
Charts/
├── charts/              # All Helm Charts source code
│   ├── headcni/        # HeadCNI Chart
│   └── ...             # More charts
│
├── scripts/             # Automation scripts
│   ├── publish-chart.sh
│   └── test-all-charts.sh
│
├── docs/                # Documentation
│   ├── getting-started.md
│   └── contributing.md
│
└── .github/             # CI/CD workflows
    └── workflows/
```

---

## 🔧 Development

### Prerequisites

- Helm 3.0+
- kubectl
- Access to a Kubernetes cluster

### Test a Chart Locally

```bash
# Lint
helm lint charts/headcni

# Template
helm template test charts/headcni

# Dry-run install
helm install test charts/headcni --dry-run --debug
```

### Test All Charts

```bash
./scripts/test-all-charts.sh
```

### Publish a Chart

```bash
./scripts/publish-chart.sh <chart-name>

# Example
./scripts/publish-chart.sh headcni
```

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/contributing.md) for guidelines.

### Adding a New Chart

1. Create a new directory under `charts/`
2. Follow the standard Helm chart structure
3. Add documentation (README.md)
4. Test locally
5. Submit a Pull Request

---

## 📝 Chart Development Guidelines

- Follow [Helm best practices](https://helm.sh/docs/chart_best_practices/)
- Include comprehensive README.md
- Provide sensible default values
- Document all values in values.yaml
- Include examples in README

---

## 📄 License

Each chart has its own license. See individual chart directories for details.

---

## 🔗 Links

- **Website**: https://charts.binrc.com
- **GitHub**: https://github.com/binrchq/Charts
- **Organization**: https://github.com/binrchq

---

## 💬 Support

- **Email**: hello@binrc.com
- **Issues**: [GitHub Issues](https://github.com/binrchq/Charts/issues)
- **Discussions**: [GitHub Discussions](https://github.com/binrchq/Charts/discussions)

---

Made with ❤️ by [binrc Team](https://binrc.com)
