# Practical Work

[简体中文](README.md) | [English](README.en.md)

**把空泛表达改成言之有物的说明，并辅助科研、工程与交付工作。**

Practical Work 识别语境中的空泛术语、无依据承诺和模板式反省：能说明对象、动作和结果时具体改写，信息不足时缩小结论或删除承诺，准确的技术用法与引用保留。科研、软件工程与交付三个入口帮助 agent 选择有用途的动作、检查声称完成的行为，同时保留项目必要检查、用户授权与数据恢复条件。

规则按当前任务读取。文件制作、应用操作和专业计算采用当前环境已有的技能与工具，不绑定 Codex 的工具名称。

默认方法借鉴 Karpathy 等人的经验，按适用条件使用，不作为每个任务必须执行的流程。可以直接使用；也可主动选择 [定制自己的基座](references/customization.md)，由模型复用已有信息、按需提问，并生成现有技能与参考文件的修改稿。默认使用无需问卷，定制不自动覆盖已安装插件或全局规则。

RSI 在这里是针对使用中具体不顺手之处改写、删除或简化相关指导，再用受影响的任务检查效果；不默认增加每次任务的日志、评分、自评或自动优化。

[本版改动](docs/release-0.3.2.md) · [既有验收](docs/acceptance-0.3.1.md) · [快速开始](#快速开始) · [兼容性](#兼容性) · [技能目录](#技能目录) · [使用示例](#使用示例) · [加载方式](#加载方式) · [维护](#维护)

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

### DeepSeek Harness

以下 Python 命令需先克隆仓库并进入源码目录：

```sh
git clone https://github.com/Aliarrrrr/practical-work.git
cd practical-work
```

导出到指定项目或用户的原生技能目录：

```sh
python scripts/portable_skills.py export --target deepseek-harness --project "C:/work/my-project"
python scripts/portable_skills.py export --target deepseek-harness --scope user
```

两条命令按所需作用域选择一条。项目目标按 Harness 的规则定位最近 `.git` 祖先；用户目标为 `$DSH_HOME/skills`，未设置时使用 `~/.dsh/skills`。自定义 `dshHome`、`customSkillDirs` 或 SDK 组合使用 `--output` 指定实际目录。宿主需要提供技能注册、文件发现和加载能力；本脚本不修改 Harness 配置。

可使用 `/practical-work-engineering` 等完整技能名。这里适配的是 **DeepSeek Harness** 的文件发现与资源读取，不是将 DeepSeek 模型接入其他客户端；仓库根 `plugin.json` 也不是 Cordis 插件。

### Antigravity IDE 与 CLI

只安装按需技能时：

```sh
python scripts/portable_skills.py export --target antigravity --project "C:/work/my-project"
python scripts/portable_skills.py export --target antigravity --scope user
```

CLI 的用户目录不同，用 `--target antigravity-cli --scope user`；不要把 IDE 用户目录当作 CLI 用户目录。旧版本或自定义目录可通过 `--output` 指定，范围见兼容说明。

需要原生插件包时另行生成：

```sh
python scripts/package_skills.py --format antigravity --output "../practical-work-packages"
```

解压生成的 ZIP 到名为 `practical-work` 的插件目录；IDE 使用项目 `.agents/plugins/` 或用户 `~/.gemini/config/plugins/`。CLI 可执行 `agy plugin install <解压目录>`。该包只使用 Antigravity 清单支持的字段，不直接复制仓库根清单。

默认仍按任务加载技能。若需要在 Antigravity 普通对话中持续应用共同约束，打包时加 `--include-common-rule`，生成 `always_on` 规则；只安装技能不等于共同约束始终生效。

停用已经安装的共同规则时，在客户端停用或移除该规则；重新解压不含规则的 ZIP 不会自动删除旧文件。

### WorkBuddy、WorkBuddy Enterprise 与 CodeBuddy

先生成三个完整的单技能包：

```sh
python scripts/package_skills.py --format skills --output "../practical-work-packages"
```

个人 WorkBuddy 的技能页提供“添加技能／上传本地技能包”。本项目提供 ZIP 和可解压的完整目录；官方说明没有明确接受的 ZIP 根布局，尚未在 WorkBuddy 中试导入，按当前界面实际支持的包形式使用。不能把 CodeBuddy 的磁盘目录当作 WorkBuddy 个人版目录。

WorkBuddy Enterprise 管理端使用专门格式，分类由企业管理员配置：

```sh
python scripts/package_skills.py --format workbuddy-enterprise --category "your-enterprise-category" --output "../practical-work-packages"
```

企业包额外包含 `manifest.yaml`；可用 `--author` 指定作者。它与个人包分别生成，不默认给个人技能增加企业字段。企业导入与分类权限尚未在管理端验证。

CodeBuddy Code 的原生目录可直接导出：

```sh
python scripts/portable_skills.py export --target codebuddy --project "C:/work/my-project"
python scripts/portable_skills.py export --target codebuddy --scope user
```

它也支持已有的 Claude 插件清单；CodeBuddy IDE 的项目技能目录同为 `.codebuddy/skills/`，用户作用域按其管理界面选择。完整来源与产品范围见 [兼容说明](docs/compatibility.md)。

### 独立技能：OpenCode、Windsurf 及其他兼容客户端

用 Python 3.10 或以上版本导出三个完整技能目录，无第三方 Python 依赖：

```sh
git clone https://github.com/Aliarrrrr/practical-work.git
cd practical-work
python scripts/portable_skills.py export --output /path/to/project/.agents/skills
```

把示例路径替换为目标项目的技能目录；Windows 也可使用 `C:/path/to/project/.agents/skills`。Claude Code 项目改用 `.claude/skills`，旧版 Windsurf 可用 `.windsurf/skills`。各客户端的用户目录与项目目录见 [兼容说明](docs/compatibility.md)。

上述导出和打包命令从本仓库根运行，需要 Python 3.10 或以上版本；输出位置须在源码仓库之外。打包不会安装客户端、启用服务或连接账号。

导出的名称为 `practical-work-research`、`practical-work-engineering`、`practical-work-delivery`。每个目录包含所需参考文件，可以单独移动或安装；不要只复制 `SKILL.md`。脚本拒绝覆盖非本工具创建的同名目录，重复导出会更新受管文件并保留额外文件。它不修改全局指令、客户端设置或连接账号。

## 兼容性

下表记录此前的客户端与文件检查；`0.3.2` 尚未在新客户端会话加载。

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
| DeepSeek Harness | 原生目录中的独立技能 | 官方 `0.2.0-rc.2` 提供器发现与资源读取检查；不代表桌面或模型行为 |
| Antigravity IDE / CLI | 独立技能、专用原生插件包 | 官方目录与清单、生成产物核对；未验证客户端加载 |
| WorkBuddy 个人版 | 完整单技能包 | 提供本地包；实际 UI 导入未验证 |
| WorkBuddy Enterprise | 含 `manifest.yaml` 的单技能 ZIP | 官方目录示例与生成产物核对；管理端导入未验证 |
| CodeBuddy Code / IDE | 独立技能；Code 支持现有 Claude 清单 | 官方能力与目录核对；未运行客户端 |

各客户端的具体版本、技能开关、权限与模型会影响发现和自动选择。目录与文件检查不能证明未运行客户端的实际行为。核对日期和官方来源见 [兼容说明](docs/compatibility.md)。

此前本机 Codex 已安装并启用 `0.3.0`；`0.2.0` 曾在新会话读取工程入口和改动参考，Claude Code 也曾通过本地 `--plugin-dir` 发现三个入口并读取共同约束与排错参考。Claude 当时配置的 DeepSeek-V4-flash 在示例分析中仍出现多余文件查找，后补充了相应排错指导。这些是历史加载记录，不能代替 `0.3.2` 的新会话加载验证，也不证明全部任务判断正确。

此前用 Node `v24.12.0`、`@deepseek-ai/cordis` `4.0.4` 及 `dsh-skill`、`dsh-skill-filesystem` `0.2.0-rc.2` 在临时目录检查：三个导出技能均被官方提供器发现，正文正确加载，资源基准指向各自目录，共同约束及所选细分参考可读。没有运行 DSH 桌面、SDK 会话或模型请求。

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

名称与描述用于发现入口。选中后只读取当前细分任务的参考；已注入或已读的相同内容直接复用。只有内容已变、已有片段不足或来源版本不明且影响判断时，才补读相关部分，不因进入下一步或继续对话而重读整个文件。

- [共同约束](references/common.md)：约束无依据措辞、泛化保证、多余操作与未经验证的完成声明，保留生产数据恢复条件。
- [应用选择](references/applications.md)：按对象与真实能力选择文献、文件、Drive、实时 Excel、浏览器、计算资源与协作工具。
- 各技能的细分参考：补充该场景判断，不组成默认流程套餐。

当前会话已加载共同约束时直接复用；否则从技能内读取。技能安装不会使普通对话自动加载这些要求，也不会自动改写 `AGENTS.md`、`CLAUDE.md`、`GEMINI.md` 或其他客户端规则。需要全局表达偏好时，将适合自己的要求加入客户端支持的指令文件；具体加载范围遵守该客户端规则。

任务明确要求编码、换行或逐字输出时，保留对应要求，并核对实际交付文件或标准输出；只比较源码或测试文件，不能据此确认标准输出的字节。

本项目没有 MCP 服务、hook、后台进程或内置账号连接。科研范围为文献、计算与数据，不包含实验室设备操作与现场采集。专业工具缺失时说明未完成的操作；不把安装插件当作已经获得全部能力。

宿主已经注入完整技能正文时直接使用，避免再调用一次加载工具。引用从宿主给出的技能目录或资源基准解析，不从当前项目目录猜路径。界面菜单、工具名称和调用语法由宿主决定，采用实际可用能力。

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
├── README.md / README.en.md         # 中英文使用说明
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
├── scripts/package_skills.py         # 单技能、企业及 Antigravity 包
├── tests/test_portable_skills.py
├── tests/test_package_skills.py
└── docs/compatibility.md
```

## 维护

当前版本为 `0.3.2`。本轮根据已有审查反馈，明确复用已读材料、按需补读，并在任务明确要求时核对编码、换行与标准输出字节。中英文 README 提供相同的安装与使用范围；技能正文仍为中文。改动与检查见 [本版说明](docs/release-0.3.2.md)。

此前两批离线审查覆盖 92 份记录：91 份满足原任务，1 份运行未确认，另保留已知输出字节失败。14 对 A/B 的任务与表达判断均持平，尚未证明插件整体改善效果，RSI 也未完成，详见 [0.3.1 版本验收](docs/acceptance-0.3.1.md)。这些结果属于微调前的指导，本轮未重跑模型评测。

仓库内插件与扩展清单保持相同名称和版本；Antigravity 专用清单不写其格式未声明的版本字段，包文件名记录版本。共同文件只修改根 `references/`；为使单个技能可独立安装，随技能携带的副本由脚本生成：

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
