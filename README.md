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

### Skills CLI

```bash
npx skills add acchuang/zh-tw-humanizer --global
```

### Manual

The runtime artifact is `SKILL.md`. Install it wherever your harness expects skill directories:

```bash
git clone https://github.com/acchuang/zh-tw-humanizer.git
mkdir -p /path/to/your/skills/zh-tw-humanizer
cp zh-tw-humanizer/SKILL.md /path/to/your/skills/zh-tw-humanizer/
```

Or clone directly:

```bash
git clone https://github.com/acchuang/zh-tw-humanizer.git /path/to/your/skills/zh-tw-humanizer
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

## License

MIT
