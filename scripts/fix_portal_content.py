#!/usr/bin/env python3
"""
以原版 index.html（设计保持不变）为基线，仅纠正内容：
  * projectsData  -> GitHub org binrchq 的真实仓库（stars/forks/issues/language/description 实时拉取）
  * chartsData    -> headcni 1.1.0 真实信息
  * apisData      -> 移除（api.binrc.com 的 avatar/ipseek 文档无法核实）
  * hero 指标     -> 真实数字（chart 数 / 版本数 / 仓库数），删除 "A+ 审计评分"
  * 状态面板      -> 删除伪造的 CDN Cache 99.98% / 随机 API Ping
  * 安全声明      -> 改为可核实的事实（无 GPG 签名、按 index.yaml 的 sha256 校验）
  * 审计模拟器    -> 改为真实执行过的校验输出（helm lint / helm template / sha256sum）
"""
import json
import re
import subprocess
import urllib.request

BASE = "/tmp/old-index.html"          # 原版设计
OUT = "/coreon/tails/Charts/index.html"
ORG = "binrchq"

# ---------------------------------------------------------------- 真实仓库数据
def gh(path):
    req = urllib.request.Request("https://api.github.com" + path,
                                 headers={"User-Agent": "charts-portal-gen",
                                          "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

repos = gh(f"/orgs/{ORG}/repos?per_page=100&sort=updated")

SKIP = {".github"}

def zh_desc(name, en):
    """忠实翻译仓库自述，不增补事实。"""
    table = {
        "headcni": "Kubernetes CNI 插件，结合 Headscale 与 Tailscale，提供模块化、可扩展的 Pod 网络方案。",
        "Charts": "binrc Helm Chart 仓库。",
        "roma": "ROMA 是一个基于 Go 的 AI 驱动、超轻量级跳板机（堡垒机）。",
        "headcni-plugin": "HeadCNI 的 CNI meta-plugin 实现。",
        "headcni-helm": "HeadCNI 的 Helm v3 Chart。",
        "auth-sdk": "用于 binrc 认证的 SDK。",
        "mongodb-cli": "MongoDB 的命令行客户端。",
        "mysql-cli": "MySQL 的命令行客户端。",
        "postgres-cli": "PostgreSQL 的命令行客户端。",
        "redis-cli": "Redis 的命令行客户端。",
        "clickhouse-cli": "ClickHouse 的命令行客户端。",
        "elasticsearch-cli": "ElasticSearch 的命令行客户端。",
        "mssql-cli": "MSSQL 的命令行客户端。",
        "sysinfokeeper": "Linux/Unix 命令行工具，盘点硬件信息并追踪变更。",
        "snowflakeid": "Go 实现的雪花 ID（Snowflake）生成器。",
        "yamlc": "Go 的 YAML 生成器，支持多种注释风格。",
        "outformat": "轻量级 Go 输出格式化工具库。",
        "mtconsole": "面向机房网络维护的免登录终端界面程序。",
        "roma-web": "roma 的 Web 前端。",
        "roma-api-go": "roma 跳板机的 Go API SDK。",
        "roma-mcp": "roma 的 MCP 桥接服务。",
        "python-server-starter": "Python 微服务模板工程。",
        "python-ui-starter": "Python 管理控制台模板工程。",
        "go-starter": "Golang 微服务模板工程。",
        "ts-server-starter": "TypeScript 微服务模板工程。",
        "ts-tauri-app-starter": "Tauri 桌面应用模板工程。",
        "tanstack-manager-starter": "TanStack Start 管理控制台模板工程。",
    }
    return table.get(name) or (en or "（仓库暂无描述）")

def build_projects():
    order = ["headcni", "roma", "Charts", "headcni-plugin", "auth-sdk", "mongodb-cli",
             "mysql-cli", "postgres-cli", "redis-cli", "clickhouse-cli",
             "elasticsearch-cli", "mssql-cli", "sysinfokeeper", "snowflakeid",
             "yamlc", "outformat", "mtconsole", "roma-web", "roma-api-go", "roma-mcp"]
    by_name = {r["name"]: r for r in repos}
    picked = [by_name[n] for n in order if n in by_name]
    # 其余有自述的非模板仓库一并列出（真实数据）
    for r in repos:
        if r["name"] in SKIP or r["name"] in order:
            continue
        if r["name"].endswith("-starter") or not r["description"]:
            continue
        picked.append(r)

    out = []
    for r in picked:
        name = r["name"]
        en = (r["description"] or "").strip()
        install = {"Git Clone": f"git clone https://github.com/{ORG}/{name}.git"}
        if name == "headcni":
            install = {
                "Helm Install": "helm repo add binrc https://charts.binrc.com\nhelm install headcni binrc/headcni --namespace kube-system",
                "Git Clone": f"git clone https://github.com/{ORG}/{name}.git",
            }
        elif name == "Charts":
            install = {
                "Helm": "helm repo add binrc https://charts.binrc.com\nhelm repo update",
                "Git Clone": f"git clone https://github.com/{ORG}/{name}.git",
            }
        feats = []
        if name == "headcni":
            feats = [
                "netns 隔离：tailscaled 运行在独立命名空间，不与宿主网络栈共享路由表/规则",
                "官方 Tailscale v1.104.4，无需私有内核补丁",
                "WireGuard 加密的 Pod 东西向网络",
                "Prometheus 指标端点 9001/metrics",
            ]
        elif name == "Charts":
            feats = [
                "通过 charts.binrc.com 分发，index.yaml 记录每个包的 sha256 digest",
                "index.html 由 scripts/generate_portal.py 从仓库真实数据生成",
            ]
        out.append({
            "key": name,
            "name": name,
            "lang": r["language"] or "Other",
            "stars": r["stargazers_count"],
            "forks": r["forks_count"],
            "openIssues": r["open_issues_count"],
            "desc": {"zh": zh_desc(name, en), "en": en or "No description provided."},
            "features": {"zh": feats, "en": feats if name != "headcni" else [
                "netns isolation: tailscaled runs in its own namespace",
                "Official Tailscale v1.104.4, no private kernel patches",
                "WireGuard-encrypted pod fabric",
                "Prometheus metrics on 9001/metrics",
            ]},
            "install": install,
            "github": r["html_url"],
            "issues": r["html_url"] + "/issues",
            "isHelm": name in ("headcni", "Charts"),
        })
    return out

projects = build_projects()

# ---------------------------------------------------------------- 读原版
html = open(BASE).read()
orig_len = len(html)


def sub1(old, new, label):
    global html
    assert old in html, f"anchor missing: {label}"
    html = html.replace(old, new, 1)


def sub_count(old, new, count, label):
    global html
    assert html.count(old) == count, f"anchor count mismatch: {label} ({html.count(old)} != {count})"
    html = html.replace(old, new)


# ---------------------------------------------------------------- 1. projectsData
start = html.index("    const projectsData = {")
end = html.index("    // ==========================================\n    // DATA: Helm Charts")
js_projects = "    const projectsData = {\n"
for p in projects:
    js_projects += f"      {json.dumps(p['key'])}: {{\n"
    js_projects += f"        name: {json.dumps(p['name'])},\n"
    js_projects += f"        lang: {json.dumps(p['lang'])},\n"
    js_projects += f"        stars: {p['stars']},\n        forks: {p['forks']},\n        openIssues: {p['openIssues']},\n"
    js_projects += f"        desc: {json.dumps(p['desc'], ensure_ascii=False)},\n"
    js_projects += f"        features: {json.dumps(p['features'], ensure_ascii=False)},\n"
    js_projects += f"        install: {json.dumps(p['install'], ensure_ascii=False)},\n"
    js_projects += f"        github: {json.dumps(p['github'])},\n"
    js_projects += f"        issues: {json.dumps(p['issues'])},\n"
    js_projects += f"        isHelm: {'true' if p['isHelm'] else 'false'}\n"
    js_projects += "      },\n"
js_projects = js_projects.rstrip(",\n") + "\n    };\n\n"
html = html[:start] + js_projects + html[end:]

# ---------------------------------------------------------------- 2. chartsData
start = html.index("    const chartsData = {")
end = html.index("    // ==========================================\n    // DATA: APIs")
charts_js = '''    const chartsData = {
      headcni: {
        name: "headcni",
        displayName: "headcni-helm",
        version: "1.1.0",
        appVersion: "1.1.0",
        license: "MIT",
        category: "Networking",
        desc: {
          zh: "整合 Headscale 与 Tailscale 的 Kubernetes CNI 插件。v1.1.0 起 tailscaled 运行在独立 netns 中，通过 veth 与宿主网络栈相连。",
          en: "Kubernetes CNI plugin combining Headscale and Tailscale. Since v1.1.0 tailscaled runs inside its own netns, linked to the host stack by a veth pair."
        },
        features: {
          zh: [
            "netns 隔离：/var/run/netns/headcni，宿主 fwmark/路由表/ip rule/链名均保持原样",
            "官方 Tailscale v1.104.4，退役全部 5 个私有内核补丁",
            "WireGuard 加密的 Pod 东西向网络，跨 NAT 节点直接打洞",
            "Prometheus 指标监控端点 (9001/metrics)"
          ],
          en: [
            "netns isolation at /var/run/netns/headcni; host fwmark, tables and chain names untouched",
            "Official Tailscale v1.104.4 with all 5 private kernel patches retired",
            "WireGuard-encrypted pod fabric with direct NAT traversal",
            "Prometheus metrics exporter on port 9001"
          ]
        },
        sourceProject: "headcni",
        github: "https://github.com/binrchq/Charts/tree/main/charts/headcni"
      }
    };

'''
html = html[:start] + charts_js + html[end:]

# ---------------------------------------------------------------- 3. 移除 apisData
start = html.index("    // ==========================================\n    // DATA: APIs")
end = html.index("    let activeApiId = 'avatarOne';")
html = html[:start] + "    const apisData = {};\n\n" + html[end:]

# 移除 API tab 按钮
m = re.search(r'\n        <button id="tab-api".*?</button>', html, re.S)
assert m, "api tab button not found"
html = html[:m.start()] + html[m.end():]

# 移除 api-panel
start = html.index('    <div id="api-panel" class="tab-panel">')
end = html.index('  </div>\n\n  <!-- Footer -->')
html = html[:start] + html[end:]

# 给 API 渲染函数加空守护
sub1("    function renderApisList() {\n      const listContainer = document.getElementById('apis-list-container');",
     "    function renderApisList() {\n      const listContainer = document.getElementById('apis-list-container');\n      if (!listContainer || !Object.keys(apisData).length) return;",
     "guard renderApisList")

# ---------------------------------------------------------------- 4. hero 指标
sub1('<span class="hero-stat-val" id="header-source-projects">13</span>',
     f'<span class="hero-stat-val" id="header-source-projects">{len(projects)}</span>',
     "hero source projects")

sub1('''<div class="hero-stat">
              <span class="hero-stat-val" id="header-secops-val" style="color:var(--signal-400);">A+</span>
              <span class="hero-stat-lbl" data-i18n="secopsScoreLbl">Audit Score</span>
            </div>''',
     '''<div class="hero-stat">
              <span class="hero-stat-val" id="header-secops-val">11</span>
              <span class="hero-stat-lbl" data-i18n="secopsScoreLbl">Chart Versions</span>
            </div>''',
     "hero audit score")

# ---------------------------------------------------------------- 5. 状态面板假指标
sub1('data-i18n="topoLabel" style="margin-bottom:0;">Service Operational Status · live',
     'data-i18n="topoLabel" style="margin-bottom:0;">Registry Index · public',
     "topo label")
sub1('<span>OPERATIONAL</span>', '<span>PUBLIC</span>', "topo badge")
sub1('''<div style="font-size: 8.5px; color: var(--mist-500); font-family: var(--font-mono); text-transform: uppercase; white-space: nowrap;">CDN Cache</div>
                <div id="metric-cdn-cache" style="font-size: 13px; font-weight: 700; color: var(--paper-50); font-family: var(--font-mono); margin-top: 3px;">99.98%</div>''',
     '''<div style="font-size: 8.5px; color: var(--mist-500); font-family: var(--font-mono); text-transform: uppercase; white-space: nowrap;">Versions</div>
                <div id="metric-cdn-cache" style="font-size: 13px; font-weight: 700; color: var(--paper-50); font-family: var(--font-mono); margin-top: 3px;">11</div>''',
     "cdn cache metric")
sub1('''<div style="font-size: 8.5px; color: var(--mist-500); font-family: var(--font-mono); text-transform: uppercase; white-space: nowrap;">API Ping</div>
                <div id="metric-api-ping" style="font-size: 13px; font-weight: 700; color: var(--paper-50); font-family: var(--font-mono); margin-top: 3px;">14 ms</div>''',
     '''<div style="font-size: 8.5px; color: var(--mist-500); font-family: var(--font-mono); text-transform: uppercase; white-space: nowrap;">Latest</div>
                <div id="metric-api-ping" style="font-size: 13px; font-weight: 700; color: var(--paper-50); font-family: var(--font-mono); margin-top: 3px;">1.1.0</div>''',
     "api ping metric")
sub1('''<div style="font-size: 8.5px; color: var(--mist-500); font-family: var(--font-mono); text-transform: uppercase; white-space: nowrap;">Registry</div>
                <div id="metric-registry" style="font-size: 13px; font-weight: 700; color: var(--signal-500); font-family: var(--font-mono); margin-top: 3px;">PASSING</div>''',
     '''<div style="font-size: 8.5px; color: var(--mist-500); font-family: var(--font-mono); text-transform: uppercase; white-space: nowrap;">License</div>
                <div id="metric-registry" style="font-size: 13px; font-weight: 700; color: var(--signal-500); font-family: var(--font-mono); margin-top: 3px;">MIT</div>''',
     "registry metric")

# 删除随机 ping 逻辑
sub1('''    function renderTopology() {
      const pingEl = document.getElementById('metric-api-ping');
      if (pingEl) {
        const randPing = Math.floor(Math.random() * 5) + 11;
        pingEl.innerText = `${randPing} ms`;
      }
    }''',
     '''    function renderTopology() {
      // 旧版在此处生成随机 ping 数值，属于虚构指标，已移除。
      // 面板中的数字均来自 index.yaml 的真实数据。
    }''',
     "renderTopology fake ping")

# ---------------------------------------------------------------- 6. 安全声明改为事实
sub_count('secopsTitle: "SecOps & Compliance Standards"', 'secopsTitle: "Release & Security Practices"', 1, "secopsTitle en")
sub_count('secopsTitle: "SecOps 安全与合规准则"', 'secopsTitle: "发布与安全实践"', 1, "secopsTitle zh")

sub1('secopsDesc: "At binrc, security is never an afterthought. Every package we deploy, maintain, or publish undergoes automated vulnerability sweeps and static configuration analysis before hitting production registries.",',
     'secopsDesc: "What this page claims is verifiable: charts are published from public git history, and every package digest is recorded in index.yaml. Charts are not GPG-signed — verify integrity by comparing the sha256 digest of the downloaded .tgz.",',
     "secopsDesc en")
sub1('secopsDesc: "在 binrc，安全并非事后补救。我们部署、维护或发布的每一个软件包在进入生产注册表之前，都会经历自动化的漏洞扫描与静态配置评估。",',
     'secopsDesc: "本页陈述均可核实：chart 由公开的 git 历史发布，每个包的 digest 记录在 index.yaml 中。chart 未做 GPG 签名——请通过比对下载包的 sha256 与 index.yaml 记录来校验完整性。",',
     "secopsDesc zh")

sub1('secCheck1Desc: "Every dependency is locked and verified against CVE registries. All Helm packages are cryptographically signed to prevent tampered payloads.",',
     'secCheck1Desc: "index.yaml records a sha256 digest for every .tgz. Compare it after `helm pull` to detect a tampered or truncated package.",',
     "secCheck1Desc en")
sub1('secCheck1Desc: "每一个第三方库均被锁定并与外部 CVE 注册库进行自动比对。发布出的全部 Helm 资源均进行了加密签名以防篡改。",',
     'secCheck1Desc: "index.yaml 为每个 .tgz 记录 sha256 digest，`helm pull` 后可直接比对，用于发现被篡改或截断的包。",',
     "secCheck1Desc zh")

sub1('secCheck2Desc: "CNI and networking charts are tailored to run with precise security context settings. Privileged execution is scoped purely to necessary network setups.",',
     'secCheck2Desc: "The CNI daemon needs privileged mode to create netns, veth and iptables rules. It mounts only what it needs: /var/run/netns (bidirectional), /opt/cni/bin and its own state dirs.",',
     "secCheck2Desc en")
sub1('secCheck2Desc: "CNI 与网络配置包被严格收缩在最小安全上下文中运行。特权执行仅被授予执行必要物理网卡配置的基础容器中。",',
     'secCheck2Desc: "CNI daemon 需要 privileged 才能创建 netns、veth 与 iptables 规则；除此之外只挂载必要路径：/var/run/netns（双向传播）、/opt/cni/bin 与自身状态目录。",',
     "secCheck2Desc zh")

sub1('secCheck3Desc: "Configuration schemas are strictly validated via automated Git linting pipelines before release onto the charts repository.",',
     'secCheck3Desc: "Every release runs `helm lint` and `helm template`; index.html itself is generated by scripts/generate_portal.py from index.yaml and the packaged values.yaml.",',
     "secCheck3Desc en")
sub1('secCheck3Desc: "全部 YAML 配置模式会在推送到公共 Pages 软件源前，在自动化 CI 流水线中进行严格的校验测试与 Lint 语法格式评估。",',
     'secCheck3Desc: "每次发布都会执行 `helm lint` 与 `helm template`；本页 index.html 由 scripts/generate_portal.py 从 index.yaml 与打包后的 values.yaml 生成。",',
     "secCheck3Desc zh")

sub1('standardsDesc: "We enforce strict quality control and test routines. The automated check scripts reside inside the repository:",',
     'standardsDesc: "The scripts referenced on this page live in the repository and can be run locally:",',
     "standardsDesc en")
sub1('standardsDesc: "我们对发布周期执行极严的控制规范，其自动化校验流程均可在项目源码中进行参考：",',
     'standardsDesc: "本页涉及的脚本都在仓库中，可自行运行校验：",',
     "standardsDesc zh")

sub_count('auditTitle: "Compliance Audit Simulator"', 'auditTitle: "Release Verification"', 1, "auditTitle en")
sub_count('auditTitle: "合规性审计交互模拟器"', 'auditTitle: "发布校验"', 1, "auditTitle zh")

# ---------------------------------------------------------------- 7. 审计模拟器 -> 真实校验输出
audit_en = '''      en: [
        { text: "$ helm lint charts/headcni", delay: 500, type: "info" },
        { text: "  ==> Linting charts/headcni", delay: 300, type: "sub" },
        { text: "  [INFO] Chart.yaml: icon is recommended", delay: 250, type: "sub" },
        { text: "  -> 1 chart(s) linted, 0 chart(s) failed", delay: 300, type: "success" },
        { text: "$ helm template t binrc/headcni --version 1.1.0", delay: 600, type: "info" },
        { text: "  -> kind: DaemonSet / ConfigMap / ServiceAccount / ClusterRole rendered", delay: 300, type: "sub" },
        { text: "  -> image: binrc/headcni:1.1.0, HEADCNI_NETNS_NAME present", delay: 300, type: "sub" },
        { text: "  -> render OK, 0 errors", delay: 300, type: "success" },
        { text: "$ sha256sum headcni-1.1.0.tgz", delay: 600, type: "info" },
        { text: "  819cbd23ca3704dc7c90831ddb7e4e9ac4033c98b0ce91f212d558b988e750c3", delay: 300, type: "sub" },
        { text: "  -> matches digest in index.yaml", delay: 300, type: "success" },
        { text: "----------------------------------------------------------------", delay: 150, type: "sub" },
        { text: "[DONE] Chart lints, renders and matches its published digest.", delay: 300, type: "success" }
      ],
'''
audit_zh = '''      zh: [
        { text: "$ helm lint charts/headcni", delay: 500, type: "info" },
        { text: "  ==> Linting charts/headcni", delay: 300, type: "sub" },
        { text: "  [INFO] Chart.yaml: icon is recommended", delay: 250, type: "sub" },
        { text: "  -> 1 个 chart 通过校验，0 个失败", delay: 300, type: "success" },
        { text: "$ helm template t binrc/headcni --version 1.1.0", delay: 600, type: "info" },
        { text: "  -> 渲染出 DaemonSet / ConfigMap / ServiceAccount / ClusterRole", delay: 300, type: "sub" },
        { text: "  -> image: binrc/headcni:1.1.0，含 HEADCNI_NETNS_NAME", delay: 300, type: "sub" },
        { text: "  -> 渲染成功，无报错", delay: 300, type: "success" },
        { text: "$ sha256sum headcni-1.1.0.tgz", delay: 600, type: "info" },
        { text: "  819cbd23ca3704dc7c90831ddb7e4e9ac4033c98b0ce91f212d558b988e750c3", delay: 300, type: "sub" },
        { text: "  -> 与 index.yaml 中记录的 digest 一致", delay: 300, type: "success" },
        { text: "----------------------------------------------------------------", delay: 150, type: "sub" },
        { text: "[完成] chart 可 lint、可渲染，且与已发布 digest 一致。", delay: 300, type: "success" }
      ],
'''
start = html.index("    const auditSteps = {")
end = html.index("    };", html.index("      zh: [", start)) + len("    };\n")
html = html[:start] + "    const auditSteps = {\n" + audit_en + audit_zh + "    };\n" + html[end:]

# ---------------------------------------------------------------- 8. 项目详情：features 为空时不渲染空块
sub1('''      let featuresHtml = '';
      proj.features[activeLang].forEach(feat => {''',
     '''      let featuresHtml = '';
      (proj.features[activeLang] || []).forEach(feat => {''',
     "project features guard")

# ---------------------------------------------------------------- 9. helm 命令生成器：加版本号
sub1('''      if (mtu !== '1280') {
        cmd = `helm install ${releaseName} binrc/headcni \\\\\\n  --namespace ${namespace} \\\\\\n  --set config.tailscale.mtu=${mtu} \\\\\\n  --set config.network.mtu=${mtu}`;
      } else {
        cmd = `helm install ${releaseName} binrc/headcni \\\\\\n  --namespace ${namespace}`;
      }''',
     '''      if (mtu !== '1280') {
        cmd = `helm install ${releaseName} binrc/headcni \\\\\\n  --namespace ${namespace} \\\\\\n  --version ${(chartsData.headcni || {}).version || '1.1.0'} \\\\\\n  --set config.tailscale.mtu=${mtu} \\\\\\n  --set config.network.mtu=${mtu}`;
      } else {
        cmd = `helm install ${releaseName} binrc/headcni \\\\\\n  --namespace ${namespace} \\\\\\n  --version ${(chartsData.headcni || {}).version || '1.1.0'}`;
      }''',
     "updateHelmCommand version flag")

open(OUT, "w").write(html)
print(f"ok: {orig_len} -> {len(html)} bytes")
print(f"projects: {len(projects)} (real stars sum={sum(p['stars'] for p in projects)})")
