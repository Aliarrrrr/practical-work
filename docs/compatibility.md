# Agent 安装与发现说明

官方文档核对日期：**2026-10-12**。本页说明目录和清单规则；各客户端是否在本机发现、读取和调用过技能，以 README 的运行记录为准。未运行的客户端不作运行成功承诺。

## 独立技能

从仓库根目录导出三个可单独携带的技能：

```sh
python scripts/portable_skills.py export --output "<skill-directory>"
```

将 `<skill-directory>` 替换为下面适用的项目或全局目录，目标必须位于源码仓库之外。项目安装建议使用目标项目的绝对路径，例如 `C:/work/my-project/.agents/skills`，不要在源码仓库根直接传入 `.agents/skills`。导出结果是 `practical-work-research/`、`practical-work-engineering/`、`practical-work-delivery/`，各自包含 `SKILL.md` 和所需参考文件。前缀用于减少与已有 `research` 等短名冲突；复制时保留整个技能文件夹。

导出不会配置客户端，也不会自动修改全局指令。安装后按客户端的发现或重载方式确认三个名称可见。只复制 `SKILL.md` 会缺少按需读取的材料。

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

`~` 表示用户主目录。表中一行列出多个目录时选择一个安装即可，避免重复发现。Windsurf 的 [原技能页面](https://docs.windsurf.com/windsurf/cascade/skills) 当前重定向到 Devin Desktop；这些目录不能据此写成任意旧版 Windsurf 均支持。Devin 在启用 Claude 配置兼容后还可读取 `.claude/skills/`。[官方说明](https://docs.devin.ai/desktop/cascade/skills)

可以在任务中明确要求“使用 `practical-work-engineering` 处理这个改动”。Codex 用 `$practical-work-engineering` 提及；Claude Code、Copilot CLI 和 VS Code 支持 `/practical-work-engineering`；Cursor 从 `/` 菜单选择；Devin Desktop / 当前 Windsurf 支持 `@practical-work-engineering`；Antigravity 2.0 / CLI 支持 `/practical-work-engineering`。Gemini CLI 用 `/skills list` 查看、`/skills reload` 重新发现，再在任务中指定名称。OpenCode 由 `skill` 工具按名称读取。以上规则见各行官方说明。

用户全局目录不等于云端目录。Claude Code 的 Cowork / 云端会话不会读取本机 `~/.claude/skills/`；Cursor 的未同步本机技能也不会自动进入云端、远程 SSH 或自托管 worker。[Claude 云端范围](https://code.claude.com/docs/en/skills#use-skills-in-cowork-and-cloud-sessions)、[Cursor 技能范围](https://cursor.com/docs/skills#skill-directories)

## 原生插件或扩展

原生插件保留 `research`、`engineering`、`delivery` 三个短名入口。独立技能导出的名称带 `practical-work-` 前缀，二者的指导内容相同。

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

## 检查范围

本仓库的检查应分别说明技能名称、随附引用、清单格式及实际客户端加载的结果。目录和清单符合规范，不能替代客户端运行。自动调用还取决于请求内容、客户端版本、模型与已有规则；必要时用名称明确选择入口。

本插件只提供任务指导。文件渲染、浏览器、应用接口和外部账号能力使用所在环境已有的工具；安装技能不会增加连接、服务或后台进程。
