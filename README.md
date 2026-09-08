# zh-tw-humanizer

**繁體中文版 README → [README.zh-TW.md](README.zh-TW.md)**

A portable agent skill that removes signs of AI-generated writing from Traditional Chinese text and localizes it to **Taiwanese Mandarin** — Taiwan vocabulary (影片/軟體/網路/資料, never 視頻/軟件/網絡/數據), Taiwanese tone, particles, and natural sentence rhythm. It never outputs simplified Chinese or mainland-style phrasing.

Plain Markdown, so it runs in any harness that supports skill-style instructions (Claude Code, OpenCode, pi, Cursor, etc.).

Based on [Wikipedia's "Signs of AI writing"](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) guide and the zh-TW [AI生成文的特徵](https://zh.wikipedia.org/zh-tw/Wikipedia:AI%E7%94%9F%E6%88%90%E6%96%87%E7%9A%84%E7%89%B9%E5%BE%B5) essay, extended with Taiwanese-Mandarin localization rules (兩岸用語差異、語助詞、台式語氣).

## What it covers

- **56 AI writing patterns in Chinese** (4 categories): 假真誠開場白、心理諮商語氣、對仗句「不是 X 而是 Y」、概念名詞化「○○感/○○性」、空話動詞「提升/打造/賦能」、連接詞堆疊「此外/綜上所述/值得一提的是」、破折號濫用、金句堆疊、排比句、同義詞輪換、虛指權威、幻覺引用、假精確（無來源的精確數字）、過程敘事（「經過分析」「深入研究後發現」）、立場真空、公式化開場、解說導引句、假推論、說教深度腔、金句公式、戲劇性短句轟炸、勸誡反問收尾、粗體轟炸、emoji 堆疊、編號切碎段落、表格誤用、預告式導言、模板佔位文字、工具痕跡、聊天機器人痕跡…
- **Chinese-specific tells English humanizers miss** (new in 1.3.0): 翻譯腔句式（「最……之一」「當……的時候」「對 X 進行 Y」）、系動詞迴避（「作為/扮演著……的角色」撐胖一句「是」）、過度強調關注度（「引發熱議」「多家媒體報導」）、引用層破綻（死連結、DOI 檢查碼錯、access-date 早於發表日）、列表式行文與行內粗體標題、標題結構與 Markdown 破綻（跳級標題、多個 H1、`---` 分隔線、中文裡的彎引號）。
- **Invisible-character cleanup**: zero-width chars (U+200B/200C/200D/FEFF/2060), tag characters (U+E0000–E007F), NBSP and narrow spaces — the provenance markers that survive every copy-paste. Code blocks, URLs, and full-width punctuation stay untouched.
- **"Rule-flavor" guard**: over-applying the rules produces its own tell (every sentence short, colloquial, and demonstrating a rule). The final pass checks for it and puts some original sentences back.
- **Taiwan-only localization layer**:
  - 48 組大陸用語 → 台灣用語對照表（視頻→影片、軟件→軟體、網絡→網路、數據→資料、地鐵→捷運、盒飯→便當…）
  - 簡繁轉換陷阱表（干/乾/幹、后/後、发/發/髮…）與台灣慣用字形（裡、台、線、為、著）
  - 台式語氣：委婉商量式、語助詞（喔/耶/啦/餒/蛤）、句式（還蠻/超/有在/這樣子/的話）、中英夾雜（cancel/confirm/case by case），各限於適合的文體
- **No-fabrication rule**: rewrites never add facts, names, dates, or citations that aren't in the source text.
- **Safety boundary**: instruction-like text pasted into the input for rewriting ("ignore previous instructions", "you are now...") is treated as literal content to rewrite, never executed as a new command.
- **False-positive guidance**: 什麼樣的人類文字不該被改（論文、單一破折號、句中「老實說」、港澳馬新中文…）
- **Voice calibration**: provide a sample of the author's own writing and the rewrite matches it instead of producing generic "clean" output.
- **Protected spans**: prices, proper nouns, links, quotes, and legal terms are locked and never touched during rewriting.
- **Scene-based intensity**: different genres get different treatment (social posts rewritten heavily, technical docs kept conservative).
- **Annotation mode**: "先標問題不要改" lists problems without rewriting — for reviewing others' drafts.
- **Pre-delivery quality self-check**: a 5-dimension 50-point score (information, no-fabrication, Taiwan-correct, rhythm, personality); below 35 it isn't delivered.

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
- **Wikipedia:Signs of AI writing (2026 revisions)** — process-narration ("after reviewing the available sources") and false-precision signs added mid-2026; source of patterns 55–56. https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
- **端傳媒（2026-04）：維基百科如何應對 AI 寫作？** — background on WikiProject AI Cleanup's ongoing pattern updates. https://theinitium.com/20260415-tech-in-numbers-wikipedia-against-ai-writing/
- **高科大 AICT：去 AI 味完全指南 2026** — why Chinese AI-flavor differs from English (heavy officialese in the training corpus + translationese), and why English humanizers underperform on Chinese; background for pattern 17. https://aict.nkust.edu.tw/digitrans/?p=12219
- **余光中〈怎樣改進英式中文？〉and translationese roundups** — 「最……之一」、「當……的時候」、「對……進行」、redundant 和／以及; direct source of pattern 17. https://zhuanlan.zhihu.com/p/72934908
- **RAR 設計攻略：去 AI 味怎麼做才有效** — source of the "rule-flavor" guard: over-applied rules create a new tell of their own. https://rar.design/posts/de-ai-flavor-writing-skill-guide
- **text-watermark-cleaner-zh-tw** (in kevintsai1202/Humanizer-zh-TW) — the zero-width / tag-character / anomalous-whitespace list behind pattern 54. https://github.com/kevintsai1202/Humanizer-zh-TW

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
