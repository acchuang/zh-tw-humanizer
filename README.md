# zh-tw-humanizer：台式中文去 AI 味編輯

A portable agent skill that removes signs of AI-generated writing from Traditional Chinese text and localizes it to **Taiwanese Mandarin** — Taiwan vocabulary (影片/軟體/網路/資料, never 視頻/軟件/網絡/數據), Taiwanese tone, particles, and natural sentence rhythm. It never outputs simplified Chinese or mainland-style phrasing.

Plain Markdown, so it runs in any harness that supports skill-style instructions (Claude Code, OpenCode, pi, Cursor, etc.).

Based on [Wikipedia's "Signs of AI writing"](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) guide and the zh-TW [AI生成文的特徵](https://zh.wikipedia.org/zh-tw/Wikipedia:AI%E7%94%9F%E6%88%90%E6%96%87%E7%9A%84%E7%89%B9%E5%BE%B5) essay, extended with Taiwanese-Mandarin localization rules (兩岸用語差異、語助詞、台式語氣).

## What it covers

- **33 AI writing patterns in Chinese**: 假真誠開場白、心理諮商語氣、對仗句「不是 X 而是 Y」、概念名詞化「○○感/○○性」、空話動詞「提升/打造/賦能」、連接詞堆疊「此外/綜上所述/值得一提的是」、破折號濫用、金句堆疊、排比句、同義詞輪換、虛指權威、聊天機器人痕跡…
- **Taiwan-only localization layer**:
  - 48 組大陸用語 → 台灣用語對照表（視頻→影片、軟件→軟體、網絡→網路、數據→資料、地鐵→捷運、盒飯→便當…）
  - 簡繁轉換陷阱表（干/乾/幹、后/後、发/發/髮…）與台灣慣用字形（裡、台、線、為、著）
  - 台式語氣：委婉商量式、語助詞（喔/耶/啦/餒/蛤）、句式（還蠻/超/有在/這樣子/的話）、中英夾雜（cancel/confirm/case by case），各限於適合的文體
- **No-fabrication rule**: rewrites never add facts, names, dates, or citations that aren't in the source text.
- **False-positive guidance**: 什麼樣的人類文字不該被改（論文、單一破折號、句中「老實說」、港澳馬新中文…）
- **Voice calibration**: provide a sample of the author's own writing and the rewrite matches it instead of producing generic "clean" output.

## Installation

The repo root is itself a valid skill directory (`SKILL.md` at the top), so for every harness the install is: clone into that harness's skills folder.

### One-command (skills.sh CLI)

```bash
npx skills add acchuang/zh-tw-humanizer --global           # all configured harnesses
npx skills add acchuang/zh-tw-humanizer --global --agent claude-code   # one harness
npx skills update zh-tw-humanizer --global                 # update
```

### Claude Code

```bash
# personal skills (all projects)
git clone https://github.com/acchuang/zh-tw-humanizer.git ~/.claude/skills/zh-tw-humanizer
# or project-level: .claude/skills/zh-tw-humanizer/
```

### Pi

```bash
# global
git clone https://github.com/acchuang/zh-tw-humanizer.git ~/.agents/skills/zh-tw-humanizer
# or ~/.pi/agent/skills/zh-tw-humanizer/
# project-level: .pi/skills/ or .agents/skills/ (in the project dir)
```

Restart the session after installing. The skill then loads on-demand and registers as `/skill:zh-tw-humanizer`.

### OpenAI Codex CLI

Codex reads user skills from `~/.agents/skills/` (same location as Pi) and repo skills from `.agents/skills/` — so the Pi install above works for Codex too:

```bash
git clone https://github.com/acchuang/zh-tw-humanizer.git ~/.agents/skills/zh-tw-humanizer
```

Optional: pin or disable it in `~/.codex/config.toml`:

```toml
[[skills.config]]
path = "/Users/you/.agents/skills/zh-tw-humanizer/SKILL.md"
enabled = true
```

Restart Codex after changing the config.

### OpenCode

```bash
# global
mkdir -p ~/.config/opencode/skills
git clone https://github.com/acchuang/zh-tw-humanizer.git ~/.config/opencode/skills/zh-tw-humanizer
# project-level: .opencode/skills/zh-tw-humanizer/ (or .claude/skills/, .agents/skills/)
```

### Gemini CLI

```bash
git clone https://github.com/acchuang/zh-tw-humanizer.git ~/.gemini/skills/zh-tw-humanizer
# ~/.agents/skills/ also works as an alias
# project-level: .gemini/skills/ or .agents/skills/
```

### Other Agent Skills-compatible harnesses (Cursor, Windsurf, …)

```bash
git clone https://github.com/acchuang/zh-tw-humanizer.git /path/to/your/skills/zh-tw-humanizer
# or just copy SKILL.md into the harness's skills directory
```

## 安裝說明（繁體中文）

這個 repo 的根目錄本身就是一個合格的 skill 目錄（`SKILL.md` 在最上層），所以每個工具要裝的方式都一樣：把 repo clone 到該工具讀取 skill 的資料夾即可。

### 一行安裝（skills.sh CLI）

```bash
npx skills add acchuang/zh-tw-humanizer --global           # 安裝到所有有設定的工具
npx skills add acchuang/zh-tw-humanizer --global --agent claude-code   # 只裝到指定工具
npx skills update zh-tw-humanizer --global                 # 更新
```

### Claude Code

```bash
# 個人 skill（所有專案共用）
git clone https://github.com/acchuang/zh-tw-humanizer.git ~/.claude/skills/zh-tw-humanizer
# 或放在專案層級：.claude/skills/zh-tw-humanizer/
```

### Pi

```bash
# 全域
git clone https://github.com/acchuang/zh-tw-humanizer.git ~/.agents/skills/zh-tw-humanizer
# 或 ~/.pi/agent/skills/zh-tw-humanizer/
# 專案層級：.pi/skills/ 或 .agents/skills/（放在專案資料夾內）
```

安裝完重開 session 就會生效，之後可透過 `/skill:zh-tw-humanizer` 直接呼叫。

### OpenAI Codex CLI

Codex 的使用者 skill 放在 `~/.agents/skills/`（跟 Pi 同一個位置），專案 skill 放在 `.agents/skills/`——所以上面 Pi 的裝法 Codex 也適用：

```bash
git clone https://github.com/acchuang/zh-tw-humanizer.git ~/.agents/skills/zh-tw-humanizer
```

也可以選擇在 `~/.codex/config.toml` 裡指定或停用：

```toml
[[skills.config]]
path = "/Users/你/你的家目錄/.agents/skills/zh-tw-humanizer/SKILL.md"
enabled = true
```

改完設定後重開 Codex。

### OpenCode

```bash
# 全域
mkdir -p ~/.config/opencode/skills
git clone https://github.com/acchuang/zh-tw-humanizer.git ~/.config/opencode/skills/zh-tw-humanizer
# 專案層級：.opencode/skills/zh-tw-humanizer/（或 .claude/skills/、.agents/skills/）
```

### Gemini CLI

```bash
git clone https://github.com/acchuang/zh-tw-humanizer.git ~/.gemini/skills/zh-tw-humanizer
# ~/.agents/skills/ 也可以，Gemini 支援這個別名
# 專案層級：.gemini/skills/ 或 .agents/skills/
```

### 其他支援 Agent Skills 的工具（Cursor、Windsurf 等）

```bash
git clone https://github.com/acchuang/zh-tw-humanizer.git /path/to/你的/skills/zh-tw-humanizer
# 或直接把 SKILL.md 複製到該工具的 skills 資料夾
```

## Usage

Invoke however your agent harness exposes installed skills:

```
去 AI 味： [paste your text here]
```

```
請把這段改成台灣風格的中文： [paste your text here]
```

Point it at a file and it rewrites in place (prose only — code blocks, frontmatter, and link targets stay untouched):

```
Humanize the prose in docs/launch-post.md
```

### Voice calibration

Provide a sample of the author's writing and the skill matches sentence rhythm, word choices, and quirks instead of applying generic rules:

```
先看我的寫作樣本：
[paste 2-3 paragraphs of your own writing]

然後把這段改成我的風格：
[paste AI text to humanize]
```

## Research references

### AI-writing tells (Chinese)

- **維基百科：AI生成文的特徵** (zh-TW) — the Traditional-Chinese counterpart of "Signs of AI writing"; source of the Chinese-specific word lists (穩/接住/見證/至關重要…), 排比句濫用, 破折號濫用, 列表式行文, and numbered-header patterns. https://zh.wikipedia.org/zh-tw/Wikipedia:AI生成文的特徵
- **維基百科：Signs of AI writing** (en, WikiProject AI Cleanup) — the structural backbone: significance inflation, rule of three, copula avoidance, false ranges, and the cluster-based detection guidance. https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
- **數位時代「AI 味」系列（2025）** — Taiwanese editor's view: 對仗句上癮（不是 X，而是 Y）、金句堆疊與「氣味」測試（能不能拍成電影）、概念名詞化（○○感/○○性/○○化）. https://www.bnext.com.tw/article/89827/ai-writing-style-unique-features-avoiding-tips · https://www.bnext.com.tw/article/90761/how-to-fix-ai-writing-style
- **經理人月刊：維基百科不忍了！公布「抓包 AI 味指南」** — zh-TW summary of the Wikipedia guide (AI 詞彙黑名單、6 句型/語氣/格式). https://www.managertoday.com.tw/articles/view/71293

### Taiwanese Mandarin style

- **教育部《國語辭典簡編本》附錄：兩岸常用詞語對照表** — authoritative 大陸 vs 台灣 vocabulary pairs (basis of the 48-row localization table). https://dict.concised.moe.edu.tw/appendix.jsp?ID=54
- **中華語文知識庫：兩岸差異用詞**（中華文化總會） — cross-strait difference-word database. https://chinese-linguipedia.org/search_difference.html
- **vocus：如何分辨台灣腔？** — 台灣華語特色：輕聲、語助詞、台式詞彙（便當/飯店）、中英夾雜（cancel/confirm/case by case）. https://vocus.cc/article/65f14d07fd8978000132eed9
- **台味語助詞教學** — 蛤/蝦/餒/唷 等台式語助詞用法。 https://marstininuk.wordpress.com/2018/09/14/台味語助詞教學：輕鬆學會道地台灣腔/

### Cross-strait vocabulary (secondary)

- **漢語地區用詞差異列表**（維基百科） — 大陸/港澳/臺灣/馬新 four-region comparison. https://zh.wikipedia.org/zh-tw/漢語地區用詞差異列表
- **兩岸三地用詞差異：軟件/軟體、激光/雷射** — tech-domain mapping (服務器/伺服器, 內存/記憶體…). https://www.toolbox365.cn/tutorials/zh-vocabulary-mainland-taiwan-hk/

## License

MIT
