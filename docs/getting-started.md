# Getting Started with binrc Helm Charts

Welcome to binrc Helm Charts! This guide will help you get started.

---

## 📦 Prerequisites

Before you begin, ensure you have:

- **Kubernetes cluster** (1.20+)
- **Helm 3.0+** installed
- **kubectl** configured

---

## 🚀 Installation

### Step 1: Add Helm Repository

```bash
helm repo add binrc https://charts.binrc.com
helm repo update
```

### Step 2: Search Available Charts

```bash
helm search repo binrc

# Example output:
# NAME           CHART VERSION   APP VERSION   DESCRIPTION
# binrc/headcni  1.0.0          1.0.0         Kubernetes CNI plugin with Tailscale
```

### Step 3: Install a Chart

```bash
helm install my-release binrc/<chart-name>

# Example: Install HeadCNI
helm install headcni binrc/headcni --namespace kube-system
```

---

## ⚙️ Configuration

### View Default Values

```bash
helm show values binrc/<chart-name>
```

### Custom Configuration

Create a `values.yaml` file:

```yaml
# Example for HeadCNI
config:
  headscale:
    url: "https://your-headscale.com"
    authKey: "your-auth-key"
  
  network:
    mtu: 1400
```

Install with custom values:

```bash
helm install my-release binrc/<chart-name> -f values.yaml
```

Or use `--set`:

```bash
helm install my-release binrc/<chart-name> \
  --set config.headscale.url=https://your-headscale.com \
  --set config.headscale.authKey=your-key
```

---

## 🔄 Upgrading

### Update Repository

```bash
helm repo update
```

### Upgrade Release

```bash
helm upgrade my-release binrc/<chart-name>

# Keep existing values
helm upgrade my-release binrc/<chart-name> --reuse-values

# Upgrade with new values
helm upgrade my-release binrc/<chart-name> -f new-values.yaml
```

---

## 🗑️ Uninstallation

```bash
helm uninstall my-release
```

---

## 📊 Monitoring

### Check Release Status

```bash
helm status my-release
helm list
```

### View Resources

```bash
kubectl get all -l app.kubernetes.io/instance=my-release
```

---

## 🐛 Troubleshooting

### Common Issues

#### Repository Not Found

```bash
# Re-add the repository
helm repo remove binrc
helm repo add binrc https://charts.binrc.com
helm repo update
```

#### Installation Fails

```bash
# Check dry-run
helm install my-release binrc/<chart-name> --dry-run --debug

# Check logs
kubectl logs -l app.kubernetes.io/instance=my-release
```

---

## 📚 Next Steps

- Read chart-specific documentation in `charts/<chart-name>/README.md`
- Check [Contributing Guide](contributing.md) if you want to contribute
- Visit https://charts.binrc.com for more information

---

## 💬 Support

Need help?

- **Issues**: [GitHub Issues](https://github.com/binrchq/Charts/issues)
- **Email**: hello@binrc.com

---

Happy charting! 🎉
