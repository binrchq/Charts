# HeadCNI Helm Chart

<div align="center">

![HeadCNI](https://img.shields.io/badge/HeadCNI-v1.0.0-blue?style=for-the-badge&logo=kubernetes)
![Kubernetes](https://img.shields.io/badge/Kubernetes-1.20+-326CE5?style=for-the-badge&logo=kubernetes)
![Helm](https://img.shields.io/badge/Helm-3.0+-0F1689?style=for-the-badge&logo=helm)
![Tailscale](https://img.shields.io/badge/Tailscale-v1.100.0-FF6B6B?style=for-the-badge&logo=tailscale)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)

**Production-ready Kubernetes CNI plugin powered by Tailscale v1.100.0**

English | [中文](README_CN.md)

[Installation](#-installation) • [Configuration](#-configuration) • [Documentation](#-documentation) • [Support](#-support)

</div>

---

## 🎯 Overview

HeadCNI is a Kubernetes CNI (Container Network Interface) plugin that integrates [Headscale](https://headscale.net/) and [Tailscale](https://tailscale.com/) to provide secure, encrypted pod networking with WireGuard.

### Why HeadCNI?

- **🔒 Zero Trust Security** - Every pod connection is encrypted with WireGuard
- **🌐 Multi-Cluster** - Connect pods across different Kubernetes clusters seamlessly
- **⚡ High Performance** - Optimized MTU (1400) for mixed network environments
- **🎯 No Conflicts** - Custom fwmark (0x90000) and routing tables prevent host conflicts
- **📈 Production Ready** - Battle-tested with 5 critical patches applied

### What's New in v1.0.0

- ✅ Tailscale upgraded to v1.100.0 (from v1.87.0)
- ✅ Default MTU optimized to 1400 (from 1280)
- ✅ 5 critical patches for multi-instance support
- ✅ Simplified configuration (removed deprecated `mode` parameter)
- ✅ Go 1.26 support

---

## 📦 Installation

### Prerequisites

- Kubernetes 1.20+ (k3s supported)
- Helm 3.0+
- A [Headscale](https://headscale.net/) server
- Linux kernel 4.19+

### Quick Start

#### Add Helm Repository

```bash
helm repo add binrc https://charts.binrc.com
helm repo update
```

#### Install HeadCNI

```bash
helm install headcni binrc/headcni \
  --namespace kube-system \
  --set config.headscale.url=https://your-headscale.example.com \
  --set config.headscale.authKey=your-auth-key-here \
  --create-namespace
```

#### Verify Installation

```bash
# Check pods
kubectl get pods -n kube-system -l app=headcni

# Check logs
kubectl logs -n kube-system -l app=headcni --tail=50

# Verify Tailscale connectivity
kubectl exec -n kube-system ds/headcni -- tailscale status
```

---

## ⚙️ Configuration

### Minimal Configuration

Create a `values.yaml`:

```yaml
config:
  headscale:
    url: "https://headscale.example.com"
    authKey: "your-auth-key"
```

Install with custom values:

```bash
helm install headcni binrc/headcni \
  -f values.yaml \
  --namespace kube-system
```

### Common Configuration Examples

#### 1. Basic Setup

```yaml
config:
  headscale:
    url: "https://headscale.example.com"
    authKey: "your-auth-key"
  
  network:
    mtu: 1400  # Recommended for mixed environments
```

#### 2. Custom CIDR Ranges

```yaml
config:
  network:
    podCIDR: "10.42.0.0/16"
    serviceCIDR: "10.43.0.0/16"
    mtu: 1400
```

#### 3. Resource Limits

```yaml
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 128Mi
```

#### 4. High Availability

```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: node-role.kubernetes.io/control-plane
          operator: Exists
```

### Full Configuration Reference

<details>
<summary>Click to expand</summary>

| Parameter | Description | Default |
|-----------|-------------|---------|
| `image.repository` | Container image repository | `binrc/headcni` |
| `image.tag` | Container image tag | `v1.0.0` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `config.headscale.url` | Headscale server URL | `""` (required) |
| `config.headscale.authKey` | Authentication key | `""` (required) |
| `config.tailscale.acceptDNS` | Accept Headscale DNS | `false` |
| `config.tailscale.interfaceName` | Interface name | `headcni01` |
| `config.network.podCIDR` | Pod CIDR range | Auto-detect |
| `config.network.serviceCIDR` | Service CIDR range | Auto-detect |
| `config.network.mtu` | Network MTU | `1400` |
| `rbac.create` | Create RBAC resources | `true` |
| `resources.limits.cpu` | CPU limit | `500m` |
| `resources.limits.memory` | Memory limit | `512Mi` |

</details>

---

## 🔧 Advanced Usage

### MTU Configuration

Choose MTU based on your environment:

| Environment | MTU | Use Case |
|-------------|-----|----------|
| **1400** | Mixed | Datacenter + Home networks (Recommended) |
| **1420** | Datacenter | Pure datacenter with MTU 1500 |
| **1280** | Conservative | Maximum compatibility, mobile networks |

```yaml
config:
  tailscale:
    mtu: 1400
  network:
    mtu: 1400  # Should match tailscale.mtu
```

### Git Clone Fix

If you experience Git clone timeouts (`gnutls_handshake() failed`), increase MTU:

```bash
helm upgrade headcni binrc/headcni \
  --set config.tailscale.mtu=1400 \
  --set config.network.mtu=1400 \
  --reuse-values
```

### Multi-Cluster Setup

HeadCNI supports connecting pods across multiple Kubernetes clusters:

1. Install HeadCNI on each cluster with different `authKey`
2. All clusters should point to the same Headscale server
3. Pods can communicate using Tailscale IPs across clusters

---

## 🚀 Upgrade

### Upgrade to v1.0.0

```bash
# Update repository
helm repo update

# Upgrade
helm upgrade headcni binrc/headcni \
  --namespace kube-system \
  --reuse-values

# Restart pods
kubectl rollout restart ds/headcni -n kube-system
```

### Migration from Legacy Versions

If upgrading from pre-v1.0.0:

1. **Remove `mode` parameter** - Only daemon mode is supported
2. **Update MTU** - Default changed from 1280 to 1400
3. **Check patches** - All 5 patches are now included

```bash
# Update values.yaml (remove mode parameter)
helm upgrade headcni binrc/headcni \
  --set config.tailscale.mtu=1400 \
  --set config.network.mtu=1400 \
  --namespace kube-system
```

---

## 🔍 Troubleshooting

### Check Installation

```bash
# Pod status
kubectl get pods -n kube-system -l app=headcni

# Logs
kubectl logs -n kube-system -l app=headcni --tail=100 -f

# Tailscale status
kubectl exec -n kube-system ds/headcni -- tailscale status
```

### Verify Patches

All 5 patches should be active:

```bash
# 1. fwmark 0x90000
kubectl exec -n kube-system ds/headcni -- \
  ip rule list | grep 0x90000

# 2. Route table 53
kubectl exec -n kube-system ds/headcni -- \
  ip route show table 53

# 3. Priority 3210
kubectl exec -n kube-system ds/headcni -- \
  ip rule list | grep 3210

# 4. Chain names ts-tune-*
kubectl exec -n kube-system ds/headcni -- \
  iptables -t nat -L | grep ts-tune

# 5. MTU 1400
kubectl exec -n kube-system ds/headcni -- \
  ip link show tailscale1 | grep "mtu 1400"
```

### Common Issues

#### Git Clone Timeout

**Symptom**: `gnutls_handshake() failed: The TLS connection was non-properly terminated`

**Solution**: Increase MTU to 1400

```bash
helm upgrade headcni binrc/headcni \
  --set config.tailscale.mtu=1400
```

#### Route Conflicts with Host Tailscale

**Symptom**: Routing issues when host also runs Tailscale

**Solution**: v1.0.0 uses custom route table 53 and fwmark 0x90000 - no conflicts

#### Pods Cannot Communicate

**Symptom**: Connectivity issues between pods

**Solution**: Check MTU consistency

```bash
# All should show same MTU
kubectl exec -n kube-system ds/headcni -- ip link show
```

---

## 📚 Documentation

- **Installation Guide**: [docs/installation.md](docs/installation.md)
- **Configuration Reference**: [docs/configuration.md](docs/configuration.md)
- **Architecture**: [docs/architecture.md](docs/architecture.md)
- **Troubleshooting**: [docs/troubleshooting.md](docs/troubleshooting.md)

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## 🔗 Links

- **Chart Repository**: https://charts.binrc.com
- **GitHub**: https://github.com/binrchq/headcni-helm
- **Issues**: https://github.com/binrchq/headcni-helm/issues
- **Headscale**: https://headscale.net/
- **Tailscale**: https://tailscale.com/

---

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/binrchq/headcni-helm/issues)
- **Discussions**: [GitHub Discussions](https://github.com/binrchq/headcni-helm/discussions)
- **Email**: hello@binrc.com

---

<div align="center">

**Made with ❤️ by [binrc Team](https://binrc.com)**

⭐ Star us on [GitHub](https://github.com/binrchq/headcni-helm)

</div>
