# 务实科研、工程与交付

本地插件 `practical-work`，版本 `0.1.0`。三个入口根据当前动作选择短参考，应用操作采用已有专业技能。

| 入口 | 用途 |
| --- | --- |
| `practical-work:research` | 文献理解、研究设计、计算复现、科学数据与机器学习研究 |
| `practical-work:engineering` | 软件实现、排错、改动审查、配置、发布和数据迁移 |
| `practical-work:delivery` | 文档、表格、演示和跨应用交付 |

入口允许根据实际任务自动选择，也可以明确指定。普通聊天、短翻译和轻微润色只应用用户全局表达约束；文件或应用操作仍采用所需的专业能力。

共享工作约束在 `references/common.md`，应用选择在 `references/applications.md`。用户全局已经加载同一共同约束时复用，不重复读取。细分规则在各入口的 `references/`，只按当前动作读取；混合任务追加当前阶段需要的内容。

## 从 GitHub 安装

仓库为 `Aliarrrrr/practical-work`，可见性为私有；安装者需要对应仓库的读取权限和已配置的 Git 认证。仓库内包含插件及其目录清单：

```powershell
codex plugin marketplace add Aliarrrrr/practical-work --ref main --json
codex plugin add practical-work@practical-work --json
codex plugin list --marketplace practical-work --json
```

也可以先克隆仓库，在仓库目录运行 `codex plugin marketplace add . --json`，再安装同一插件。已有 `practical-work@zlf-local` 本地安装者可继续使用原来源，不必再启用同名插件的另一份安装。

本仓库不修改安装者的全局规则。入口在没有对应全局约束时读取 `references/common.md`；安装者可将适合自己的共同偏好加入全局 AGENTS。原本机 `$practical-engineering` 手动兼容入口属于个人配置，不随本仓库分发。实际技能入口位置从当前目录发现，不固定缓存版本路径。

## 更新与检查

修改源码，保持根 `plugin.json` 和 `.codex-plugin/plugin.json` 的身份、版本及展示信息一致。GitHub 安装可用 `codex plugin marketplace upgrade practical-work --json` 更新目录快照，再用 `codex plugin add practical-work@practical-work --json` 刷新安装；原本地来源继续使用其安装命令。随后在新会话核对读取到的文件和实际任务表现，不能仅凭命令成功就断言改动已加载。桌面仍显示旧内容时重启应用再核对。不要直接编辑缓存副本。

插件不包含 MCP 服务、账号连接或后台进程，不向现有工具增加权限。科研范围为文献、计算与数据，不执行实验室设备或现场采集。缺少连接时准确说明尚未完成的外部操作。
