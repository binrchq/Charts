#!/usr/bin/env python3
"""
生成 charts.binrc.com 的 index.html。
所有数据均来自仓库真实内容：index.yaml（版本/摘要）、headcni-1.1.0.tgz（values.yaml）、
以及 Charts 仓库的 git 提交记录（版本说明）。不包含任何虚构项目、API 或评分。
"""
import json
import os
import re
import subprocess
import tarfile

REPO = "/coreon/tails/Charts"
CHART = "headcni"
OUT = os.path.join(REPO, "index.html")

# ---------------------------------------------------------------- 真实数据
with open(os.path.join(REPO, "index.yaml")) as f:
    import yaml
    index = yaml.safe_load(f)

# 版本说明：取自 Charts 仓库 main 分支的真实提交信息
NOTES = {
    "1.1.0": ("netns 隔离架构", "tailscaled 迁入 /var/run/netns/headcni；回归官方 tailscale.com v1.104.4，退役全部 5 个内核补丁；修复 cniPlugins 多行 JSON 导致的 Chart 渲染失败"),
    "1.0.10": ("镜像更新", "镜像升级至 1.0.10"),
    "1.0.9": ("IP 释放修复", "修复 Pod 删除时 IPAM 租约释放时机"),
    "1.0.8": ("MTU 对齐", "默认 MTU 统一为 1280"),
    "1.0.7": ("Tailscale v1.98.4", "随 Tailscale v1.98.4 更新"),
    "1.0.6": ("常规更新", "chart 版本更新"),
    "1.0.5": ("常规更新", "chart 版本更新"),
    "1.0.4": ("常规更新", "chart 版本更新"),
    "1.0.3": ("结构调整", "合并 CNI plugin 容器、简化镜像仓库配置、MTU 热更新链路"),
    "1.0.2": ("常规更新", "chart 版本更新"),
    "1.0.0": ("首个版本", "HeadCNI Chart 首次发布"),
}

releases = []
for e in index.get("entries", {}).get(CHART, []):
    v = e.get("version", "")
    title, note = NOTES.get(v, ("更新", "chart 更新"))
    releases.append({
        "version": v,
        "appVersion": e.get("appVersion", ""),
        "created": (e.get("created") or "")[:10],
        "digest": (e.get("digest") or "")[:16],
        "url": (e.get("urls") or [""])[0],
        "title": title,
        "note": note,
        "latest": False,
    })
if releases:
    releases[0]["latest"] = True

# values.yaml：从最新 tgz 中取出原文
tgz = os.path.join(REPO, f"{CHART}-1.1.0.tgz")
with tarfile.open(tgz, "r:gz") as tar:
    values_yaml = tar.extractfile(f"{CHART}/values.yaml").read().decode("utf-8")

# 配置项：全部来自 values.yaml 实际存在的键
VALUE_ROWS = [
    ("镜像", "image.repository", "binrc/headcni:1.1.0", "daemon 镜像"),
    ("镜像", "image.cniPluginRepository", "binrc/headcni-plugin:1.1.0", "CNI 插件镜像"),
    ("镜像", "image.pullPolicy", "IfNotPresent", "拉取策略"),
    ("控制面", "config.headscale.url", "—", "Headscale 地址（必填）"),
    ("控制面", "config.headscale.timeout", "30s", "API 超时"),
    ("控制面", "config.headscale.retries", "3", "API 重试次数"),
    ("Tailscale", "config.tailscale.mode", "daemon", "daemon=自管 tailscaled；host=复用宿主实例"),
    ("Tailscale", "config.tailscale.url", "—", "Headscale 地址（daemon 模式）"),
    ("Tailscale", "config.tailscale.mtu", "1280", "TUN 接口 MTU"),
    ("Tailscale", "config.tailscale.acceptDNS", "false", "是否接受 MagicDNS"),
    ("Tailscale", "config.tailscale.interfaceName", "headcni01", "TUN 接口名"),
    ("隔离", "config.netns.enabled", "true", "开启 netns 隔离（1.1.0 起推荐）"),
    ("隔离", "config.netns.name", "headcni", "命名空间名，路径 /var/run/netns/<name>"),
    ("隔离", "config.netns.hostVeth", "hcni0", "宿主侧 veth"),
    ("隔离", "config.netns.peerVeth", "hcni1", "netns 侧 veth"),
    ("隔离", "config.netns.peerCIDR", "169.254.10.0/30", "veth 互联网段"),
    ("隔离", "config.netns.tunPort", "41641", "netns 内 tailscaled 监听端口"),
    ("网络", "config.network.podCIDR", "10.42.0.0/16", "集群 Pod 网段"),
    ("网络", "config.network.serviceCIDR", "10.43.0.0/16", "Service 网段"),
    ("网络", "config.network.mtu", "1230", "网卡 MTU"),
    ("IPAM", "config.ipam.type", "host-local", "host-local 或 headcni-ipam"),
    ("IPAM", "config.ipam.gcInterval", "1h", "租约回收周期"),
    ("监控", "config.monitoring.enabled", "true", "内置 Prometheus 指标"),
    ("监控", "config.monitoring.port", "9001", "指标端口"),
    ("调度", "priorityClassName", "system-node-critical", "优先级类"),
    ("调度", "tolerations[0].operator", "Exists", "容忍所有 NoSchedule 污点"),
]

latest = releases[0]["version"] if releases else "1.1.0"
stats = {
    "charts": len(index.get("entries", {})),
    "versions": len(releases),
    "latest": latest,
}

CSS = r"""
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0a0e14; --bg-2:#0d1219; --panel:#111823; --panel-2:#151d2a;
  --line:rgba(148,163,184,.14); --line-2:rgba(148,163,184,.24);
  --fg:#e8eef7; --fg-2:#a8b6c8; --fg-3:#6f8096;
  --acc:#10b981; --acc-2:#34d399; --acc-dim:rgba(16,185,129,.1);
  --blue:#60a5fa; --amber:#fbbf24;
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
  --sans:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,"PingFang SC","Hiragino Sans GB","Noto Sans SC","Source Han Sans SC","Microsoft YaHei",sans-serif;
  --r:10px; --r-lg:14px;
}
html{scroll-behavior:smooth;color-scheme:dark}
body{
  font-family:var(--sans);background:var(--bg);color:var(--fg);
  line-height:1.6;-webkit-font-smoothing:antialiased;
  background-image:
    radial-gradient(900px 420px at 12% -8%,rgba(16,185,129,.07),transparent 60%),
    radial-gradient(760px 380px at 92% 4%,rgba(96,165,250,.05),transparent 60%);
  background-attachment:fixed;
}
a{color:inherit;text-decoration:none}
code,pre,.mono{font-family:var(--mono);font-variant-ligatures:none}
.wrap{max-width:1120px;margin:0 auto;padding:0 24px}
.hr{height:1px;background:var(--line);border:0}

/* ---------- header ---------- */
header.top{
  position:sticky;top:0;z-index:50;
  backdrop-filter:blur(14px) saturate(140%);
  background:rgba(10,14,20,.78);
  border-bottom:1px solid var(--line);
}
.top-in{display:flex;align-items:center;gap:20px;height:58px}
.brand{display:flex;align-items:center;gap:9px;font-weight:650;letter-spacing:-.01em;font-size:15px}
.brand-mark{
  width:22px;height:22px;border-radius:6px;flex:0 0 auto;
  background:linear-gradient(145deg,var(--acc),#059669);
  display:grid;place-items:center;font-size:12px;font-weight:800;color:#062017;
}
.brand small{color:var(--fg-3);font-weight:500;font-size:12px;letter-spacing:.04em}
nav.main{display:flex;gap:4px;margin-left:auto}
nav.main a{
  font-size:13px;color:var(--fg-2);padding:6px 11px;border-radius:7px;
  transition:background .15s,color .15s;
}
nav.main a:hover{background:rgba(148,163,184,.1);color:var(--fg)}
.top-cta{
  display:inline-flex;align-items:center;gap:6px;font-size:13px;
  padding:7px 13px;border-radius:8px;border:1px solid var(--line-2);
  color:var(--fg);background:rgba(148,163,184,.06);transition:.15s;
}
.top-cta:hover{background:rgba(148,163,184,.13);border-color:rgba(148,163,184,.34)}

/* ---------- hero ---------- */
.hero{padding:64px 0 44px}
.eyebrow{
  display:inline-flex;align-items:center;gap:7px;
  font-family:var(--mono);font-size:11px;letter-spacing:.13em;text-transform:uppercase;
  color:var(--acc-2);padding:5px 10px;border-radius:999px;
  border:1px solid rgba(16,185,129,.24);background:var(--acc-dim);
}
.eyebrow .dot{width:5px;height:5px;border-radius:50%;background:var(--acc);box-shadow:0 0 0 3px rgba(16,185,129,.16)}
h1{
  font-size:clamp(27px,5vw,46px);line-height:1.1;letter-spacing:-.03em;
  font-weight:680;margin:18px 0 14px;
}
h1 .thin{color:var(--fg-3);font-weight:400}
.lede{color:var(--fg-2);font-size:15.5px;max-width:640px}
.lede b{color:var(--fg);font-weight:600}
.stats{display:flex;flex-wrap:wrap;gap:0;margin:30px 0 0;border:1px solid var(--line);border-radius:var(--r);overflow:hidden;background:var(--panel)}
.stat{flex:1 1 140px;padding:15px 18px;border-right:1px solid var(--line)}
.stat:last-child{border-right:0}
.stat .v{font-family:var(--mono);font-size:21px;font-weight:600;letter-spacing:-.02em}
.stat .k{font-size:11.5px;color:var(--fg-3);letter-spacing:.05em;text-transform:uppercase;margin-top:2px}

/* ---------- code block ---------- */
.code{
  position:relative;background:#080b10;border:1px solid var(--line);
  border-radius:var(--r);overflow:hidden;min-width:0;
}
.code-hd{
  display:flex;align-items:center;gap:8px;padding:9px 13px;
  border-bottom:1px solid var(--line);background:rgba(148,163,184,.035);
}
.code-hd .t{font-family:var(--mono);font-size:11.5px;color:var(--fg-3);letter-spacing:.05em}
.code pre{padding:15px 16px;overflow-x:auto;font-size:12.9px;line-height:1.75;color:#d6e2f0}
.code pre .cm{color:#5b6b80}
.code pre .fl{color:var(--acc-2)}
.copy{
  margin-left:auto;font-family:var(--mono);font-size:11px;color:var(--fg-3);
  background:transparent;border:1px solid var(--line-2);border-radius:6px;
  padding:3px 9px;cursor:pointer;transition:.15s;
}
.copy:hover{color:var(--fg);border-color:rgba(148,163,184,.44)}

/* ---------- sections ---------- */
section{padding:52px 0;border-top:1px solid var(--line)}
.sec-hd{margin-bottom:26px}
.sec-eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--fg-3)}
h2{font-size:23px;letter-spacing:-.02em;font-weight:640;margin:7px 0 8px}
.sec-sub{color:var(--fg-2);font-size:14px;max-width:660px}

/* ---------- chart card ---------- */
.chart-card{
  border:1px solid var(--line);border-radius:var(--r-lg);background:var(--panel);
  padding:22px 24px;
}
.chart-card h3{font-size:19px;letter-spacing:-.01em;font-weight:640;display:flex;align-items:center;gap:9px}
.chart-card .desc{color:var(--fg-2);font-size:13.5px;margin-top:8px;max-width:560px}
.pill{
  font-family:var(--mono);font-size:10.5px;letter-spacing:.05em;
  padding:3px 8px;border-radius:999px;border:1px solid var(--line-2);color:var(--fg-2);
}
.pill.acc{color:var(--acc-2);border-color:rgba(16,185,129,.3);background:var(--acc-dim)}
.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(128px,1fr));gap:1px;background:var(--line);border:1px solid var(--line);border-radius:var(--r);margin-top:18px;overflow:hidden}
.fact{background:var(--panel);padding:12px 14px}
.fact .k{font-size:11px;color:var(--fg-3);letter-spacing:.05em;text-transform:uppercase}
.fact .v{font-family:var(--mono);font-size:13.5px;margin-top:3px}
.links{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px}
.links a{
  font-size:12.5px;padding:7px 12px;border-radius:8px;border:1px solid var(--line-2);
  color:var(--fg-2);transition:.15s;
}
.links a:hover{color:var(--fg);border-color:rgba(148,163,184,.42);background:rgba(148,163,184,.06)}

/* ---------- topology ---------- */
.topo{display:grid;grid-template-columns:1fr 1fr;gap:0;border:1px solid var(--line);border-radius:var(--r-lg);overflow:hidden;background:var(--panel)}
.ns{padding:20px 22px}
.ns+.ns{border-left:1px dashed var(--line-2)}
.ns-hd{display:flex;align-items:center;gap:8px;margin-bottom:14px}
.ns-hd .tag{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--fg-3)}
.ns-hd .nm{font-family:var(--mono);font-size:12.5px;color:var(--fg)}
.iface{
  display:flex;align-items:baseline;gap:10px;padding:9px 12px;border-radius:8px;
  border:1px solid var(--line);background:var(--bg-2);margin-bottom:8px;
  font-family:var(--mono);font-size:12.2px;
}
.iface .n{color:var(--fg);min-width:96px}
.iface .a{color:var(--fg-2)}
.iface.hi{border-color:rgba(16,185,129,.34);background:rgba(16,185,129,.06)}
.iface.blue{border-color:rgba(96,165,250,.3);background:rgba(96,165,250,.05)}
.ns-note{font-size:12px;color:var(--fg-3);margin-top:10px;line-height:1.6}
.veth-note{
  grid-column:1/-1;border-top:1px dashed var(--line-2);padding:12px 22px;
  font-size:12.2px;color:var(--fg-3);display:flex;gap:10px;align-items:center;flex-wrap:wrap;
}
.paths{display:grid;gap:10px;margin-top:16px}
.path{
  display:grid;grid-template-columns:88px 1fr;gap:14px;align-items:start;
  padding:13px 16px;border:1px solid var(--line);border-radius:var(--r);background:var(--panel);
}
.path .lbl{font-family:var(--mono);font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--acc-2);padding-top:2px}
.path .flow{font-family:var(--mono);font-size:12.2px;color:var(--fg-2);line-height:1.85}
.path .flow b{color:var(--fg);font-weight:600}
.path .flow .arrow{color:var(--fg-3)}

/* ---------- builder ---------- */
.builder{display:grid;grid-template-columns:minmax(280px,.85fr) 1.15fr;gap:20px;align-items:start;min-width:0}
.form{border:1px solid var(--line);border-radius:var(--r-lg);background:var(--panel);padding:18px 20px}
.field{margin-bottom:14px}
.field:last-child{margin-bottom:0}
.field label{display:block;font-size:12px;color:var(--fg-2);margin-bottom:5px;letter-spacing:.01em}
.field label .mono{color:var(--fg-3);font-size:11px}
.field input[type=text],.field input[type=number],.field select{
  width:100%;background:#080b10;border:1px solid var(--line-2);border-radius:7px;
  color:var(--fg);font-family:var(--mono);font-size:12.5px;padding:8px 10px;outline:none;
  transition:border-color .15s;
}
.field input:focus,.field select:focus{border-color:rgba(16,185,129,.5)}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.check{display:flex;align-items:center;gap:9px;cursor:pointer;font-size:12.5px;color:var(--fg-2)}
.check input{appearance:none;width:34px;height:19px;border-radius:999px;background:#1b2432;border:1px solid var(--line-2);position:relative;cursor:pointer;transition:.18s;flex:0 0 auto}
.check input:checked{background:rgba(16,185,129,.28);border-color:rgba(16,185,129,.55)}
.check input::after{content:"";position:absolute;top:2px;left:2px;width:13px;height:13px;border-radius:50%;background:#8296ad;transition:.18s}
.check input:checked::after{left:17px;background:var(--acc-2)}
.out{display:grid;gap:14px;min-width:0}

/* ---------- values table ---------- */
.toolbar{display:flex;gap:10px;align-items:center;margin-bottom:14px;flex-wrap:wrap}
.search{
  flex:1 1 240px;display:flex;align-items:center;gap:8px;
  background:#080b10;border:1px solid var(--line-2);border-radius:8px;padding:7px 11px;
}
.search input{background:transparent;border:0;outline:none;color:var(--fg);font-family:var(--mono);font-size:12.5px;width:100%}
.search span{color:var(--fg-3);font-size:12px}
.tbl-wrap{border:1px solid var(--line);border-radius:var(--r);overflow-x:auto;overflow-y:hidden;background:var(--panel);-webkit-overflow-scrolling:touch}
table{width:100%;min-width:560px;border-collapse:collapse;font-size:12.8px}
thead th{
  text-align:left;font-size:11px;letter-spacing:.08em;text-transform:uppercase;
  color:var(--fg-3);font-weight:600;padding:10px 14px;background:rgba(148,163,184,.05);
  border-bottom:1px solid var(--line);position:sticky;top:0;
}
tbody td{padding:9px 14px;border-bottom:1px solid rgba(148,163,184,.07);vertical-align:top}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover{background:rgba(148,163,184,.035)}
td.key{font-family:var(--mono);font-size:12.2px;color:var(--fg);white-space:nowrap}
td.def{font-family:var(--mono);font-size:12.2px;color:var(--acc-2);white-space:nowrap}
td.desc{color:var(--fg-2)}
td.grp{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--fg-3);white-space:nowrap}
.empty{padding:26px;text-align:center;color:var(--fg-3);font-size:13px}

details.raw{margin-top:16px;border:1px solid var(--line);border-radius:var(--r);background:var(--panel);overflow:hidden}
details.raw summary{
  cursor:pointer;padding:12px 16px;font-size:13px;color:var(--fg-2);
  font-family:var(--mono);list-style:none;display:flex;align-items:center;gap:9px;
}
details.raw summary::-webkit-details-marker{display:none}
details.raw summary::before{content:"▸";color:var(--fg-3);transition:transform .18s}
details.raw[open] summary::before{transform:rotate(90deg)}
details.raw pre{
  max-height:440px;overflow:auto;padding:0 16px 16px;font-size:12.2px;
  line-height:1.75;color:#c9d6e5;border-top:1px solid var(--line);
}

/* ---------- releases ---------- */
.rel-list{display:grid;gap:0;border:1px solid var(--line);border-radius:var(--r-lg);overflow:hidden;background:var(--panel)}
.rel{
  display:grid;grid-template-columns:132px 1fr auto;gap:18px;align-items:center;
  padding:15px 20px;border-bottom:1px solid var(--line);
}
.rel:last-child{border-bottom:0}
.rel:hover{background:rgba(148,163,184,.03)}
.rel .ver{display:flex;align-items:center;gap:9px;font-family:var(--mono);font-size:13.5px;font-weight:600}
.rel .meta{font-size:12.4px;color:var(--fg-2)}
.rel .meta .t{color:var(--fg);font-weight:560}
.rel .date{font-family:var(--mono);font-size:11.5px;color:var(--fg-3);margin-top:3px}
.rel .dl{font-family:var(--mono);font-size:11.5px;color:var(--fg-3);border:1px solid var(--line-2);border-radius:6px;padding:5px 10px;transition:.15s}
.rel .dl:hover{color:var(--acc-2);border-color:rgba(16,185,129,.4)}

/* ---------- footer ---------- */
footer{border-top:1px solid var(--line);padding:34px 0 46px;margin-top:8px}
.foot{display:flex;flex-wrap:wrap;gap:18px;align-items:center;justify-content:space-between;font-size:12.6px;color:var(--fg-3)}
.foot a{color:var(--fg-2)}
.foot a:hover{color:var(--fg)}
.foot-links{display:flex;gap:16px;flex-wrap:wrap}

@media (max-width:900px){
  .topo,.builder,.chart-card{grid-template-columns:1fr}
  .ns+.ns{border-left:0;border-top:1px dashed var(--line-2)}
  .rel{grid-template-columns:1fr;gap:6px}
  nav.main{display:none}
}
@media (max-width:600px){
  .wrap{padding:0 16px}
  .hero{padding:40px 0 30px}
  section{padding:38px 0}
  .stat{flex-basis:50%}
  .row2{grid-template-columns:1fr}
}
"""

HEAD = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>binrc Helm Charts</title>
<meta name="description" content="binrc 官方 Helm Chart 仓库。HeadCNI：基于 Headscale 与官方 Tailscale 的 Kubernetes CNI，采用 netns 隔离架构。">
<meta name="generator" content="scripts/generate_portal.py">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='8' fill='%2310b981'/><text x='16' y='23' font-size='18' font-family='monospace' font-weight='bold' text-anchor='middle' fill='%23062017'>b</text></svg>">
<style>__CSS__</style>
</head>
<body>
"""

HEADER = """
<header class="top">
  <div class="wrap top-in">
    <a class="brand" href="#top">
      <span class="brand-mark">b</span>
      <span>binrc <small>/ Charts</small></span>
    </a>
    <nav class="main">
      <a href="#chart">Chart</a>
      <a href="#arch">架构</a>
      <a href="#install">安装</a>
      <a href="#config">配置</a>
      <a href="#releases">版本</a>
    </nav>
    <a class="top-cta" href="https://github.com/binrchq/Charts" target="_blank" rel="noopener">
      GitHub
    </a>
  </div>
</header>
"""

HERO = """
<main id="top">
<section class="hero">
  <div class="wrap">
    <span class="eyebrow"><span class="dot"></span>Helm Repository</span>
    <h1>binrc Helm Charts<br><span class="thin">生产环境的 Kubernetes 网络组件</span></h1>
    <p class="lede">
      本仓库是 binrc 的官方 Helm Chart 源，通过 <b>charts.binrc.com</b> 分发。
      当前提供 <b>HeadCNI</b> —— 基于 Headscale 与官方 Tailscale 的 CNI 插件，
      v1.1.0 起采用 <b style="white-space:nowrap">netns 隔离</b>架构，数据面与宿主机网络栈彻底分离。
    </p>

    <div class="stats">
      <div class="stat"><div class="v">__NCHARTS__</div><div class="k">Charts</div></div>
      <div class="stat"><div class="v">__NVERS__</div><div class="k">发布版本</div></div>
      <div class="stat"><div class="v">__LATEST__</div><div class="k">最新版本</div></div>
      <div class="stat"><div class="v">MIT</div><div class="k">License</div></div>
    </div>

    <div class="code" style="margin-top:24px">
      <div class="code-hd">
        <span class="t">快速开始</span>
        <button class="copy" onclick="copyCode(this,'c-quick')">复制</button>
      </div>
      <pre id="c-quick"><span class="cm"># 添加仓库</span>
helm repo add binrc https://charts.binrc.com
helm repo update

<span class="cm"># 安装 HeadCNI（需替换 Headscale 地址）</span>
helm install headcni binrc/headcni \\
  --namespace kube-system --create-namespace \\
  --set <span class="fl">config.headscale.url</span>=https://hs.example.com</pre>
    </div>
  </div>
</section>
"""

CHART_SEC = """
<section id="chart">
  <div class="wrap">
    <div class="sec-hd">
      <div class="sec-eyebrow">Chart</div>
      <h2>headcni</h2>
      <p class="sec-sub">Kubernetes CNI：用 WireGuard 组建跨节点 Pod 网络，路由由 Headscale 统一编排。</p>
    </div>

    <div class="chart-card">
      <div>
        <h3>
          headcni
          <span class="pill acc">v__LATEST__</span>
          <span class="pill">Networking</span>
        </h3>
        <p class="desc">
          daemon 以 hostNetwork 运行，负责 IPAM、路由与 Headscale 协调；
          tailscaled 子进程运行在独立 netns 中，通过 veth 与宿主网络栈相连。
          因此不需要修改宿主机的 fwmark、路由表号、ip rule 优先级或 iptables 链名。
        </p>
        <div class="facts">
          <div class="fact"><div class="k">Chart</div><div class="v">__LATEST__</div></div>
          <div class="fact"><div class="k">App</div><div class="v">__APPVER__</div></div>
          <div class="fact"><div class="k">Tailscale</div><div class="v">v1.104.4</div></div>
          <div class="fact"><div class="k">K8s</div><div class="v">1.20+</div></div>
          <div class="fact"><div class="k">License</div><div class="v">MIT</div></div>
        </div>
        <div class="links">
          <a href="https://github.com/binrchq/Charts/tree/main/charts/headcni" target="_blank" rel="noopener">Chart 源码</a>
          <a href="https://github.com/binrchq/headcni" target="_blank" rel="noopener">项目仓库</a>
          <a href="https://github.com/binrchq/headcni/issues" target="_blank" rel="noopener">Issues</a>
          <a href="__TGZ__">下载 __LATEST__ 包</a>
        </div>
      </div>
      <div class="code" style="margin-top:18px">
        <div class="code-hd">
          <span class="t">helm install</span>
          <button class="copy" onclick="copyCode(this,'c-inst')">复制</button>
        </div>
        <pre id="c-inst">helm install headcni binrc/headcni \\
  --namespace kube-system --create-namespace \\
  --version <span class="fl">__LATEST__</span> \\
  --set config.headscale.url=https://hs.example.com</pre>
      </div>
    </div>
  </div>
</section>
"""

ARCH_SEC = """
<section id="arch">
  <div class="wrap">
    <div class="sec-hd">
      <div class="sec-eyebrow">Architecture</div>
      <h2>netns 隔离拓扑</h2>
      <p class="sec-sub">
        两个独立的内核网络栈：宿主 netns 只增加一根 veth、一条 SNAT 和若干明确路由；
        tailscaled 的路由表、ip rule、fwmark 与 iptables 链全部留在隔离栈内。
      </p>
    </div>

    <div class="topo">
      <div class="ns">
        <div class="ns-hd"><span class="tag">host netns</span><span class="nm">宿主机网络栈</span></div>
        <div class="iface"><span class="n">tailscale0</span><span class="a">10.2.0.17/32 · 节点身份</span></div>
        <div class="iface"><span class="n">cni0</span><span class="a">10.42.5.1/24 · 本机 Pod 网关</span></div>
        <div class="iface hi"><span class="n">hcni0</span><span class="a">169.254.10.1/30 · 通往隔离区</span></div>
        <div class="ns-note">
          ip rule 52xx / table 52 / fwmark 0x80000 属于宿主 tailscaled，本方案不做任何改动。
        </div>
      </div>

      <div class="ns">
        <div class="ns-hd"><span class="tag">headcni netns</span><span class="nm">/var/run/netns/headcni</span></div>
        <div class="iface hi"><span class="n">hcni1</span><span class="a">169.254.10.2/30 · 默认路由出口</span></div>
        <div class="iface blue"><span class="n">headcni01</span><span class="a">tun · WireGuard 数据面</span></div>
        <div class="iface"><span class="n">tailscaled</span><span class="a">:41641 · 官方 v1.104.4</span></div>
        <div class="ns-note">
          自己的 table 52、52xx 规则、0x80000 与 ts-* 链。数字与宿主相同，但命名空间不同，因此不冲突。
        </div>
      </div>

      <div class="veth-note">
        <span>veth pair：</span>
        <span class="mono">hcni0 ↔ hcni1</span>
        <span>宿主侧仅一条 <span class="mono">MASQUERADE 169.254.10.0/30</span>，用于 tailscaled 自身出网</span>
      </div>
    </div>

    <div class="paths">
      <div class="path">
        <div class="lbl">Pod → Pod</div>
        <div class="flow">
          Pod <span class="arrow">→</span> cni0 <span class="arrow">→</span> 宿主任路由 <b>10.42.1.0/24 via 169.254.10.2 dev hcni0</b>
          <span class="arrow">→</span> hcni1 <span class="arrow">→</span> headcni01 <span class="arrow">→</span> WireGuard <span class="arrow">→</span> 对端<br>
          <span class="cm">全程保留 Pod 源 IP，不做 NAT</span>
        </div>
      </div>
      <div class="path">
        <div class="lbl">自身出网</div>
        <div class="flow">
          tailscaled <span class="arrow">→</span> default via 169.254.10.1 <span class="arrow">→</span> hcni1 <span class="arrow">→</span> hcni0
          <span class="arrow">→</span> 宿主 eth0 <span class="arrow">→</span> MASQUERADE<br>
          <span class="cm">169.254.10.2 是链路本地地址，必须 SNAT 才能收回包</span>
        </div>
      </div>
      <div class="path">
        <div class="lbl">宿主 tailnet</div>
        <div class="flow">
          tailscale0 <span class="arrow">→</span> table 52 <span class="arrow">→</span> 物理网卡<br>
          <span class="cm">完全不经过 hcni0，与 CNI 数据面互不干扰</span>
        </div>
      </div>
    </div>
  </div>
</section>
"""

INSTALL_SEC = """
<section id="install">
  <div class="wrap">
    <div class="sec-hd">
      <div class="sec-eyebrow">Install</div>
      <h2>命令生成器</h2>
      <p class="sec-sub">按实际参数生成 helm 命令与 values 覆盖片段，字段均对应 chart 中真实存在的键。</p>
    </div>

    <div class="builder">
      <div class="form">
        <div class="row2">
          <div class="field">
            <label>Release 名称</label>
            <input type="text" id="f-name" value="headcni">
          </div>
          <div class="field">
            <label>命名空间</label>
            <input type="text" id="f-ns" value="kube-system">
          </div>
        </div>
        <div class="field">
          <label>Headscale 地址 <span class="mono">config.headscale.url</span></label>
          <input type="text" id="f-hs" value="https://hs.example.com">
        </div>
        <div class="field">
          <label>Tailscale 控制地址 <span class="mono">config.tailscale.url</span></label>
          <input type="text" id="f-ts" value="https://hs.example.com">
        </div>
        <div class="row2">
          <div class="field">
            <label>版本</label>
            <select id="f-ver">__VER_OPTS__</select>
          </div>
          <div class="field">
            <label>MTU <span class="mono">config.network.mtu</span></label>
            <input type="number" id="f-mtu" value="1230" min="1200" max="1500">
          </div>
        </div>
        <div class="field">
          <label class="check"><input type="checkbox" id="f-netns" checked> netns 隔离（推荐）</label>
        </div>
        <div class="field">
          <label class="check"><input type="checkbox" id="f-metrics" checked> Prometheus 指标</label>
        </div>
      </div>

      <div class="out">
        <div class="code">
          <div class="code-hd">
            <span class="t">shell</span>
            <button class="copy" onclick="copyCode(this,'c-gen')">复制</button>
          </div>
          <pre id="c-gen"></pre>
        </div>
        <div class="code">
          <div class="code-hd">
            <span class="t">values-overlay.yaml</span>
            <button class="copy" onclick="copyCode(this,'c-val')">复制</button>
          </div>
          <pre id="c-val"></pre>
        </div>
      </div>
    </div>
  </div>
</section>
"""

CONFIG_SEC = """
<section id="config">
  <div class="wrap">
    <div class="sec-hd">
      <div class="sec-eyebrow">Values</div>
      <h2>配置参考</h2>
      <p class="sec-sub">下表为 __LATEST__ 版本 values.yaml 中的实际配置项与默认值。</p>
    </div>

    <div class="toolbar">
      <label class="search">
        <span>/</span>
        <input type="text" id="f-q" placeholder="搜索配置项，例如 netns 或 mtu" autocomplete="off">
      </label>
      <span class="pill" id="q-count"></span>
    </div>

    <div class="tbl-wrap">
      <table>
        <thead>
          <tr><th>分组</th><th>键</th><th>默认值</th><th>说明</th></tr>
        </thead>
        <tbody id="tbody"></tbody>
      </table>
    </div>

    <details class="raw">
      <summary>完整 values.yaml（__LATEST__）</summary>
      <pre><code id="raw-values"></code></pre>
    </details>
  </div>
</section>
"""

REL_SEC = """
<section id="releases">
  <div class="wrap">
    <div class="sec-hd">
      <div class="sec-eyebrow">Releases</div>
      <h2>版本记录</h2>
      <p class="sec-sub">来自 index.yaml 的真实发布记录，说明取自本仓库对应提交。</p>
    </div>
    <div class="rel-list">__REL_ROWS__</div>
  </div>
</section>
</main>
"""

FOOTER = """
<footer>
  <div class="wrap foot">
    <div class="foot-links">
      <a href="https://charts.binrc.com/index.yaml">index.yaml</a>
      <a href="https://github.com/binrchq/Charts">GitHub</a>
      <a href="https://github.com/binrchq/headcni">headcni</a>
      <a href="https://helm.sh/docs/">Helm 文档</a>
    </div>
    <div>binrc · charts.binrc.com · MIT</div>
  </div>
</footer>
"""

JS = r"""
<script>
const RELEASES = __RELEASES__;
const VALUES_YAML = __VALUES__;
const VALUE_ROWS = __ROWS__;

function copyCode(btn, id){
  const el = document.getElementById(id);
  if(!el) return;
  const text = el.innerText;
  const done = () => { const t = btn.textContent; btn.textContent = '已复制'; setTimeout(()=>btn.textContent=t, 1400); };
  if(navigator.clipboard && navigator.clipboard.writeText){
    navigator.clipboard.writeText(text).then(done).catch(()=>fallback(text, done));
  } else { fallback(text, done); }
  function fallback(txt, cb){
    const ta = document.createElement('textarea');
    ta.value = txt; ta.style.position='fixed'; ta.style.opacity='0';
    document.body.appendChild(ta); ta.select();
    try{ document.execCommand('copy'); cb(); }catch(e){}
    document.body.removeChild(ta);
  }
}

/* ---------- 配置表 ---------- */
const tbody = document.getElementById('tbody');
const qInput = document.getElementById('f-q');
const qCount = document.getElementById('q-count');

function renderRows(list){
  let prev = null;
  tbody.innerHTML = list.length ? list.map(r => {
    const grp = (r[0] === prev) ? '' : r[0];
    prev = r[0];
    return '<tr><td class="grp">' + grp + '</td>' +
    '<td class="key">' + r[1] + '</td>' +
    '<td class="def">' + r[2] + '</td>' +
    '<td class="desc">' + r[3] + '</td></tr>';
  }).join('') : '<tr><td colspan="4" class="empty">没有匹配的配置项</td></tr>';
  qCount.textContent = list.length + ' / ' + VALUE_ROWS.length;
}
renderRows(VALUE_ROWS);
qInput.addEventListener('input', () => {
  const q = qInput.value.trim().toLowerCase();
  renderRows(!q ? VALUE_ROWS : VALUE_ROWS.filter(r => (r[0]+' '+r[1]+' '+r[2]+' '+r[3]).toLowerCase().includes(q)));
});

/* ---------- 完整 values.yaml ---------- */
document.getElementById('raw-values').textContent = VALUES_YAML;

/* ---------- 命令生成器 ---------- */
const fName = document.getElementById('f-name');
const fNs = document.getElementById('f-ns');
const fHs = document.getElementById('f-hs');
const fTs = document.getElementById('f-ts');
const fVer = document.getElementById('f-ver');
const fMtu = document.getElementById('f-mtu');
const fNetns = document.getElementById('f-netns');
const fMetrics = document.getElementById('f-metrics');

function esc(s){ return s.replace(/\\/g,'\\\\').replace(/"/g,'\\"'); }

function build(){
  const name = (fName.value.trim() || 'headcni');
  const ns = (fNs.value.trim() || 'kube-system');
  const hs = fHs.value.trim();
  const ts = fTs.value.trim();
  const ver = fVer.value;
  const mtu = fMtu.value.trim();
  const netns = fNetns.checked;
  const metrics = fMetrics.checked;

  const lines = [
    'helm repo add binrc https://charts.binrc.com',
    'helm repo update',
    '',
    'helm upgrade --install ' + name + ' binrc/headcni \\\\',
    '  --namespace ' + ns + ' --create-namespace \\\\',
    '  --version ' + ver + ' \\\\'
  ];
  const sets = [];
  if(hs) sets.push('config.headscale.url=' + esc(hs));
  if(ts) sets.push('config.tailscale.url=' + esc(ts));
  if(mtu) sets.push('config.network.mtu=' + mtu);
  sets.push('config.netns.enabled=' + (netns ? 'true' : 'false'));
  sets.push('config.monitoring.enabled=' + (metrics ? 'true' : 'false'));
  sets.forEach((s,i) => {
    lines.push('  --set ' + s + (i === sets.length - 1 ? '' : ' \\\\'));
  });

  document.getElementById('c-gen').textContent = lines.join('\n');

  const y = ['# values-overlay.yaml', 'config:'];
  if(hs) y.push('  headscale:', '    url: "' + hs + '"');
  if(ts) y.push('  tailscale:', '    url: "' + ts + '"');
  y.push('  network:', '    mtu: ' + (mtu || 1230));
  y.push('  netns:', '    enabled: ' + (netns ? 'true' : 'false'));
  y.push('  monitoring:', '    enabled: ' + (metrics ? 'true' : 'false'));
  document.getElementById('c-val').textContent = y.join('\n');
}
[fName,fNs,fHs,fTs,fVer,fMtu,fNetns,fMetrics].forEach(el => {
  el.addEventListener('input', build);
  el.addEventListener('change', build);
});
build();
</script>
</body>
</html>
"""

# ---------------------------------------------------------------- 组装
rel_rows = []
for r in releases:
    badge = '<span class="pill acc">latest</span>' if r["latest"] else ''
    rel_rows.append(
        '<div class="rel">'
        f'<div class="ver">{r["version"]}{badge}</div>'
        f'<div class="meta"><span class="t">{r["title"]}</span> — {r["note"]}'
        f'<div class="date">{r["created"]} · appVersion {r["appVersion"]} · sha256 {r["digest"]}…</div></div>'
        f'<a class="dl" href="{r["url"]}">tgz</a>'
        '</div>'
    )

ver_opts = "".join(
    f'<option value="{r["version"]}"{" selected" if r["latest"] else ""}>{r["version"]}</option>'
    for r in releases
)

html = (
    HEAD.replace("__CSS__", CSS)
    + HEADER
    + HERO
    + CHART_SEC
    + ARCH_SEC
    + INSTALL_SEC
    + CONFIG_SEC
    + REL_SEC
    + FOOTER
    + JS
)
html = (html
        .replace("__NCHARTS__", str(stats["charts"]))
        .replace("__NVERS__", str(stats["versions"]))
        .replace("__LATEST__", stats["latest"])
        .replace("__APPVER__", releases[0]["appVersion"] if releases else "")
        .replace("__TGZ__", f"https://charts.binrc.com/{CHART}-{stats['latest']}.tgz")
        .replace("__VER_OPTS__", ver_opts)
        .replace("__REL_ROWS__", "".join(rel_rows))
        .replace("__RELEASES__", json.dumps(releases, ensure_ascii=False))
        .replace("__VALUES__", json.dumps(values_yaml, ensure_ascii=False))
        .replace("__ROWS__", json.dumps(VALUE_ROWS, ensure_ascii=False))
        .replace("\n\n\n", "\n\n")
)

with open(OUT, "w") as f:
    f.write(html)

print(f"wrote {OUT} ({len(html)} bytes, {len(html.splitlines())} lines)")
print(f"charts={stats['charts']} versions={stats['versions']} latest={stats['latest']}")
