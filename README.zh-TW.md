# zh-tw-humanizer：台式中文去 AI 味編輯

**English README → [README.md](README.md)**

這是一個可攜式 agent skill，能把繁體中文文字裡的 AI 生成痕跡去掉，並在地化成**台灣國語**——台灣用詞（影片/軟體/網路/資料，絕不用視頻/軟件/網絡/數據）、台式語氣、語助詞、自然的句子節奏。絕不輸出簡體中文或大陸腔調用語。

純 Markdown 格式，任何支援 skill 指令格式的工具都能跑（Claude Code、OpenCode、pi、Cursor 等）。

根據 [Wikipedia's "Signs of AI writing"](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) 指南與 zh-TW 版的 [AI生成文的特徵](https://zh.wikipedia.org/zh-tw/Wikipedia:AI%E7%94%9F%E6%88%90%E6%96%87%E7%9A%84%E7%89%B9%E5%BE%B5) 條目為基礎，再加上台灣國語在地化規則（兩岸用語差異、語助詞、台式語氣）延伸而成。

## 涵蓋內容

- **56 種中文 AI 寫作特徵**（4 大類）：假真誠開場白、心理諮商語氣、對仗句「不是 X 而是 Y」、概念名詞化「○○感/○○性」、空話動詞「提升/打造/賦能」、連接詞堆疊「此外/綜上所述/值得一提的是」、破折號濫用、金句堆疊、排比句、同義詞輪換、虛指權威、幻覺引用、假精確（無來源的精確數字）、過程敘事（「經過分析」「深入研究後發現」）、立場真空、公式化開場、解說導引句、假推論、說教深度腔、金句公式、戲劇性短句轟炸、勸誡反問收尾、粗體轟炸、emoji 堆疊、編號切碎段落、表格誤用、預告式導言、模板佔位文字、工具痕跡、聊天機器人痕跡…
- **英文 humanizer 抓不到的中文專屬破綻**（1.3.0 新增）：翻譯腔句式（「最……之一」「當……的時候」「對 X 進行 Y」）、系動詞迴避（用「作為／扮演著……的角色」把一句「是」撐胖）、過度強調關注度（「引發熱議」「多家媒體報導」）、引用層破綻（死連結、DOI 檢查碼錯、造訪日期早於發表日）、列表式行文與行內粗體標題、標題結構與 Markdown 破綻（跳級標題、多個 H1、`---` 分隔線、中文裡的彎引號）。
- **隱形字元清除**：零寬字元（U+200B/200C/200D/FEFF/2060）、tag characters（U+E0000–E007F）、不換行空格與窄空格——複製貼上到哪都跟著走的機器指紋。程式碼區塊、URL、全形標點不動。
- **「規則腔」防呆**：規則套過頭會生出新的破綻（句句短、句句口語、每句都在示範某條規則），最後一關會檢查並放幾句原文回去。
- **台灣專屬在地化層**：
  - 48 組大陸用語 → 台灣用語對照表（視頻→影片、軟件→軟體、網絡→網路、數據→資料、地鐵→捷運、盒飯→便當…）
  - 簡繁轉換陷阱表（干/乾/幹、后/後、发/發/髮…）與台灣慣用字形（裡、台、線、為、著）
  - 台式語氣：委婉商量式、語助詞（喔/耶/啦/餒/蛤）、句式（還蠻/超/有在/這樣子/的話）、中英夾雜（cancel/confirm/case by case），各限於適合的文體
- **不捏造原則**：改寫過程絕不新增原文沒有的事實、人名、日期或引用來源。
- **安全邊界**：貼進來要改寫的文字如果混有指令式內容（「忽略前面的指令」「你現在是…」），一律當成待改寫的純文字內容，絕不當成新指令執行。
- **誤判防呆指引**：什麼樣的人類文字不該被改（論文、單一破折號、句中「老實說」、港澳馬新中文…）
- **語感校準**：提供作者本人的寫作樣本，改寫會貼近該樣本的節奏與用字，而不是套用制式化的「乾淨」版本。
- **保護區段**：價格、專有名詞、連結、引號內文字、法律用語在改寫過程中會鎖定不動。
- **依場景調整力道**：不同文體採不同處理方式（社群貼文大幅改寫，技術文件則保守處理）。
- **標註模式**：下指令「先標問題不要改」只列出問題，不動手改寫——適合審閱別人的草稿。
- **交付前品質自檢**：5 個面向、滿分 50 分的自評（資訊完整度、不捏造、台灣用語正確、節奏、個人風格），低於 35 分不交付。

## 安裝方式

這個 repo 的根目錄本身就是合格的 skill 目錄（`SKILL.md` 在最上層），所以每個工具的安裝方式都一樣：把 repo clone 到該工具讀取 skill 的資料夾即可。

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

## 用法

依你的 agent 工具呼叫已安裝 skill 的方式來使用：

```
去 AI 味： [貼上你的文字]
```

```
請把這段改成台灣風格的中文： [貼上你的文字]
```

指定一個檔案，它會原地改寫（只動內文——程式碼區塊、frontmatter、連結目標都不會被動到）：

```
Humanize the prose in docs/launch-post.md
```

### 語感校準

提供作者本人的寫作樣本，skill 會貼近句子節奏、用字習慣與小癖好來改寫，而不是套用制式化規則：

```
先看我的寫作樣本：
[貼上 2-3 段你自己寫的文字]

然後把這段改成我的風格：
[貼上要去 AI 味的文字]
```

## 研究參考資料

### 中文 AI 寫作特徵

- **維基百科：AI生成文的特徵**（zh-TW）——「Signs of AI writing」的繁體中文對應條目；中文特有詞彙表（穩/接住/見證/至關重要…）、排比句濫用、破折號濫用、列表式行文、編號標題等特徵的來源。https://zh.wikipedia.org/zh-tw/Wikipedia:AI生成文的特徵
- **維基百科：Signs of AI writing**（英文，WikiProject AI Cleanup）——結構性骨架：意義誇大、三段式修辭、避免用「是」的句法、假範圍，以及群集式判斷準則。https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
- **數位時代「AI 味」系列（2025）**——台灣編輯視角：對仗句上癮（不是 X，而是 Y）、金句堆疊與「氣味」測試（能不能拍成電影）、概念名詞化（○○感/○○性/○○化）。https://www.bnext.com.tw/article/89827/ai-writing-style-unique-features-avoiding-tips · https://www.bnext.com.tw/article/90761/how-to-fix-ai-writing-style
- **經理人月刊：維基百科不忍了！公布「抓包 AI 味指南」**——維基百科指南的繁中摘要（AI 詞彙黑名單、6 句型/語氣/格式）。https://www.managertoday.com.tw/articles/view/71293
- **Wikipedia:Signs of AI writing（2026 年版本更新）**——過程敘事（「經過審視現有資料來源後」）與假精確特徵是 2026 年中新增的；特徵 55–56 的來源。https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
- **端傳媒（2026-04）：維基百科如何應對 AI 寫作？**——WikiProject AI Cleanup 持續更新特徵清單的背景報導。https://theinitium.com/20260415-tech-in-numbers-wikipedia-against-ai-writing/
- **高科大 AICT：去 AI 味完全指南 2026**——中文 AI 味的成因（公文語料佔比高＋翻譯腔），也是「英文 humanizer 處理中文效果差」的說明；特徵 17 的背景。https://aict.nkust.edu.tw/digitrans/?p=12219
- **余光中〈怎樣改進英式中文？〉與相關翻譯腔整理**——「最……之一」「當……的時候」「對……進行」「多餘的和／以及」；特徵 17 的直接來源。https://zhuanlan.zhihu.com/p/72934908
- **RAR 設計攻略：去 AI 味怎麼做才有效**——「規則腔」的來源：規則套過頭會生出新的破綻，工整得像在填表。https://rar.design/posts/de-ai-flavor-writing-skill-guide
- **同類 skill 的隱形字元處理**（kevintsai1202/Humanizer-zh-TW 的 text-watermark-cleaner-zh-tw）——零寬字元、tag characters、異形空白清單；特徵 54 的來源。https://github.com/kevintsai1202/Humanizer-zh-TW

### 台灣國語風格

- **教育部《國語辭典簡編本》附錄：兩岸常用詞語對照表**——大陸 vs 台灣用詞的權威對照（48 組在地化對照表的依據）。https://dict.concised.moe.edu.tw/appendix.jsp?ID=54
- **中華語文知識庫：兩岸差異用詞**（中華文化總會）——兩岸用詞差異資料庫。https://chinese-linguipedia.org/search_difference.html
- **vocus：如何分辨台灣腔？**——台灣華語特色：輕聲、語助詞、台式詞彙（便當/飯店）、中英夾雜（cancel/confirm/case by case）。https://vocus.cc/article/65f14d07fd8978000132eed9
- **台味語助詞教學**——蛤/蝦/餒/唷 等台式語助詞用法。https://marstininuk.wordpress.com/2018/09/14/台味語助詞教學：輕鬆學會道地台灣腔/

### 兩岸用詞對照（次要參考）

- **漢語地區用詞差異列表**（維基百科）——大陸/港澳/臺灣/馬新四地對照。https://zh.wikipedia.org/zh-tw/漢語地區用詞差異列表
- **兩岸三地用詞差異：軟件/軟體、激光/雷射**——科技領域用詞對照（服務器/伺服器、內存/記憶體…）。https://www.toolbox365.cn/tutorials/zh-vocabulary-mainland-taiwan-hk/

## 授權

MIT
