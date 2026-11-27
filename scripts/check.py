#!/usr/bin/env python3
"""機械可驗的破綻檢查。給 SKILL.md 流程第 6 步用，取代人工打分。

用法：
    python3 scripts/check.py 最終稿.md
    cat 最終稿.md | python3 scripts/check.py
    python3 scripts/check.py --source 原稿.md 最終稿.md   # 另外比對事實有沒有掉、有沒有憑空多
    python3 scripts/check.py --patterns 稿.md            # 另外列出 SKILL.md 各模式「注意詞」的命中（只提示，不影響結果）
    python3 scripts/check.py --self-test

只檢查「查得準」的規則：破折號、大陸用語、簡體字與高把握簡轉繁錯字、隱形字元、
彎引號、工具痕跡、emoji 密度、佔位文字。語氣、節奏、人味這種要判斷的，機器不管。
--source 模式再加一道事實比對：原稿的數字、日期、版本、網址、信箱、代碼、
「」引文、程式碼，改寫後要原樣在；改寫後出現原稿沒有的數字、網址、信箱、代碼，
就是捏造。中文數字（三成）換成阿拉伯數字（30%）會被當成新增，這是已知的誤報。
Markdown 骨架（程式碼區塊、連結、標題、表格列）的數量變動改為提示（不影響 exit code），
避免模式 45／46 拆表或整標題時誤報失敗。
大陸用語表直接從 SKILL.md 模式 34 讀，不在這裡重抄一份。
"""

import argparse
import re
import statistics
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

SKILL = Path(__file__).resolve().parent.parent / "SKILL.md"

INVISIBLE = {
    "\u200b": "零寬空格",
    "\u200c": "零寬不連字",
    "\u200d": "零寬連字",
    "\ufeff": "BOM／零寬不斷空格",
    "\u2060": "word joiner",
    "\u00a0": "不換行空格（換成一般空格）",
    "\u2009": "窄空格",
    "\u202f": "窄不換行空格",
}

TOOL_TRACES = [
    (r"utm_source=(chatgpt\.com|openai|perplexity)", "AI 工具的 utm 參數"),
    (r"referrer=grok\.com", "Grok referrer"),
    (r"turn\d+(search|view)\d+", "ChatGPT 檢索標記"),
    (r"oai_?cite|contentReference", "ChatGPT 引用標記"),
    (r"\[cite: ?\d+\]|\[span_\d+\]\(start_span\)", "Gemini 引用標記"),
    (r"grok_card|grok_render_citation_card_json", "Grok 卡片標記"),
    (r"attached_file|ppl-ai-file-upload", "Perplexity 上傳標記"),
    (r":::writing", "未清乾淨的區塊標記"),
    (r"\[object Object\]", "序列化失敗的殘骸"),
]

PLACEHOLDERS = [
    (r"Lorem ipsum", "模板佔位文字"),
    (r"【[^】]*(填寫|填入|插入|公司名稱|日期)[^】]*】", "模板佔位文字"),
    (r"\b(TBD|TODO)\b", "未補的佔位文字"),
    (r"(待補充|待確認|XXX)", "未補的佔位文字"),
]

# 僅收錄台灣繁體中文正常行文不會出現的簡化字；刻意排除繁簡共用或字義不同者（系、面、干、后、里、只、划、别、准、云、制、冲等）。
SIMPLIFIED_CHARS = (
    "这们说为与发会时来对开关过进还学经经济国际实现电脑网络数软质体点机业产动长问题"
    "从应该结构设计资讯视频线给让种样号码标处简单复杂确认选择练习转换显编辑译读写听"
    "见观觉爱乐车东门间风飞马鸟鱼龙华语词义区专传统环错误报导称赞举办签约购买卖钱银账"
    "联帮满达图书馆历纪录医疗卫个"
)
SIMPLIFIED_RE = re.compile("[" + "".join(sorted(set(SIMPLIFIED_CHARS))) + "]")

# 高把握簡轉繁錯字（排除會跨詞誤判的組合，或加前後文邊界）
S2T_TYPO_RULES = [
    (re.compile(re.escape(bad)), bad, good)
    for bad, good in (
        ("幹淨", "乾淨"),
        ("干淨", "乾淨"),
        ("復雜", "複雜"),
        ("以后", "以後"),
        ("然后", "然後"),
        ("最后", "最後"),
        ("背后", "背後"),
        ("身后", "身後"),
        ("售后", "售後"),
        ("泡面", "泡麵"),
        ("拌面", "拌麵"),
        ("陽春面", "陽春麵"),
        ("牛肉面", "牛肉麵"),
        ("義大利面", "義大利麵"),
        ("規划", "規劃"),
        ("計划", "計畫"),
        ("標准", "標準"),
        ("標志", "標誌"),
        ("雜志", "雜誌"),
        ("沖刺", "衝刺"),
        ("沖突", "衝突"),
        ("沖擊", "衝擊"),
        ("別扭", "彆扭"),
        ("人雲亦雲", "人云亦云"),
        ("這里", "這裡"),
        ("那里", "那裡"),
        ("哪里", "哪裡"),
        ("心里", "心裡"),
        ("家里", "家裡"),
        ("洗頭發", "洗頭髮"),
        ("剪頭發", "剪頭髮"),
        ("吹頭發", "吹頭髮"),
        ("白發蒼蒼", "白髮蒼蒼"),
        ("滿頭白發", "滿頭白髮"),
    )
] + [
    (re.compile(r"(?<![開源鏡街念心底])頭發(?![現生展動表送射出起言])"), "頭發", "頭髮"),
    (re.compile(r"(?<!皇)后來"), "后來", "後來"),
    (re.compile(r"(?<![書表正背反側全單多])面條(?![款件文理])"), "面條", "麵條"),
]

EMOJI = re.compile(
    "[\U0001f300-\U0001faff\U00002600-\U000027bf\U0001f1e6-\U0001f1ff⬀-⯿]"
)
CJK = r"㐀-鿿豈-﫿"
SAFE_URL_RE = re.compile(r"https?://[A-Za-z0-9\-._~:/?#\[@!$&'(*+,;=%]+")


def _vocab_rows(skill_path):
    """模式 34 表格的 [(左欄, 右欄)]，不含表頭與分隔列。"""
    if not skill_path.exists():
        return []
    body = skill_path.read_text(encoding="utf-8")
    section = re.search(r"^### 34\..*?$(.*?)^### 35\.", body, re.S | re.M)
    if not section:
        return []
    return [
        (l, r)
        for l, r in re.findall(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$", section.group(1), re.M)
        if l not in ("大陸用語", "---", ":---") and not set(l) <= {"-", ":"}
    ]


def load_vocab(skill_path=SKILL):
    """從 SKILL.md 模式 34 的表格讀大陸用語對照。找不到就回空表。"""
    pairs = []
    for left, right in _vocab_rows(skill_path):
        # 「程序（軟體語境）」這種標了語境的詞，機器分不出語境，交給人和 SKILL.md 判斷
        if "（" in left:
            continue
        for variant in [t for t in re.split(r"[／/]", left) if t]:
            pairs.append((variant, right))
    return pairs


def load_context_terms(skill_path=SKILL):
    """被 load_vocab 略過的標語境詞（程序、代碼……），只取詞本身。"""
    return [re.split(r"[（(]", left)[0] for left, _ in _vocab_rows(skill_path) if "（" in left]


def load_exempt(skill_path=SKILL):
    """模式 34「台灣也用」清單：命中這些詞的片段不算大陸用語。"""
    if not skill_path.exists():
        return []
    m = re.search(
        r"^\*\*台灣也用（不要改）\*\*：(.+)$",
        skill_path.read_text(encoding="utf-8"),
        re.M,
    )
    return [w.strip() for w in m.group(1).split("、") if w.strip()] if m else []


def load_watchwords(skill_path=SKILL):
    """從 SKILL.md 各模式的「**注意詞**」行讀詞。回傳 [(模式編號, 詞)]。
    兩字以下（作為、豐富）、含句型佔位（……／英文代碼）或說明片段不收；模式 36 為正面詞，跳過。"""
    if not skill_path.exists():
        return []
    body = skill_path.read_text(encoding="utf-8")
    out = []
    seen = set()
    for num_str, block in re.findall(r"^### (\d+)\.(.*?)(?=^### |\Z)", body, re.S | re.M):
        num = int(num_str)
        if num == 36:
            continue
        m = re.search(r"^\*\*注意詞\*\*：(.+)$", block, re.M)
        if not m:
            continue
        cleaned = re.sub(r"（[^）]*）|\([^)]*\)", "", m.group(1).rstrip("。"))
        for w in re.split(r"[、，,；;／/]", cleaned):
            w = w.strip()
            if len(w) < 3 or len(w) > 10:
                continue
            if any(ch in w for ch in "……。：？！「」%"):
                continue
            if re.search(r"[A-Za-z]", w):
                continue
            key = (num, w)
            if key not in seen:
                seen.add(key)
                out.append(key)
    return out


ADVISORY_PATTERNS = [
    (6, re.compile(r"(?:不是|不只是|不僅僅是)[^。！？\n]{1,20}[，,、]\s*(?:而是|更是|比較像)")),
    (9, re.compile(r"賦能|深耕|助力|締造|煥新")),
    (24, re.compile(r"(?:不是嗎|難道不是嗎|你還在等什麼)[？?]")),
    (44, re.compile(r"首先[，,][\s\S]{1,160}其次[，,]")),
    (60, re.compile(r"從[^。！？\n]{2,15}到[^。！？\n]{2,15}不等")),
]


def scan_patterns(text, words=None):
    """注意詞命中，回傳 [(行, 欄, 模式編號, 詞)]。命中不代表有問題，只是該看一眼。"""
    words = load_watchwords() if words is None else words
    prose = strip_protected(text)
    hits = set()

    def add_hit(offset, num, label):
        line = prose.count("\n", 0, offset) + 1
        col = offset - (prose.rfind("\n", 0, offset) + 1) + 1
        hits.add((line, col, num, label))

    for num, w in words:
        for m in re.finditer(re.escape(w), prose):
            add_hit(m.start(), num, w)
    for num, rx in ADVISORY_PATTERNS:
        for m in rx.finditer(prose):
            label = m.group(0).replace("\n", " ")
            if len(label) > 24:
                label = label[:24] + "…"
            add_hit(m.start(), num, label)
    return sorted(hits)


def _clen(s):
    return len(re.sub(r"[\s\W_]", "", s))


def rhythm(text):
    """節奏提示，回傳 [(行, 說明)]。只看散文段落，標題、表格、條列不算。
    門檻是經驗值（短句 ≤6 字、變異係數 0.25／0.15），誤報多再調。"""
    prose = strip_protected(text)
    paras, start, buf = [], 1, []
    for i, line in enumerate(prose.split("\n") + [""], 1):
        if line.strip() and not re.match(r"\s*(#|\||[-*+] |\d+[.)] |>)", line):
            if not buf:
                start = i
            buf.append(line.strip())
        elif buf:
            paras.append((start, "".join(buf)))
            buf = []
    out, sents = [], []
    for start, p in paras:
        ss = [s for s in re.split(r"(?<=[。！？!?])", p) if _clen(s)]
        sents += ss
        run = 0
        for s in ss:
            run = run + 1 if _clen(s) <= 6 else 0
            if run == 3:
                out.append((start, "連續三句以上的短句（模式 23）"))
                break
    cv = lambda xs: statistics.pstdev(xs) / statistics.mean(xs)
    if len(sents) >= 8 and cv([_clen(s) for s in sents]) < 0.25:
        out.append((1, "句子長度太平均，長短沒有變化"))
    if len(paras) >= 4 and cv([_clen(p) for _, p in paras]) < 0.15:
        out.append((1, "段落長度太平均"))
    return out


def strip_protected(text):
    """把 YAML frontmatter、程式碼區塊、行內程式碼、Markdown 表格分隔線、URL 換成等長空白，位置不變，內容不掃。"""
    def blank(m):
        return re.sub(r"[^\n]", " ", m.group(0))

    text = re.sub(r"\A---\r?\n.*?\r?\n---(?=\r?\n|\Z)", blank, text, flags=re.S)
    text = re.sub(r"^```.*?^```", blank, text, flags=re.S | re.M)
    text = re.sub(r"`[^`\n]+`", blank, text)
    text = re.sub(r"^[ \t]*(?=.*\|)(?=.*-)[ \t:|\-]+$", blank, text, flags=re.M)
    text = SAFE_URL_RE.sub(blank, text)
    return text


def scan(text, vocab=None):
    """回傳 [(行, 欄, 規則, 說明)]。行欄都是 1-based。"""
    vocab = load_vocab() if vocab is None else vocab
    prose = strip_protected(text)
    hits = []

    def add(offset, rule, note, src=text):
        line = src.count("\n", 0, offset) + 1
        col = offset - (src.rfind("\n", 0, offset) + 1) + 1
        hits.append((line, col, rule, note))

    # 隱形字元：程式碼區塊裡一樣看不見，所以掃全文
    for m in re.finditer("[" + "".join(INVISIBLE) + "]", text):
        ch = m.group(0)
        add(m.start(), "隱形字元", f"U+{ord(ch):04X} {INVISIBLE[ch]}")
    for m in re.finditer("[\U000e0000-\U000e007f]", text):
        add(m.start(), "隱形字元", f"U+{ord(m.group(0)):05X} tag character")

    for m in re.finditer(r"——|—|(?<!-)--(?!-)", prose):
        add(m.start(), "破折號", f"模式 27：{m.group(0)!r} 是硬規則，改標點或重組句子")

    for m in re.finditer(r"[“”‘’]", prose):
        add(m.start(), "彎引號", f"模式 46：{m.group(0)} 換成「」『』")

    for m in re.finditer(f'["\'](?=[{CJK}])|(?<=[{CJK}])["\']', prose):
        add(m.start(), "直引號", "模式 46：中文裡的英文引號，換成「」")

    for m in re.finditer(f"(?<=[{CJK}])[,!?;:]", prose):
        add(m.start(), "半形標點", f"模式 40：中文裡出現半形標點「{m.group(0)}」，換成全形")

    for m in SIMPLIFIED_RE.finditer(prose):
        add(m.start(), "簡體字", f"模式 35：出現簡體字「{m.group(0)}」")

    for rx, bad, good in S2T_TYPO_RULES:
        for m in rx.finditer(prose):
            add(m.start(), "簡轉繁錯字", f"模式 35：{bad} → {good}")

    exempt = [
        m.span()
        for w in load_exempt()
        for m in re.finditer(re.escape(w), prose)
    ]
    found = [
        (m.start(), m.end(), term, fix)
        for term, fix in vocab
        for m in re.finditer(re.escape(term), prose)
    ]
    # 重疊的命中只留最左邊、最長的：視頻通話 吃掉裡面的 視頻，本周末 只報 本周
    reported_to = 0
    for s, e, term, fix in sorted(found, key=lambda h: (h[0], h[0] - h[1])):
        if s < reported_to or any(a <= s and e <= b for a, b in exempt):
            continue
        reported_to = e
        add(s, "大陸用語", f"模式 34：{term} → {fix}")

    for pattern, note in TOOL_TRACES:
        for m in re.finditer(pattern, text):
            add(m.start(), "工具痕跡", f"模式 54：{note}")

    for pattern, note in PLACEHOLDERS:
        for m in re.finditer(pattern, prose):
            add(m.start(), "佔位文字", f"模式 53：{note}")

    for i, line in enumerate(prose.split("\n"), 1):
        n = len(EMOJI.findall(line))
        if n >= 3:
            hits.append((i, 1, "emoji 堆疊", f"模式 43：這行 {n} 個 emoji"))

    return sorted(hits)


URL_RE = SAFE_URL_RE
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
DATE_RE = re.compile(r"\d{4}\s*年\s*\d{1,2}\s*月(?:\s*\d{1,2}\s*日)?|\d{1,2}\s*月\s*\d{1,2}\s*日")
VERSION_RE = re.compile(r"\bv?\d+(?:\.\d+){2,}\b")
NUMBER_RE = re.compile(r"\d[\d,]*(?:\.\d+)?")
CODE_RE = re.compile(r"\b(?=[A-Z0-9]*[A-Z])(?=[A-Z0-9]*\d)[A-Z][A-Z0-9]{3,}\b")
QUOTE_RE = re.compile(r"「[^」]+」|『[^』]+』")
FENCE_RE = re.compile(r"^```.*?^```|`[^`\n]+`", re.S | re.M)


def _normalize_url(u):
    u = u.rstrip(".,;:!?")
    parts = urlsplit(u)
    if not parts.query:
        return u
    pairs = parse_qsl(parts.query, keep_blank_values=True)
    kept = [
        (k, v)
        for k, v in pairs
        if not (
            (k == "utm_source" and v in ("chatgpt.com", "openai", "perplexity"))
            or (k == "referrer" and v == "grok.com")
        )
    ]
    if len(kept) == len(pairs):
        return u
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(kept, doseq=True), parts.fragment))


def facts(text):
    """抽出改寫不該動、也不該憑空多出來的事實。回傳 {類別: set}。"""
    out = {k: set() for k in ("引文", "程式碼", "網址", "信箱", "日期", "版本", "代碼", "數字")}
    out["引文"] = {re.sub(r"\s+", "", q) for q in QUOTE_RE.findall(text)}
    out["程式碼"] = {c.strip("`\n ") for c in FENCE_RE.findall(text)}

    # 抽過的就換成空白，避免同一段被後面的規則重複算
    def take(rx, key, norm=lambda x: x):
        nonlocal text
        for m in rx.finditer(text):
            out[key].add(norm(m.group(0)))
        text = rx.sub(lambda m: " " * len(m.group(0)), text)

    text = FENCE_RE.sub(lambda m: " " * len(m.group(0)), text)
    take(URL_RE, "網址", _normalize_url)
    take(EMAIL_RE, "信箱", str.lower)
    take(DATE_RE, "日期", lambda d: re.sub(r"\s+", "", d))
    take(VERSION_RE, "版本", lambda v: v.lstrip("v"))
    take(CODE_RE, "代碼")
    # 條列編號和標題記號不是事實
    text = re.sub(r"^\s*(?:\d+[.)、]|#+)\s", "", text, flags=re.M)
    take(NUMBER_RE, "數字", lambda n: n.replace(",", ""))
    return out


FENCE_BLOCK_RE = re.compile(r"^```.*?^```", re.S | re.M)
LINK_RE = re.compile(r"\[[^\]\n]+\]\([^)\s]+\)")
HEADING_RE = re.compile(r"^#{1,6}\s", re.M)
TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$", re.M)


def structure(text):
    """Markdown 骨架的數量：程式碼區塊、連結、標題、表格列。"""
    blocks = FENCE_BLOCK_RE.findall(text)
    prose = FENCE_BLOCK_RE.sub("", text)
    return {
        "程式碼區塊": len(blocks),
        "連結": len(LINK_RE.findall(prose)),
        "標題": len(HEADING_RE.findall(prose)),
        "表格列": len(TABLE_ROW_RE.findall(prose)),
    }


def compare_structure(source, draft):
    """回傳 [(規則, 說明)]：Markdown 骨架的提示性變動（不影響 exit code）。"""
    hits = []
    s_struct, n_struct = structure(source), structure(draft)
    for kind, before in s_struct.items():
        if before != n_struct[kind]:
            hits.append(("結構變動", f"{kind}原稿 {before} 個，改寫後 {n_struct[kind]} 個"))
    return hits


def compare(source, draft):
    """回傳 [(規則, 說明)]：原稿的事實掉了、或改寫憑空多了。"""
    src, new = facts(source), facts(draft)
    hits = []
    for kind, items in src.items():
        for item in sorted(items - new[kind]):
            hits.append(("遺失事實", f"{kind}{item}原稿有，改寫後不見了"))
    # 引文與程式碼是原樣保留的對象，改寫後多出來的不算捏造；其餘多出來的算
    for kind in ("網址", "信箱", "日期", "版本", "代碼", "數字"):
        for item in sorted(new[kind] - src[kind]):
            hits.append(("新增事實", f"{kind}{item}原稿沒有，疑似捏造"))
    return hits


def report(name, text):
    hits = scan(text)
    for line, col, rule, note in hits:
        print(f"{name}:{line}:{col}  {rule}  {note}")
    prose = strip_protected(text)
    skipped = sorted({w for w in load_context_terms() if w in prose})
    if skipped:
        print(f"{name}  略過標語境的詞，請人工看是不是大陸用法：{'、'.join(skipped)}", file=sys.stderr)
    return hits


def print_hints(name, text):
    for line, col, num, w in scan_patterns(text):
        print(f"{name}:{line}:{col}  提示  模式 {num}：{w}")
    for line, note in rhythm(text):
        print(f"{name}:{line}  提示  節奏：{note}")


def self_test():
    vocab = [("軟件", "軟體"), ("視頻", "影片")]
    rules = lambda t: {h[2] for h in scan(t, vocab)}

    assert rules("這個軟件很好用") == {"大陸用語"}
    assert rules("這個軟體很好用") == set()
    # 程式碼區塊與行內程式碼裡的大陸用語不算破綻
    assert rules("```\n安裝軟件\n```") == set()
    assert rules("執行 `install 軟件`") == set()
    assert rules("魯肉飯——台灣人的主食") == {"破折號"}
    assert rules("成本 3--5 元") == {"破折號"}
    assert rules("用 well-known 的方法") == set()
    # URL 後緊接中文與破折號不可被吞掉
    url_hits = rules("詳情見 https://example.com/a。這個軟件——超好用。")
    assert url_hits == {"大陸用語", "破折號"}, url_hits
    assert facts("請見https://example.com/path，並填寫表單。")["網址"] == {"https://example.com/path"}
    # YAML frontmatter 與 Markdown 表格分隔線不算破折號
    assert rules("---\ntitle: test\n---\n\n| 甲 | 乙 |\n|---|---|\n| 1 | 2 |\n") == set()
    assert rules("第一段\n\n---\n\n第二段") == set()
    assert rules("他說\u200b好") == {"隱形字元"}
    assert rules("見 https://a.com/?utm_source=chatgpt.com") == {"工具痕跡"}
    assert rules("打造“智慧”城市") == {"彎引號"}
    assert rules('他說"好"') == {"直引號"}
    for hw in ("你好,世界", "太棒了!", "真的嗎?", "備註:無", "甲;乙"):
        assert rules(hw) == {"半形標點"}, f"should flag half-width punct: {hw}"
    for hw_ok in ("NT$1,680", "下午 14:30", "React, Vue 都能用", "`a:b`", "https://a.com/x?a=1"):
        assert rules(hw_ok) == set(), f"false positive on {hw_ok}: {scan(hw_ok, vocab)}"
    assert rules("上線啦 🚀🎉🔥") == {"emoji 堆疊"}
    assert rules("上線啦 🚀") == set()
    assert rules("感謝您對【公司名稱】的支持") == {"佔位文字"}
    # 簡體字與簡轉繁錯字
    assert "簡體字" in rules("这是一个测试")
    for typo in ("這樣幹淨嗎", "頭發很長", "系統很復雜", "后來才發現", "這里很安靜", "一碗面條"):
        assert "簡轉繁錯字" in rules(typo), f"should flag typo: {typo}"
    for ok_zh in ("批准", "系統", "恢復", "回復正常", "乾淨", "頭髮", "這裡", "開頭發現", "皇後來了", "書面條款"):
        assert rules(ok_zh) == set(), f"false positive on {ok_zh}: {scan(ok_zh, vocab)}"
    # 行號要對
    assert scan("正常\n這個軟件", vocab)[0][0] == 2
    # 事實比對
    src = (
        "2026 年 10 月 1 日起年費由 NT$1,280 調整為 NT$1,580，優惠碼 EARLY2026，"
        "見 https://a.com/x 或 a@b.com。條款：「已付款者不受影響。」"
    )
    ok = (
        "自 2026年10月1日 起年費從 NT$1,280 調到 NT$1,580，優惠碼 EARLY2026，"
        "細節 https://a.com/x ，信箱 a@b.com。條款：「已付款者不受影響。」"
    )
    assert compare(src, ok) == [], compare(src, ok)
    # 拿掉 AI 追蹤參數不算遺失或新增網址
    assert compare(
        "詳情見 https://example.com/?utm_source=chatgpt.com",
        "詳情見 https://example.com/",
    ) == []
    # 日期縮水（protected-spans 案例實際發生過的失敗）
    cut = ok.replace("2026年10月1日", "10月1日")
    assert any(r == "遺失事實" and "日期" in n for r, n in compare(src, cut))
    # 引文被改寫
    assert any("引文" in n for r, n in compare(src, ok.replace("已付款者", "付過款的人")))
    # 憑空多出來的精確數字
    assert any(r == "新增事實" and "73.6" in n for r, n in compare(src, ok + "有 73.6% 的人同意。"))
    # 條列編號不算新增數字
    assert compare("甲乙", "1. 甲\n2. 乙") == []
    # Markdown 骨架：提示性檢查
    md = "# 標題\n\n見 [文件](https://a.com)。\n\n```\ncode\n```\n\n| a | b |\n|---|---|\n| 1 | 2 |\n"
    assert compare(md, md) == [] and compare_structure(md, md) == []
    gone = lambda d, k: any(r == "結構變動" and k in n for r, n in compare_structure(md, d))
    assert gone(md.replace("[文件](https://a.com)", "https://a.com"), "連結")
    assert gone(md.replace("```\ncode\n```", "code"), "程式碼區塊")
    assert gone(md.replace("# 標題\n\n", ""), "標題")
    assert gone(md.replace("| 1 | 2 |\n", ""), "表格列")
    # 程式碼區塊裡的 # 註解不算標題
    assert structure("```\n# note\n```")["標題"] == 0
    # 注意詞提示
    words = [(10, "專家指出"), (15, "未來可期")]
    assert [h[2:] for h in scan_patterns("專家指出，公司未來可期。", words)] == [(10, "專家指出"), (15, "未來可期")]
    assert scan_patterns("`專家指出`", words) == []
    adv_nums = {h[2] for h in scan_patterns("這不只是更新，更是突破。我們賦能團隊，你還在等什麼？首先，看數據。其次，看結果。從日常到未來不等。", [])}
    assert adv_nums == {6, 9, 24, 44, 60}, adv_nums
    watch = load_watchwords()
    assert len(watch) >= 100, f"注意詞太少（{len(watch)}），SKILL.md 格式可能變了"
    assert all(num != 36 for num, _ in watch)
    assert all("（" not in w and "。" not in w and "X" not in w for _, w in watch)
    # 節奏提示
    notes = lambda t: [n for _, n in rhythm(t)]
    assert any("模式 23" in n for n in notes("一切都變了。沒有回頭路。我們只能向前。"))
    assert not notes("好。我們走吧，天快黑了，再晚就趕不上末班車。")
    assert not notes("- 一\n- 二\n- 三")
    flat = "".join(f"第{i}句寫得一樣長長的。" for i in range(8))
    assert any("句子長度" in n for n in notes(flat))
    mixed = "好。" + "這一句故意寫得比較長，讓整段的句子長短有明顯的落差。" * 4 + "對。很好。然後呢，我們再看看接下來要怎麼走才對。"
    assert not any("句子長度" in n for n in notes(mixed))
    assert any("段落" in n for n in notes("\n\n".join(["這是一段剛好十二個字。"] * 4)))
    assert rhythm("\n\n第二段開頭。好。對。是。")[0][0] == 3
    # 真的讀得到 SKILL.md 的表
    real = load_vocab()
    assert len(real) >= 158, f"只讀到 {len(real)} 組大陸用語，表格格式可能變了"
    assert ("視頻", "影片") in real
    assert ("打印", "列印") in real and ("打印機", "印表機") in real
    for tech in ("配置文件", "報錯信息", "線程", "回滾", "復盤"):
        assert scan(tech, real), f"should flag {tech}"
    assert not scan("用戶端與大數據", real) and scan("通過考試的用戶", real)
    # 台灣常見日常詞與技術專詞不誤報
    for tw in (
        "現在線上報名", "濕紙巾", "菠蘿麵包", "非本科轉職", "晶華酒店", "東京地鐵",
        "脆皮雪糕", "古早味土豆麵筋", "馬鈴薯片", "物理質量",
        "閉環控制", "鏈路聚合", "地球內核", "歷史進程", "書法字體", "刷新紀錄",
    ):
        assert not scan(tw, real), f"TW false positive on {tw}: {scan(tw, real)}"
    # 標了語境的列不掃；長詞優先
    assert ("程序", "程式") not in real and not scan("程序正義與股票代碼", real)
    assert [h[3] for h in scan("視頻通話", real)] == ["模式 34：視頻通話 → 視訊通話"]
    assert [h[3] for h in scan("檢查配置文件與報錯信息", real)] == [
        "模式 34：配置文件 → 設定檔",
        "模式 34：報錯信息 → 錯誤訊息",
    ]
    assert len(scan("本周末去看展", real)) == 1
    assert not scan("青花菜", real) and scan("花菜", real)
    ctx = load_context_terms()
    for term in (
        "代碼", "程序", "酒店", "土豆", "本科", "地鐵", "雪糕", "質量", "菠蘿", "紙巾", "登錄",
        "內核", "進程", "字體", "鏡像", "接口", "刷新", "構建",
    ):
        assert term in ctx, f"missing context term: {term}"
    print(f"self-test ok（大陸用語表 {len(real)} 組）")


def main(argv):
    parser = argparse.ArgumentParser(description="機械可驗的中文去 AI 味破綻檢查")
    parser.add_argument("--self-test", action="store_true", help="執行自我測試")
    parser.add_argument("--source", metavar="ORIG", help="比對原稿與改寫稿的事實與 Markdown 骨架")
    parser.add_argument("--patterns", action="store_true", help="另外提示各模式注意詞與節奏（不影響 exit code）")
    parser.add_argument("files", nargs="*", help="待檢查檔案（省略則讀 stdin）")
    args = parser.parse_args(argv)

    if args.self_test:
        self_test()
        return 0

    if args.source:
        if len(args.files) > 1:
            print("用法：check.py --source 原稿.md [最終稿.md]", file=sys.stderr)
            return 2
        source = Path(args.source).read_text(encoding="utf-8")
        if args.files:
            draft_name = args.files[0]
            draft = Path(draft_name).read_text(encoding="utf-8")
        else:
            draft_name = "<stdin>"
            draft = sys.stdin.read()
        total = list(report(draft_name, draft))
        for rule, note in compare(source, draft):
            print(f"{draft_name}  {rule}  {note}")
            total.append(rule)
        for rule, note in compare_structure(source, draft):
            print(f"{draft_name}  提示  {rule}：{note}")
        if args.patterns:
            print_hints(draft_name, draft)
        if total:
            print(f"\n{len(total)} 個破綻。改完再交稿。", file=sys.stderr)
            return 1
        print("機械檢查與事實比對通過（語氣、節奏、人味請自己看）。", file=sys.stderr)
        return 0

    inputs = (
        [(p, Path(p).read_text(encoding="utf-8")) for p in args.files]
        if args.files
        else [("<stdin>", sys.stdin.read())]
    )
    total = []
    for name, text in inputs:
        total += report(name, text)
        if args.patterns:
            print_hints(name, text)
    if total:
        print(f"\n{len(total)} 個機械破綻。改完再交稿。", file=sys.stderr)
        return 1
    print("機械檢查通過（語氣、節奏、人味請自己看）。", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
