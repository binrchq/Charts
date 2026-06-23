# Contributing to binrc Helm Charts

Thank you for considering contributing to binrc Helm Charts!

---

## 📋 How to Contribute

### Reporting Issues

- Use GitHub Issues
- Provide clear description
- Include steps to reproduce
- Specify chart version and Kubernetes version

### Submitting Changes

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a Pull Request

---

## 🔧 Development Workflow

### 1. Clone the Repository

```bash
git clone https://github.com/binrchq/Charts.git
cd Charts
```

### 2. Create a Branch

```bash
git checkout -b feature/my-feature
```

### 3. Make Changes

```bash
# Edit files in charts/<chart-name>/
```

### 4. Test Your Changes

```bash
# Lint
helm lint charts/<chart-name>

# Test all charts
./scripts/test-all-charts.sh

# Template test
helm template test charts/<chart-name>
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat(chart-name): Add feature X

- Description of change
- Why this change is needed
"
```

### 6. Push and Create PR

```bash
git push origin feature/my-feature
```

Then create a Pull Request on GitHub.

---

## 📝 Commit Message Guidelines

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat(chart-name): Add new feature`
- `fix(chart-name): Fix bug`
- `docs(chart-name): Update documentation`
- `chore: Update dependencies`

---

## ✅ Pull Request Checklist

- [ ] Chart version bumped (if needed)
- [ ] CHANGELOG.md updated (if applicable)
- [ ] Documentation updated
- [ ] Tests pass
- [ ] Follows Helm best practices

---

## 🎯 Chart Guidelines

### Structure

```
charts/my-chart/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ...
├── README.md
└── CHANGELOG.md (optional)
```

### Best Practices

- Use semantic versioning
- Document all values
- Provide examples
- Follow Kubernetes naming conventions
- Include resource limits/requests
- Support multiple configurations

---

## 📚 Resources

- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [binrc Charts](https://charts.binrc.com)

---

Thank you for contributing! 🎉
