# HeadCNI Helm Chart

<div align="center">

![HeadCNI](https://img.shields.io/badge/HeadCNI-v1.0.0-blue?style=for-the-badge&logo=kubernetes)
![Kubernetes](https://img.shields.io/badge/Kubernetes-1.20+-326CE5?style=for-the-badge&logo=kubernetes)
![Helm](https://img.shields.io/badge/Helm-3.0+-0F1689?style=for-the-badge&logo=helm)
![Tailscale](https://img.shields.io/badge/Tailscale-v1.100.0-FF6B6B?style=for-the-badge&logo=tailscale)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)

**基于 Tailscale v1.100.0 的生产级 Kubernetes CNI 插件**

[English](README.md) | 中文

[安装](#-安装) • [配置](#-配置) • [文档](#-文档) • [支持](#-支持)

</div>

---

## 🎯 概述

HeadCNI 是一个 Kubernetes CNI（容器网络接口）插件，集成了 [Headscale](https://headscale.net/) 和 [Tailscale](https://tailscale.com/)，通过 WireGuard 为 Pod 提供安全加密的网络连接。

### 为什么选择 HeadCNI？

- **🔒 零信任安全** - 所有 Pod 连接都使用 WireGuard 加密
- **🌐 多集群互联** - 无缝连接不同 Kubernetes 集群的 Pod
- **⚡ 高性能** - 针对混合网络环境优化的 MTU (1400)
- **🎯 无冲突** - 自定义 fwmark (0x90000) 和路由表避免与主机冲突
- **📈 生产就绪** - 经过实战测试，应用了 5 个关键补丁

### v1.0.0 新特性

- ✅ Tailscale 升级到 v1.100.0（从 v1.87.0）
- ✅ 默认 MTU 优化为 1400（从 1280）
- ✅ 5 个关键补丁支持多实例部署
- ✅ 简化配置（移除废弃的 \`mode\` 参数）
- ✅ 支持 Go 1.26

---

## 📦 安装

### 前置要求

- Kubernetes 1.20+（支持 k3s）
- Helm 3.0+
- 一个 [Headscale](https://headscale.net/) 服务器
- Linux 内核 4.19+

### 快速开始

#### 添加 Helm 仓库

\`\`\`bash
helm repo add binrc https://charts.binrc.com
helm repo update
\`\`\`

#### 安装 HeadCNI

\`\`\`bash
helm install headcni binrc/headcni \\
  --namespace kube-system \\
  --set config.headscale.url=https://your-headscale.example.com \\
  --set config.headscale.authKey=your-auth-key-here \\
  --create-namespace
\`\`\`

#### 验证安装

\`\`\`bash
# 检查 Pod
kubectl get pods -n kube-system -l app=headcni

# 查看日志
kubectl logs -n kube-system -l app=headcni --tail=50

# 验证 Tailscale 连接
kubectl exec -n kube-system ds/headcni -- tailscale status
\`\`\`

---

## ⚙️ 配置

### 最小配置

创建 \`values.yaml\`：

\`\`\`yaml
config:
  headscale:
    url: "https://headscale.example.com"
    authKey: "your-auth-key"
\`\`\`

使用自定义配置安装：

\`\`\`bash
helm install headcni binrc/headcni \\
  -f values.yaml \\
  --namespace kube-system
\`\`\`

### 常见配置示例

#### 1. 基础设置

\`\`\`yaml
config:
  headscale:
    url: "https://headscale.example.com"
    authKey: "your-auth-key"
  
  network:
    mtu: 1400  # 推荐用于混合环境
\`\`\`

#### 2. 自定义 CIDR 范围

\`\`\`yaml
config:
  network:
    podCIDR: "10.42.0.0/16"
    serviceCIDR: "10.43.0.0/16"
    mtu: 1400
\`\`\`

---

## 🔧 高级用法

### MTU 配置

根据您的环境选择 MTU：

| 环境 | MTU | 适用场景 |
|------|-----|----------|
| **1400** | 混合环境 | 数据中心 + 家庭网络（推荐） |
| **1420** | 数据中心 | 纯数据中心环境，MTU 1500 |
| **1280** | 保守配置 | 最大兼容性，移动网络 |

### 修复 Git Clone 问题

如果遇到 Git clone 超时（\`gnutls_handshake() failed\`），增加 MTU：

\`\`\`bash
helm upgrade headcni binrc/headcni \\
  --set config.tailscale.mtu=1400 \\
  --set config.network.mtu=1400 \\
  --reuse-values
\`\`\`

---

## 🚀 升级

\`\`\`bash
# 更新仓库
helm repo update

# 升级
helm upgrade headcni binrc/headcni \\
  --namespace kube-system \\
  --reuse-values

# 重启 Pod
kubectl rollout restart ds/headcni -n kube-system
\`\`\`

---

## 🔍 故障排查

### 检查安装

\`\`\`bash
# Pod 状态
kubectl get pods -n kube-system -l app=headcni

# 日志
kubectl logs -n kube-system -l app=headcni --tail=100 -f

# Tailscale 状态
kubectl exec -n kube-system ds/headcni -- tailscale status
\`\`\`

### 常见问题

#### Git Clone 超时

**症状**：\`gnutls_handshake() failed\`

**解决方案**：增加 MTU 到 1400

\`\`\`bash
helm upgrade headcni binrc/headcni --set config.tailscale.mtu=1400
\`\`\`

---

## 📚 文档

- **Chart 仓库**：https://charts.binrc.com
- **GitHub**：https://github.com/binrchq/headcni-helm
- **Issues**：https://github.com/binrchq/headcni-helm/issues

---

<div align="center">

**由 [binrc 团队](https://binrc.com) 用 ❤️ 制作**

⭐ 在 [GitHub](https://github.com/binrchq/headcni-helm) 上给我们 Star

</div>
