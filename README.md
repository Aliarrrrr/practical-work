# Practical Work

**务实科研、工程与交付：面向 Codex 的任务指导插件。**

Practical Work 提供科研、软件工程和交付协作三个技能入口，帮助 agent 围绕具体问题选择工作、验证实际结果，并准确说明结论范围。目标是减少空泛保证和无用途流程，同时保留必要的检查与数据保护。

详细规则按当前任务读取。文档、表格、演示及外部应用的实际操作，交给运行环境中已有的专业技能和工具。

[快速开始](#快速开始) · [技能目录](#技能目录) · [使用示例](#使用示例) · [加载方式](#加载方式) · [更新](#更新) · [项目结构](#项目结构)

## 快速开始

### 环境要求

- 支持 `codex plugin` 命令的 Codex CLI，以及可用的 Git。
- 本仓库当前为私有仓库；Git 认证需具备 `Aliarrrrr/practical-work` 的读取权限。
- 创建文件或操作应用时，当前环境需具备相应专业技能、工具或已授权连接。

本项目的安装、入口发现和代表性任务已在 Windows 的 Codex CLI `0.162.0-alpha.17.2` 上验证。

### 从 GitHub 安装

```sh
codex plugin marketplace add Aliarrrrr/practical-work --ref main --json
codex plugin add practical-work@practical-work --json
codex plugin list --marketplace practical-work --json
```

确认列表中 `practical-work@practical-work` 已安装且启用，然后开始新会话，查看技能选择器中是否出现三个入口。桌面应用仍显示旧目录时，重启应用后再检查。

### 从本地源码安装

```sh
git clone https://github.com/Aliarrrrr/practical-work.git
cd practical-work
codex plugin marketplace add . --json
codex plugin add practical-work@practical-work --json
```

两种安装方式选择一种即可。已有 `practical-work@zlf-local` 安装者可继续使用原来源，避免同时启用同名插件的两份安装。

## 技能目录

| 技能 | 适用任务 | 按需读取的主题 |
| --- | --- | --- |
| [practical-work:research](skills/research/SKILL.md) | 文献理解、研究设计、计算复现与科学数据分析 | 阅读、研究设计、实验、统计分析、机器学习 |
| [practical-work:engineering](skills/engineering/SKILL.md) | 软件实现、故障排查、改动审查、配置与发布迁移 | 改动、排错、审查、发布与数据恢复 |
| [practical-work:delivery](skills/delivery/SKILL.md) | 报告、文档、表格、演示与跨应用交付 | 文档、表格、演示、跨应用操作 |

三个入口均允许根据任务描述自动选择，也可以在 Codex 的技能选择器中明确选用。是否调用取决于当前要完成的动作；单纯出现“论文”“代码”或 CSV 文件，不足以决定场景。

## 使用示例

可以直接描述任务，也可以写明要使用的入口：

```text
使用 practical-work:research 解读这篇论文的实验结果，区分作者报告的发现和材料能支持的结论。

使用 practical-work:engineering 修复这个退款计算错误。商品折后金额为180元，运费12元不退，预期退款为180元。

使用 practical-work:delivery 把已有实验结果整理成报告，沿用提供的模板，不新增研究结论。
```

混合任务按当前动作补充指导。例如：

```text
分析 CSV 中 A、B 两组的观察差异，并把结果和解释整理成 Excel。
```

分析阶段使用科研规则，制作工作簿时补充交付规则和表格能力。若复现脚本报错，追加工程排错指导，并保留已有研究问题与数据上下文。

普通聊天、短翻译和轻微润色不启动场景流程；涉及真实文件或应用操作时，仍使用所需的专业能力。

## 加载方式

技能的名称和描述用于发现入口。选中入口后，agent 根据当前动作读取对应参考，任务变化时再补充相关内容；已加载且仍有效的上下文继续复用。

- [共同约束](references/common.md)：约束无依据术语、泛化保证、多余操作和未经验证的完成声明。生产数据操作保留原始数据恢复与副本转换要求。
- [应用选择](references/applications.md)：按实际对象选择 PDF、本地文件、Google Drive、实时 Excel、浏览器、Hugging Face 和项目协作能力。
- 各技能的 `references/`：提供该场景的细分判断，不要求每次读取全部内容。

已有全局共同约束时直接复用；缺少时，场景入口读取插件内的共同约束。插件不会自动修改安装者的全局 `AGENTS.md`。若希望普通对话也默认遵守这些表达偏好，可将适合自己的要求加入全局规则。

## 集成与范围

文件格式、渲染、表格计算和应用接口操作采用环境已有的专业能力。Word、独立 Excel 文件与实时 Excel 会话分别选择对应工具；Google Docs、Sheets、Slides 使用对应连接；科学图表使用真实数据与标准绘图工具。具体选择见 [应用说明](references/applications.md)。

首版包含技能说明和参考文件，没有捆绑 MCP 服务、账号连接或后台进程。外部能力需要在当前环境中可用，并遵守用户授权。科研执行范围为文献、计算与数据，不包含实验室设备操作或现场采集。

已有项目的必要检查、系统与开发者规则及执行权限继续生效。插件提供任务指导，实际结果仍需通过相应材料、计算或操作判断。

## 更新

从 GitHub 安装时，刷新目录快照并重新安装插件：

```sh
codex plugin marketplace upgrade practical-work --json
codex plugin add practical-work@practical-work --json
```

从本地源码安装时，更新源码后重新运行 `codex plugin add practical-work@practical-work --json`；其他本地来源使用对应的插件标识。更新后在新会话确认读取到的内容，不直接编辑安装缓存。

## 项目结构

```text
practical-work/
├── plugin.json                         # 插件清单
├── .codex-plugin/plugin.json           # Codex 兼容清单
├── .agents/plugins/marketplace.json    # 仓库目录清单
├── skills/
│   ├── research/
│   ├── engineering/
│   └── delivery/
└── references/
    ├── common.md                      # 共同工作约束
    └── applications.md                # 应用与工具选择
```

每个技能目录包含 `SKILL.md`、`agents/openai.yaml` 和按需读取的 `references/`。两个插件清单保持相同的名称、版本和展示信息。

## 维护与扩展

新增指导应对应实际任务，把细分内容放进所属技能的参考文件，并在入口说明何时读取。检查同类请求、容易混淆的请求和混合任务，确认调用范围与实际结果；只针对观察到的问题修改规则。

仅增加参考内容不应变成新的默认流程。修改应用操作说明时核对当前专业技能和可用工具，避免写入个人绝对路径、凭据或固定缓存版本。

## 相关资料

- [OpenAI Plugins](https://github.com/openai/plugins)、[Anthropic Skills](https://github.com/anthropics/skills) 和 [Superpowers](https://github.com/obra/superpowers)：README 组织与项目说明的参考。
- [OpenAI 插件开发文档](https://developers.openai.com/plugins/build/plugins)、[Agent Skills 标准](https://agentskills.io)：插件与技能格式。
- [共同约束的原始参考](references/common.md#原始参考)：工程判断和问题解决方法的来源。
