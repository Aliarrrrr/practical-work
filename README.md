# Practical Work

**务实科研、工程与交付：适用于支持 Agent Skills 的助手。**

Practical Work 提供科研、软件工程与交付协作三个入口，帮助 agent 围绕具体问题选择工作、验证实际结果，并准确说明结论范围。减少空泛保证和无用途流程，同时保留项目必要检查、用户授权与数据恢复条件。

规则按当前任务读取。文件制作、应用操作和专业计算采用当前环境已有的技能与工具，不绑定 Codex 的工具名称。

[快速开始](#快速开始) · [兼容性](#兼容性) · [技能目录](#技能目录) · [使用示例](#使用示例) · [加载方式](#加载方式) · [维护](#维护)

## 快速开始

选择一种安装方式。原生插件和独立技能提供相同规则，不要在同一客户端重复安装两份。

### Codex

```sh
codex plugin marketplace add Aliarrrrr/practical-work --ref main --json
codex plugin add practical-work@practical-work --json
codex plugin list --marketplace practical-work --json
```

需要支持 `codex plugin` 的 CLI 和 Git。确认已安装且启用，再开始新会话查看三个 `practical-work:*` 入口。已有 `practical-work@zlf-local` 的安装可继续使用原来源。

### Claude Code

```sh
claude plugin marketplace add Aliarrrrr/practical-work
claude plugin install practical-work@practical-work-marketplace
```

新会话可使用 `/practical-work:research`、`/practical-work:engineering`、`/practical-work:delivery`。

### Gemini CLI

```sh
gemini extensions install https://github.com/Aliarrrrr/practical-work
```

重新启动会话，通过 `/skills list` 确认 `research`、`engineering`、`delivery`。这些是技能，不是扩展注册的三个同名命令；也可按下文安装带前缀的独立技能，避免与已有名称冲突。

### GitHub Copilot CLI

```sh
copilot plugin install Aliarrrrr/practical-work
```

VS Code 使用命令面板 **Chat: Install Plugin From Source**，输入仓库 URL；需启用 `chat.plugins.enabled`。云端 agent 使用项目内技能目录，不能依赖本机用户目录。

### Cursor

在 **Customize → From GitHub Repository** 中添加 `https://github.com/Aliarrrrr/practical-work`，选择插件安装。仓库已包含 Cursor 所需的市场清单。

### 独立技能：OpenCode、Windsurf、Antigravity 及其他兼容客户端

用 Python 3.10 或以上版本导出三个完整技能目录，无第三方 Python 依赖：

```sh
git clone https://github.com/Aliarrrrr/practical-work.git
cd practical-work
python scripts/portable_skills.py export --output /path/to/project/.agents/skills
```

把示例路径替换为目标项目的技能目录；Windows 也可使用 `C:/path/to/project/.agents/skills`。Claude Code 项目改用 `.claude/skills`，旧版 Windsurf 可用 `.windsurf/skills`。各客户端的用户目录与项目目录见 [兼容说明](docs/compatibility.md)。

导出的名称为 `practical-work-research`、`practical-work-engineering`、`practical-work-delivery`。每个目录包含所需参考文件，可以单独移动或安装；不要只复制 `SKILL.md`。脚本拒绝覆盖非本工具创建的同名目录，重复导出会更新受管文件并保留额外文件。它不修改全局指令、客户端设置或连接账号。

## 兼容性

| 客户端 | 提供的安装形式 | 本项目检查范围 |
| --- | --- | --- |
| Codex | 原生插件、独立技能 | Windows CLI `0.162.0-alpha.17.2` 安装与新会话加载 |
| Claude Code | 原生插件、独立技能 | Windows `2.1.245` 清单验证与本地插件加载 |
| Cursor | Agent Plugins 插件、独立技能 | 官方清单与技能目录核对 |
| Gemini CLI | 扩展、独立技能 | 官方扩展与技能目录核对 |
| GitHub Copilot CLI / VS Code | Agent Plugins 插件、独立技能 | 官方格式与安装入口核对 |
| Copilot cloud agent | 项目内独立技能 | 官方目录核对；未运行云端任务 |
| OpenCode | 独立技能 | 官方目录核对 |
| Windsurf / 当前 Devin Desktop | 独立技能 | 当前官方目录核对；不涵盖任意旧版 |
| Antigravity IDE / CLI | 独立技能 | 官方目录核对；IDE 与 CLI 用户目录分别说明 |

各客户端的具体版本、技能开关、权限与模型会影响发现和自动选择。目录与文件检查不能证明未运行客户端的实际行为。核对日期和官方来源见 [兼容说明](docs/compatibility.md)。

本机 Codex 已安装并启用 Practical Work `0.2.0`，新会话读取了工程入口和改动参考；Claude Code 通过本地 `--plugin-dir` 发现三个入口并读取了共同约束与排错参考。Claude 当前配置的 DeepSeek-V4-flash 在示例分析中仍出现多余文件查找，已补充相应排错指导；这些加载结果不作为全部任务判断均正确的证明。

## 技能目录

| 场景 | 原生插件技能 | 独立技能 | 按需读取的内容 |
| --- | --- | --- | --- |
| [科研](skills/research/SKILL.md) | `research` | `practical-work-research` | 文献、研究设计、计算复现、数据分析、机器学习 |
| [工程](skills/engineering/SKILL.md) | `engineering` | `practical-work-engineering` | 实现与配置、排错、指定改动审查、发布与数据迁移 |
| [交付](skills/delivery/SKILL.md) | `delivery` | `practical-work-delivery` | 文档、表格、演示、跨应用操作 |

Codex、Claude 等插件宿主会为原生名称加上 `practical-work:` 命名空间。独立技能使用完整前缀名称，手动调用语法由客户端决定。`agents/openai.yaml` 提供 Codex 的 UI 配置，其他宿主仍可使用标准 `SKILL.md`；不假定它们解析 OpenAI UI 配置。

## 使用示例

直接描述任务即可，也可指定当前客户端实际显示的技能名称：

```text
使用 practical-work-research 解读这篇论文的实验结果，区分作者报告与材料能支持的结论。

使用 practical-work-engineering 修复退款计算错误：折后商品180元，运费12元不退，预期退款180元。

使用 practical-work-delivery 将已有实验结果整理成报告，沿用提供的模板，不新增研究结论。
```

原生 Codex / Claude 插件的工程入口写作 `practical-work:engineering`。混合任务按动作补充规则，例如分析 CSV 时用科研指导，制作 Excel 时追加交付指导和表格操作能力；复现脚本报错时追加工程排错指导，保留已有研究问题、数据与结果。

普通聊天、标题翻译和轻微润色不启动场景流程。出现“论文”“代码”或 CSV 文件本身不足以决定入口。

## 加载方式

名称与描述用于发现入口。选中后只读取当前细分任务的参考；任务变化时补充所需内容，不重新读取仍有效的规则。

- [共同约束](references/common.md)：约束无依据措辞、泛化保证、多余操作与未经验证的完成声明，保留生产数据恢复条件。
- [应用选择](references/applications.md)：按对象与真实能力选择文献、文件、Drive、实时 Excel、浏览器、计算资源与协作工具。
- 各技能的细分参考：补充该场景判断，不组成默认流程套餐。

当前会话已加载共同约束时直接复用；否则从技能内读取。技能安装不会使普通对话自动加载这些要求，也不会自动改写 `AGENTS.md`、`CLAUDE.md`、`GEMINI.md` 或其他客户端规则。需要全局表达偏好时，将适合自己的要求加入客户端支持的指令文件；具体加载范围遵守该客户端规则。

本项目没有 MCP 服务、hook、后台进程或内置账号连接。科研范围为文献、计算与数据，不包含实验室设备操作与现场采集。专业工具缺失时说明未完成的操作；不把安装插件当作已经获得全部能力。

## 更新

Codex 的 GitHub 安装：

```sh
codex plugin marketplace upgrade practical-work --json
codex plugin add practical-work@practical-work --json
```

Claude Code：`claude plugin marketplace update practical-work-marketplace` 后执行 `claude plugin update practical-work@practical-work-marketplace`。Gemini CLI：`gemini extensions update practical-work`。其他客户端使用其插件管理功能。

独立技能：在源码目录 `git pull --ff-only`，重新运行同一导出命令。更新后开始新会话，不直接修改插件缓存。导出目录中自行添加的文件会保留；若修改受管文件，更新会用源码版本覆盖它们。

## 项目结构

```text
practical-work/
├── plugin.json                      # Agent Plugins 清单
├── .codex-plugin/plugin.json         # Codex 兼容清单
├── .claude-plugin/                   # Claude 插件与市场清单
├── .cursor-plugin/marketplace.json   # Cursor 市场清单
├── .agents/plugins/marketplace.json  # Codex 仓库市场清单
├── gemini-extension.json             # Gemini 扩展清单
├── skills/{research,engineering,delivery}/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/                   # 场景参考与生成的共同参考
├── references/                      # 共同参考唯一维护源
├── scripts/portable_skills.py        # 同步与独立技能导出
├── tests/test_portable_skills.py
└── docs/compatibility.md
```

## 维护

版本为 `0.2.0`。插件与扩展清单保持相同名称和版本。共同文件只修改根 `references/`；为使单个技能可独立安装，随技能携带的副本由脚本生成：

```sh
python scripts/portable_skills.py sync
python scripts/portable_skills.py sync --check
python -m unittest discover -s tests -v
```

导出检查覆盖独立携带、名称改写、受管更新、外来文件保护与 Windows 目录联接拒绝。本机符号链接创建受权限限制，相应测试跳过；未据此声明所有平台都已运行测试。

新增指导对应实际任务，把细分内容放进相应技能参考。检查实际读取范围、操作选择与交付结果，只修正观察到的问题，不以术语命中率代替质量判断。引用路径必须留在技能目录内，不加入个人路径、凭据或固定缓存版本。

## 参考

- [Agent Skills 标准](https://agentskills.io/specification)：技能格式与按需读取资源。
- [OpenAI 插件开发文档](https://developers.openai.com/plugins/build/plugins)：插件打包。
- [各客户端官方兼容资料](docs/compatibility.md)：安装、目录与调用方式。
- [OpenAI Plugins](https://github.com/openai/plugins)、[Anthropic Skills](https://github.com/anthropics/skills)、[Superpowers](https://github.com/obra/superpowers)：项目说明组织的参考。
- [共同规则原始参考](references/common.md#原始参考)：工程判断与问题解决方法。
