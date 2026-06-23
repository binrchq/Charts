# binrc Helm Charts

Official Helm Chart repository for binrc products.

**Repository URL**: https://charts.binrc.com

---

## 📦 Usage

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

| Chart | Version | App Version | Description |
|-------|---------|-------------|-------------|
| [headcni](https://github.com/binrchq/headcni-helm) | 1.0.0 | 1.0.0 | Kubernetes CNI plugin with Tailscale integration |

---

## 🚀 Quick Start

### Install HeadCNI

```bash
helm install headcni binrc/headcni \
  --namespace kube-system \
  --set config.headscale.url=https://your-headscale.com \
  --set config.headscale.authKey=your-auth-key
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

Visit https://charts.binrc.com for the full documentation and chart catalog.

---

## 🤝 Contributing

We welcome contributions! Please see individual chart repositories for contribution guidelines.

---

## 📄 License

Each chart has its own license. See the individual chart documentation for details.

---

## 🔗 Links

- **Website**: https://charts.binrc.com
- **GitHub**: https://github.com/binrchq/Charts
- **Organization**: https://github.com/binrchq

---

## 💬 Support

- Email: hello@binrc.com
- Issues: [GitHub Issues](https://github.com/binrchq/Charts/issues)

---

Made with ❤️ by [binrc Team](https://binrc.com)
