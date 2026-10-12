# Agent 安装与发现说明

官方文档核对日期：**2026-10-12**。本页说明目录和清单规则；各客户端是否在本机发现、读取和调用过技能，以 README 的运行记录为准。未运行的客户端不作运行成功承诺。

## 独立技能

从仓库根目录导出三个可单独携带的技能：

```sh
python scripts/portable_skills.py export --output "<skill-directory>"
```

将 `<skill-directory>` 替换为下面适用的项目或全局目录，目标必须位于源码仓库之外。项目安装建议使用目标项目的绝对路径，例如 `C:/work/my-project/.agents/skills`，不要在源码仓库根直接传入 `.agents/skills`。导出结果是 `practical-work-research/`、`practical-work-engineering/`、`practical-work-delivery/`，各自包含 `SKILL.md` 和所需参考文件。前缀用于减少与已有 `research` 等短名冲突；复制时保留整个技能文件夹。

导出不会配置客户端，也不会自动修改全局指令。安装后按客户端的发现或重载方式确认三个名称可见。只复制 `SKILL.md` 会缺少按需读取的材料。

也可以选择本仓库提供的目标目录配置：

```sh
python scripts/portable_skills.py export --target deepseek-harness --scope project --project "<existing-project>"
python scripts/portable_skills.py export --target codebuddy --scope user
```

`--target` 还接受 `antigravity` 和 `antigravity-cli`。作用域默认是 `project`，必须用 `--project` 指向已存在的项目目录；`user` 写入对应用户技能目录。`--output` 与 `--target` 二选一，用于客户端另配了技能根目录的情况。导出目标仍必须位于本仓库之外。

| 客户端及官方说明 | 项目技能目录 | 全局技能目录 |
| --- | --- | --- |
| [Codex](https://developers.openai.com/codex/skills/) | `.agents/skills/` | `~/.agents/skills/` |
| [Claude Code](https://code.claude.com/docs/en/skills#choose-where-skills-load) | `.claude/skills/` | `~/.claude/skills/` |
| [Cursor](https://cursor.com/docs/skills#skill-directories) | `.agents/skills/`、`.cursor/skills/`；也读 `.claude/skills/`、`.codex/skills/` | `~/.agents/skills/`、`~/.cursor/skills/`；也读 `~/.claude/skills/`、`~/.codex/skills/` |
| [Gemini CLI](https://geminicli.com/docs/cli/skills/) | `.gemini/skills/`、`.agents/skills/` | `~/.gemini/skills/`、`~/.agents/skills/` |
| [Copilot CLI](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference) | `.github/skills/`、`.agents/skills/`、`.claude/skills/` | `~/.copilot/skills/`、`~/.agents/skills/` |
| [VS Code / Copilot](https://code.visualstudio.com/docs/agent-customization/agent-skills) | `.github/skills/`、`.claude/skills/`、`.agents/skills/` | `~/.copilot/skills/`、`~/.claude/skills/`、`~/.agents/skills/` |
| [Copilot cloud agent](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills) | 仓库中的 `.github/skills/`、`.claude/skills/`、`.agents/skills/` | 使用仓库目录，不从本机用户目录分发 |
| [OpenCode](https://opencode.ai/docs/skills/) | `.opencode/skills/`、`.claude/skills/`、`.agents/skills/` | `~/.config/opencode/skills/`、`~/.claude/skills/`、`~/.agents/skills/` |
| [Devin Desktop / 当前 Windsurf 文档](https://docs.devin.ai/desktop/cascade/skills) | `.devin/skills/`；兼容 `.windsurf/skills/`、`.agents/skills/` | `~/.config/devin/skills/`、`~/.codeium/windsurf/skills/`、`~/.agents/skills/` |
| [Antigravity 2.0 / IDE](https://antigravity.google/docs/skills?app=antigravity-ide) | `.agents/skills/`；兼容 `.agent/skills/` | `~/.gemini/config/skills/`；IDE 兼容 `~/.gemini/antigravity/skills/` |
| [Antigravity CLI](https://antigravity.google/docs/skills?app=antigravity-ide) | `.agents/skills/`；兼容 `.agent/skills/` | `~/.gemini/antigravity-cli/skills/` |
| [DeepSeek Harness 本地文件系统技能提供方](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.zh.md) | 最近 `.git` 祖先目录下的 `.dsh/skills/`、`.agents/skills/`；没有 `.git` 时用当前工作目录 | `<dshHome>/skills/`，默认 `$DSH_HOME/skills/` 或 `~/.dsh/skills/`；也读 `<agentsHome>/skills/`，默认 `$DSH_AGENTS_HOME/skills/` 或 `~/.agents/skills/` |
| [CodeBuddy Code / CLI](https://www.codebuddy.ai/docs/zh/cli/skills) | `.codebuddy/skills/` | `~/.codebuddy/skills/` |
| [CodeBuddy IDE](https://cloud.tencent.com/document/product/1831/137452) | `.codebuddy/skills/` | 官方技能管理界面支持用户技能；该页未明确用户磁盘目录，不用 CLI 路径替代保证 |

`~` 表示用户主目录。表中一行列出多个目录时选择一个安装即可，避免重复发现。Windsurf 的 [原技能页面](https://docs.windsurf.com/windsurf/cascade/skills) 当前重定向到 Devin Desktop；这些目录不能据此写成任意旧版 Windsurf 均支持。Devin 在启用 Claude 配置兼容后还可读取 `.claude/skills/`。[官方说明](https://docs.devin.ai/desktop/cascade/skills)

可以在任务中明确要求“使用 `practical-work-engineering` 处理这个改动”。Codex 用 `$practical-work-engineering` 提及；Claude Code、Copilot CLI 和 VS Code 支持 `/practical-work-engineering`；Cursor 从 `/` 菜单选择；Devin Desktop / 当前 Windsurf 支持 `@practical-work-engineering`；Antigravity 2.0 / CLI 支持 `/practical-work-engineering`。Gemini CLI 用 `/skills list` 查看、`/skills reload` 重新发现，再在任务中指定名称。OpenCode 由 `skill` 工具按名称读取。以上规则见各行官方说明。

CodeBuddy Code 和 IDE 支持按任务自动选择技能，也支持 `/practical-work-engineering` 手动调用；CLI 用 `/skills` 查看名称。DeepSeek Harness 的 `dsh-tool-skill` 提供按名称读取的 `skill` 工具，并支持用户输入 `/practical-work-engineering` 加载正文。自定义 Harness 部署需要具备技能注册表、文件系统提供方和相应消费能力；仅复制目录不能补齐这些运行时能力。[CodeBuddy CLI](https://www.codebuddy.ai/docs/zh/cli/skills)、[CodeBuddy IDE](https://cloud.tencent.com/document/product/1831/137452)、[DeepSeek Harness 调用能力](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/tool-skill/README.md)

`--target deepseek-harness` 的项目导出会从 `--project` 向上寻找最近的 `.git`；用户导出尊重 `DSH_HOME`。如果 Harness 配置覆写了 `dshHome`、`agentsHome`、`customSkillDirs` 或关闭默认目录扫描，请用 `--output` 指向实际被扫描的目录。该提供方发现技能根目录直接子目录的 `SKILL.md`，不会递归寻找任意嵌套技能或读取插件清单。[发现范围与配置](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.zh.md)

用户全局目录不等于云端目录。Claude Code 的 Cowork / 云端会话不会读取本机 `~/.claude/skills/`；Cursor 的未同步本机技能也不会自动进入云端、远程 SSH 或自托管 worker。[Claude 云端范围](https://code.claude.com/docs/en/skills#use-skills-in-cowork-and-cloud-sessions)、[Cursor 技能范围](https://cursor.com/docs/skills#skill-directories)

## 原生插件或扩展

本仓库源码中的原生插件保留 `research`、`engineering`、`delivery` 三个短名入口。独立技能导出及下面的 Antigravity 专用包使用 `practical-work-` 前缀，指导内容相同。

### Codex

本仓库提供根 `plugin.json`、`.codex-plugin/plugin.json` 和 `.agents/plugins/marketplace.json`，见 [官方包装说明](https://developers.openai.com/plugins/build/plugins)。本机使用插件安装及更新；命令和已执行结果见 [README](../README.md#快速开始)。

### Claude Code

Claude 使用 `.claude-plugin/plugin.json`，市场 `practical-work-marketplace` 由 `.claude-plugin/marketplace.json` 提供。组件位于插件根 `skills/`，不放进 `.claude-plugin/`。[清单规则](https://code.claude.com/docs/en/plugins-reference)

```sh
claude plugin marketplace add Aliarrrrr/practical-work
claude plugin install practical-work@practical-work-marketplace
```

会话中可通过 `/plugin marketplace add Aliarrrrr/practical-work` 注册目录，再在 `/plugin` 中安装。插件入口是 `/practical-work:research`、`/practical-work:engineering`、`/practical-work:delivery`。[注册与安装](https://code.claude.com/docs/en/plugin-marketplaces)、[GitHub 来源](https://code.claude.com/docs/en/plugins/host-marketplace)

开发者可用 `claude plugin validate .` 检查清单；该命令通过只说明它检查的内容，技能实际加载与引用读取仍需在客户端确认。[验证命令](https://code.claude.com/docs/en/plugins-reference#validate-the-manifest)

### Cursor

Cursor 支持本仓库根 `plugin.json` 的 Agent Plugins 格式。`.cursor-plugin/marketplace.json` 用于从 GitHub 导入 `practical-work-marketplace`；纯技能插件无需再添加 Cursor 专属组件。[插件格式](https://cursor.com/docs/reference/plugins#supported-plugin-formats)

在 **Customize → From GitHub Repository** 导入 `Aliarrrrr/practical-work`，然后找到 `practical-work`，选择 **Install** 和项目或用户作用域。技能随后在 Customize 和 `/` 选择菜单中显示。[仓库导入](https://cursor.com/docs/skills#installing-skills-from-a-repository)、[安装作用域](https://cursor.com/docs/plugins#installing-plugins)

CLI 也提供市场注册命令；注册后使用客户端插件界面安装：

```sh
agent plugin marketplace add https://github.com/Aliarrrrr/practical-work.git
```

上述命令来源于 [Cursor CLI 更新记录](https://cursor.com/docs/cli/changelog)。

### Gemini CLI

根 `gemini-extension.json` 提供扩展信息，`skills/` 自动发现三个入口。[扩展规则](https://geminicli.com/docs/extensions/reference/)

```sh
gemini extensions install https://github.com/Aliarrrrr/practical-work
```

安装后用 `/skills list` 确认来源和名称。扩展默认在用户作用域启用，可用扩展的 enable / disable 命令按 `user` 或 `workspace` 作用域管理。开发者可用 `gemini extensions link <local-root>` 读取本地源码。[扩展命令](https://geminicli.com/docs/extensions/reference/)

### Copilot

Copilot CLI 和 VS Code 支持根 `plugin.json` 的 Agent Plugins 格式及 `skills/`。VS Code 需启用 `chat.plugins.enabled` 插件功能。[CLI 插件规范](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference)、[VS Code 插件规范](https://code.visualstudio.com/docs/agent-customization/agent-plugins)

```sh
copilot plugin install Aliarrrrr/practical-work
```

VS Code 使用 **Chat: Install Plugin From Source** 并输入仓库 URL。原生插件技能的名称前缀在不同客户端可能使用不同分隔符，调用时以当前客户端显示的技能名称为准。Copilot cloud agent 可使用上表中的仓库技能目录；本机安装插件不会自动成为云端配置。[VS Code 安装](https://code.visualstudio.com/docs/agent-customization/agent-plugins)、[Cloud agent 技能](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)

### Antigravity 原生插件

Antigravity 的根 `plugin.json` 格式与本仓库的 Agent Plugins 清单不同。使用下面的 `antigravity` 打包格式，包内仅保留 `name`、`description` 清单字段和带前缀的三个 `skills/` 目录；不要直接将源码根清单当成 Antigravity 清单。[官方插件格式](https://www.antigravity.google/docs/plugins?tab=cli)

将 ZIP 内容解压到名为 `practical-work` 的目录，使 `plugin.json` 直接位于该目录中。Antigravity 2.0 / IDE 的项目安装位置是 `<project>/.agents/plugins/practical-work/`，用户安装位置是 `~/.gemini/config/plugins/practical-work/`。CLI 可从解压目录安装：

```sh
agy plugin install "<unpacked-plugin-directory>"
agy plugin list
```

CLI 安装后的存放位置是 `~/.gemini/antigravity-cli/plugins/<plugin-name>/`。上述安装命令和目录来自官方文档；本包尚未在这些客户端安装并观察调用。[各界面安装说明](https://www.antigravity.google/docs/plugins?tab=cli)

默认只随技能按需加载共同约束。打包时加 `--include-common-rule` 才会额外包含 `trigger: always_on` 的共同规则，改变为持续加载；根据使用者需要选择。[规则加载方式](https://www.antigravity.google/docs/rules)

如果已经安装该共同规则，改用不含规则的 ZIP 并解压不会删除旧规则文件；应在客户端停用或移除该规则，才能停止其持续加载。

### CodeBuddy Code / CLI

CodeBuddy 原生插件明确兼容 `.claude-plugin/plugin.json`，因此复用本仓库的 Claude 清单；组件仍位于根 `skills/`。独立技能目录和原生插件是两种入口，插件调用名带插件前缀，例如 `/practical-work:engineering`。[清单兼容与布局](https://www.codebuddy.ai/docs/zh/cli/plugins-reference)

官方提供从本地目录加载插件的会话入口：

```sh
codebuddy --plugin-dir "<local-repository-root>"
```

该方式只对本次会话生效。官方的持久插件安装先注册市场，再安装 `plugin-name@marketplace-name`；市场指南明确列出的清单位置是 `.codebuddy-plugin/marketplace.json`。这里不把 `.claude-plugin/plugin.json` 的兼容规则扩大成本仓库市场文件已被自动识别的结论。需要直接安装技能时使用上面的 `--target codebuddy` 导出。[本地插件入口](https://www.codebuddy.ai/docs/zh/cli/plugins)、[市场安装方式](https://www.codebuddy.ai/docs/zh/cli/plugin-marketplaces)

## 单技能和专用 ZIP 包

在仓库根目录运行以下命令，输出目录必须在源码仓库之外：

```sh
python scripts/package_skills.py --format skills --output "<outside-output-directory>"
python scripts/package_skills.py --format antigravity --output "<outside-output-directory>"
python scripts/package_skills.py --format workbuddy-enterprise --category "<enterprise-category>" --output "<outside-output-directory>"
```

三个格式分别写入输出目录下的 `skills/`、`antigravity/` 和 `workbuddy-enterprise/`，ZIP 文件名包含当前版本（本次为 `0.3.0`）。它们的用途和布局不同：

| 格式 | 内容与使用方式 |
| --- | --- |
| `skills` | 三个独立 ZIP，各自根目录是 `SKILL.md` 与 `references/`。解压到对应的 `practical-work-<scene>/` 文件夹后，整个文件夹可放入上表的技能目录。 |
| `antigravity` | 一个完整插件 ZIP，根目录是 Antigravity 专用 `plugin.json` 与 `skills/`。按上面的原生插件安装说明使用。可另加 `--include-common-rule`。 |
| `workbuddy-enterprise` | 三个独立 ZIP，每包包含一个 `practical-work-<scene>/` 顶层目录，内有 `SKILL.md`、`references/` 与 `manifest.yaml`。用于企业管理端的 Skill 上传入口。 |

### WorkBuddy 个人桌面

在技能页选择 **添加技能 → 上传技能**，按客户端提示选择本地技能包。官方说明上传或创建的技能默认供所有项目使用，也可按项目存放；没有在该页明确具体磁盘路径。创建后的技能可由自然语言任务触发。[个人技能界面](https://www.codebuddy.ai/docs/zh/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)、[作用域说明](https://intl.cloud.tencent.com/zh/document/product/1316/84503)、[自然语言调用](https://www.codebuddy.ai/docs/zh/workbuddy/From-Beginner-to-Expert-Guide/Practice-Cases/Create-Skills)

这些文档没有明确个人桌面导入包的 ZIP 根布局，也没有确认直接从 GitHub 或 URL 导入。`skills` 格式提供完整的单技能下载包；尚未在 WorkBuddy 个人桌面试导入，不保证该客户端接受这一 ZIP 布局。个人包不添加企业管理用的 `manifest.yaml`。

### WorkBuddy Enterprise 管理端

企业管理后台的 **AI 资源管理 → Skill 管理 → 上传 Skill** 明确接受 `.zip`；官方目录图要求技能目录同时包含 `SKILL.md` 与 `manifest.yaml`。本仓库企业包沿用该图的单技能目录包装层，尚未确认实际导入；它与个人桌面的本地包入口不同。[企业上传规范](https://intl.cloud.tencent.com/zh/document/product/1316/84533)

企业包的 manifest 按官方最小示例生成五个字段：`name`、`version`、`description`、`category`、`author`。版号来自插件清单；`--category` 必须填写企业使用的分类，`--author` 可覆盖默认的 `Aliarrrrr`。官方示例的 `data-processing` 不是已公布的分类枚举，管理端允许创建分类；文档没有提供逐字段 schema 或说明 ZIP 是否还接受省略顶层技能目录的布局。因此这些字段和包装选择按示例提供，不宣称已通过企业管理端导入。[manifest 示例与分类配置](https://intl.cloud.tencent.com/zh/document/product/1316/84533)

## 检查范围

本仓库的检查应分别说明技能名称、随附引用、清单格式及实际客户端加载的结果。目录和清单符合规范，不能替代客户端运行。自动调用还取决于请求内容、客户端版本、模型与已有规则；必要时用名称明确选择入口。

本插件只提供任务指导。文件渲染、浏览器、应用接口和外部账号能力使用所在环境已有的工具；安装技能不会增加连接、服务或后台进程。
