[English](README.en.md) | [简体中文](README.md)

# Practical Work

**Replace vague language with concrete explanations, and support research, engineering, and delivery work.**

Practical Work helps an agent recognize vague terminology, unsupported promises, and formulaic self-reflection in context. When the available information identifies the object, action, and result, it makes the wording specific. When information is missing, it narrows the conclusion or removes the promise. Accurate technical usage and quotations remain intact. Three entry points help the agent choose useful work and check the behavior it claims to have completed, while retaining required project checks, user authorization, and data recovery requirements.

The two READMEs describe the same installation and usage scope. Skill instructions and references remain in Chinese.

Guidance is loaded for the current task. File creation, application control, and specialized calculations use the skills and tools available in the host environment; the plugin does not depend on Codex-specific tool names.

The default guidance draws on practices from Karpathy and others, applied where useful rather than imposed as a workflow for every task. Use it directly, or explicitly choose [customization](references/customization.md): the agent reuses existing information, asks only for details that affect the result, and proposes edits to the existing skills and reference files. Default use requires no questionnaire. Customization does not automatically overwrite installed plugins or global instructions.

Here, RSI means revising, deleting, or simplifying guidance in response to a specific difficulty encountered during use, then checking the affected tasks. It does not add logging, scoring, self-evaluation, or automatic optimization to every task.

[0.3.2 changes and checks](docs/release-0.3.2.md) · [Historical 0.3.1 acceptance results](docs/acceptance-0.3.1.md) · [Quick start](#quick-start) · [Compatibility](#compatibility) · [Skills](#skills) · [Examples](#examples) · [Loading](#loading) · [Maintenance](#maintenance)

## Quick start

Choose one installation method. Native plugins and standalone skills contain the same guidance; avoid installing both in the same client.

### Codex

```sh
codex plugin marketplace add Aliarrrrr/practical-work --ref main --json
codex plugin add practical-work@practical-work --json
codex plugin list --marketplace practical-work --json
```

This requires Git and a CLI that supports `codex plugin`. Confirm that the plugin is installed and enabled, then start a new session to find the three `practical-work:*` entry points. Existing installations from `practical-work@zlf-local` can continue using that source.

### Claude Code

```sh
claude plugin marketplace add Aliarrrrr/practical-work
claude plugin install practical-work@practical-work-marketplace
```

In a new session, use `/practical-work:research`, `/practical-work:engineering`, or `/practical-work:delivery`.

### Gemini CLI

```sh
gemini extensions install https://github.com/Aliarrrrr/practical-work
```

Restart the session and use `/skills list` to confirm that `research`, `engineering`, and `delivery` are available. These are skills, not three commands registered by the extension. The prefixed standalone skills described below can avoid conflicts with existing skill names.

### GitHub Copilot CLI

```sh
copilot plugin install Aliarrrrr/practical-work
```

In VS Code, run **Chat: Install Plugin From Source** from the command palette and enter the repository URL. `chat.plugins.enabled` must be enabled. Cloud agents use project-local skill directories and cannot depend on your local user directory.

### Cursor

In **Customize → From GitHub Repository**, add `https://github.com/Aliarrrrr/practical-work` and choose plugin installation. The repository includes the marketplace manifest required by Cursor.

### DeepSeek Harness

Before running the Python commands below, clone the repository and enter its source directory:

```sh
git clone https://github.com/Aliarrrrr/practical-work.git
cd practical-work
```

Export to the native skill directory for a project or user:

```sh
python scripts/portable_skills.py export --target deepseek-harness --project "C:/work/my-project"
python scripts/portable_skills.py export --target deepseek-harness --scope user
```

Choose one command for the required scope. The project target follows Harness rules to locate the nearest `.git` ancestor. The user target is `$DSH_HOME/skills`, or `~/.dsh/skills` when the variable is unset. For a custom `dshHome`, `customSkillDirs`, or SDK setup, use `--output` to specify the actual directory. The host must provide skill registration, file discovery, and loading; this script does not change Harness configuration.

Use the full skill name, such as `/practical-work-engineering`. This integration covers **DeepSeek Harness** file discovery and resource reading. It does not connect a DeepSeek model to another client, and the root `plugin.json` is not a Cordis plugin.

### Antigravity IDE and CLI

To install skills for loading as needed:

```sh
python scripts/portable_skills.py export --target antigravity --project "C:/work/my-project"
python scripts/portable_skills.py export --target antigravity --scope user
```

The CLI has a different user directory: use `--target antigravity-cli --scope user`. Do not use the IDE's user directory for the CLI. For older versions or custom directories, specify `--output`; see the compatibility notes for the supported scope.

To generate a native plugin package instead:

```sh
python scripts/package_skills.py --format antigravity --output "../practical-work-packages"
```

Extract the generated ZIP into a plugin directory named `practical-work`. The IDE uses the project's `.agents/plugins/` or the user's `~/.gemini/config/plugins/`. For the CLI, run `agy plugin install <extracted-directory>`. This package uses fields supported by the Antigravity manifest rather than copying the root repository manifest.

Skills are still loaded by task by default. To keep the common guidance active during ordinary Antigravity conversations, add `--include-common-rule` when packaging. This generates an `always_on` rule. Installing skills alone does not make the common guidance always active.

To disable an already installed common rule, disable or remove it in the client. Extracting a new ZIP without the rule does not automatically delete the old file.

### WorkBuddy, WorkBuddy Enterprise, and CodeBuddy

First, generate three complete single-skill packages:

```sh
python scripts/package_skills.py --format skills --output "../practical-work-packages"
```

Personal WorkBuddy provides an **Add skill / Upload local skill package** option on its skills page. This project supplies ZIP files and complete directories that can be extracted. Official guidance does not specify the accepted ZIP root layout, and import has not been tried in WorkBuddy. Use the package form supported by the current interface. CodeBuddy's on-disk directories are not personal WorkBuddy directories.

WorkBuddy Enterprise's admin interface uses a separate format. An enterprise administrator configures the category:

```sh
python scripts/package_skills.py --format workbuddy-enterprise --category "your-enterprise-category" --output "../practical-work-packages"
```

Enterprise packages also contain `manifest.yaml`; use `--author` to set the author. They are generated separately from personal packages, without adding enterprise fields to personal skills by default. Enterprise import and category permissions have not been checked in the admin interface.

Export directly to CodeBuddy Code's native directories:

```sh
python scripts/portable_skills.py export --target codebuddy --project "C:/work/my-project"
python scripts/portable_skills.py export --target codebuddy --scope user
```

CodeBuddy Code also supports the existing Claude plugin manifest. CodeBuddy IDE uses `.codebuddy/skills/` for project skills; select the user scope through its management interface. See [compatibility notes](docs/compatibility.md) for sources and product scope.

### Standalone skills: OpenCode, Windsurf, and other compatible clients

Use Python 3.10 or later to export three complete skill directories. No third-party Python dependencies are required:

```sh
git clone https://github.com/Aliarrrrr/practical-work.git
cd practical-work
python scripts/portable_skills.py export --output /path/to/project/.agents/skills
```

Replace the example path with the target project's skill directory. On Windows, a path such as `C:/path/to/project/.agents/skills` also works. Use `.claude/skills` for a Claude Code project; older Windsurf versions can use `.windsurf/skills`. See [compatibility notes](docs/compatibility.md) for each client's user and project directories.

Run all export and packaging commands above from this repository's root with Python 3.10 or later. Output must be outside the source repository. Packaging does not install clients, enable services, or connect accounts.

The exported names are `practical-work-research`, `practical-work-engineering`, and `practical-work-delivery`. Each directory contains its required reference files and can be moved or installed independently. Do not copy only `SKILL.md`. The script refuses to overwrite same-named directories it did not create. Re-exporting updates managed files and preserves additional files. It does not modify global instructions, client settings, or account connections.

## Compatibility

The table describes the installation forms supplied and checks recorded before 0.3.2. Client-loading results are historical; 0.3.2 has not been loaded in a new client session.

| Client | Installation forms supplied | Recorded check scope |
| --- | --- | --- |
| Codex | Native plugin, standalone skills | Historical installation and new-session loading on Windows CLI `0.162.0-alpha.17.2` |
| Claude Code | Native plugin, standalone skills | Historical manifest validation and local plugin loading on Windows `2.1.245` |
| Cursor | Agent Plugins plugin, standalone skills | Manifest and skill-directory comparison with official documentation |
| Gemini CLI | Extension, standalone skills | Extension and skill-directory comparison with official documentation |
| GitHub Copilot CLI / VS Code | Agent Plugins plugin, standalone skills | Format and installation-entry comparison with official documentation |
| Copilot cloud agent | Project-local standalone skills | Directory comparison with official documentation; no cloud task run |
| OpenCode | Standalone skills | Directory comparison with official documentation |
| Windsurf / current Devin Desktop | Standalone skills | Directory comparison with documentation current at the recorded check date; arbitrary older versions are not covered |
| DeepSeek Harness | Standalone skills in native directories | Historical discovery and resource-reading checks with the official `0.2.0-rc.2` provider; no desktop or model-behavior result |
| Antigravity IDE / CLI | Standalone skills, dedicated native plugin package | Official directories, manifests, and generated files checked; client loading untested |
| Personal WorkBuddy | Complete single-skill packages | Local packages supplied; UI import untested |
| WorkBuddy Enterprise | Single-skill ZIP with `manifest.yaml` | Official directory examples and generated files checked; admin import untested |
| CodeBuddy Code / IDE | Standalone skills; Code also supports the existing Claude manifest | Official capabilities and directories checked; client not run |

Discovery and automatic selection depend on the client's version, skill settings, permissions, and model. Directory and file checks do not establish behavior in clients that were not run. Check dates and official sources are in the [compatibility notes](docs/compatibility.md).

In earlier local checks, Codex had `0.3.0` installed and enabled. Version `0.2.0` had read the engineering entry point and change guidance in a new session. Claude Code had also discovered all three entry points through local `--plugin-dir` loading and read the common and debugging guidance. The DeepSeek-V4-flash model configured in that Claude session still performed unnecessary file searches during an example analysis; related debugging guidance was added afterward. These historical loading records do not replace a new-session loading check for `0.3.2` or establish that all task decisions are correct.

An earlier temporary-directory check used Node `v24.12.0`, `@deepseek-ai/cordis` `4.0.4`, and `dsh-skill` / `dsh-skill-filesystem` `0.2.0-rc.2`. The official provider discovered all three exported skills, loaded their bodies correctly, resolved resources from each skill's directory, and read the common and selected task-specific references. No DSH desktop, SDK session, or model request was run.

## Skills

| Area | Native plugin skill | Standalone skill | Guidance loaded as needed |
| --- | --- | --- | --- |
| [Research](skills/research/SKILL.md) | `research` | `practical-work-research` | Literature, study design, computational reproduction, data analysis, machine learning |
| [Engineering](skills/engineering/SKILL.md) | `engineering` | `practical-work-engineering` | Implementation and configuration, debugging, specified change review, releases and data migration |
| [Delivery](skills/delivery/SKILL.md) | `delivery` | `practical-work-delivery` | Documents, spreadsheets, presentations, cross-application operations |

Plugin hosts such as Codex and Claude add the `practical-work:` namespace to native names. Standalone skills use their full prefixed names; the client determines manual invocation syntax. `agents/openai.yaml` supplies Codex UI configuration. Other hosts can use standard `SKILL.md` files; they are not assumed to parse OpenAI UI configuration.

## Examples

Describe the task directly, or name the skill as it actually appears in your client:

```text
Use practical-work-research to interpret this paper's experimental results,
distinguishing the authors' claims from conclusions supported by the material.

Use practical-work-engineering to fix a refund calculation: discounted goods
cost 180 yuan, shipping of 12 yuan is non-refundable, and the expected refund is 180 yuan.

Use practical-work-delivery to turn the existing experimental results into a report,
following the supplied template without adding research conclusions.
```

For native Codex / Claude plugins, the engineering entry point is `practical-work:engineering`. For mixed tasks, add guidance according to the current action. For example, use research guidance to analyze a CSV, then add delivery guidance and spreadsheet capabilities when producing an Excel workbook. When a reproduction script fails, add engineering debugging guidance while retaining the existing research question, data, and results.

Ordinary conversation, title translation, and light wording edits do not start a scenario workflow. A mention of a paper, code, or a CSV file is not enough to choose an entry point.

## Loading

Names and descriptions identify entry points. Once selected, read only the references needed for the current task. When the task changes, add missing or changed material and reuse guidance that remains valid. Reuse information already present in the conversation or previously read files instead of reading unchanged material again.

- [Common guidance](references/common.md): limits unsupported wording, broad guarantees, unnecessary work, and unverified completion claims; retains production-data recovery requirements.
- [Application selection](references/applications.md): chooses literature, file, Drive, live Excel, browser, compute, and collaboration tools according to the object and actual capabilities.
- Each skill's task-specific references: add relevant judgment without forming a default workflow package.

When common guidance is already loaded in the session, reuse it; otherwise read the copy within the selected skill. Installing skills does not automatically load these requirements for ordinary conversation or rewrite `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, or other client instruction files. To apply personal writing preferences globally, put suitable instructions in a file your client supports; its rules determine when that file loads.

When a task explicitly requires an encoding, line ending, or exact stdout bytes, preserve that requirement in the implementation and check the actual output it applies to. A source-file or test-file comparison alone does not establish the stdout result.

This project has no MCP service, hooks, background processes, or built-in account connections. Research covers literature, computation, and data, excluding laboratory equipment operation and field collection. When a specialized tool is unavailable, state which operation remains incomplete. Installing the plugin does not supply every specialized capability.

If the host has already injected the full skill body, use it directly instead of invoking another loading tool. Resolve references from the skill directory or resource base provided by the host, rather than guessing paths from the current project directory. Menus, tool names, and invocation syntax depend on the host; use capabilities that are actually available.

## Updating

For a Codex installation from GitHub:

```sh
codex plugin marketplace upgrade practical-work --json
codex plugin add practical-work@practical-work --json
```

For Claude Code, run `claude plugin marketplace update practical-work-marketplace`, then `claude plugin update practical-work@practical-work-marketplace`. For Gemini CLI, run `gemini extensions update practical-work`. Use the plugin manager supplied by other clients.

For standalone skills, run `git pull --ff-only` in the source directory, then repeat the same export command. Start a new session after updating. Do not edit the plugin cache directly. Files you added to an export directory are preserved; edits to managed files are overwritten by their source versions during an update.

## Project structure

```text
practical-work/
├── README.md / README.en.md         # Chinese and English usage guides
├── plugin.json                      # Agent Plugins manifest
├── .codex-plugin/plugin.json         # Codex compatibility manifest
├── .claude-plugin/                   # Claude plugin and marketplace manifests
├── .cursor-plugin/marketplace.json   # Cursor marketplace manifest
├── .agents/plugins/marketplace.json  # Codex repository marketplace manifest
├── gemini-extension.json             # Gemini extension manifest
├── skills/{research,engineering,delivery}/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/                   # Area-specific and generated shared references
├── references/                      # Shared reference source files
├── scripts/portable_skills.py        # Synchronization and standalone skill export
├── scripts/package_skills.py         # Single-skill, enterprise, and Antigravity packages
├── tests/test_portable_skills.py
├── tests/test_package_skills.py
└── docs/compatibility.md
```

## Maintenance

The current version is `0.3.2`. This revision clarifies reuse of existing material and preservation of explicit encoding, line-ending, and stdout-byte requirements. It also adds this English README. The [0.3.2 change and check record](docs/release-0.3.2.md) describes this revision. The [historical 0.3.1 acceptance report](docs/acceptance-0.3.1.md) records earlier task reviews, which did not establish an overall improvement in model behavior; RSI remains incomplete. This wording revision alone does not demonstrate a behavioral improvement. The two earlier offline review batches covered 92 records: 91 met the original task requirements and one had no confirmed runtime result. A separate stdout-byte failure remains recorded. Across 14 comparable A/B pairs, task and wording judgments were tied. These results apply to the guidance before this revision; model evaluations were not rerun for 0.3.2.

Repository plugin and extension manifests use the same name and version. The dedicated Antigravity manifest omits a version field because its format does not declare one; package filenames record the version. Edit shared files only in the root `references/` directory. To make each skill independently installable, the script generates copies within the skills:

```sh
python scripts/portable_skills.py sync
python scripts/portable_skills.py sync --check
python -m unittest discover -s tests -v
```

Export checks cover self-contained skills, renamed skills, managed updates, protection of foreign files, and rejection of Windows directory junctions. Local symbolic-link creation was restricted by permissions during earlier tests, so the corresponding tests were skipped. This does not establish that tests have run on every platform.

New guidance should address an actual task, with detailed content placed in the relevant skill reference. Check what was read, which operations were selected, and what was delivered. Correct observed problems rather than using terminology matches as a measure of quality. Reference paths must stay within the skill directory; do not add personal paths, credentials, or fixed cache versions.

## References

- [Agent Skills specification](https://agentskills.io/specification): skill format and resources read as needed.
- [OpenAI plugin development documentation](https://developers.openai.com/plugins/build/plugins): plugin packaging.
- [Official client compatibility sources](docs/compatibility.md): installation, directories, and invocation.
- [OpenAI Plugins](https://github.com/openai/plugins), [Anthropic Skills](https://github.com/anthropics/skills), and [Superpowers](https://github.com/obra/superpowers): references for organizing project guidance.
- [Original references for common guidance](references/common.md#原始参考): engineering judgment and problem-solving methods.
