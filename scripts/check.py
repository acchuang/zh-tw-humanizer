#!/usr/bin/env python3
"""機械可驗的破綻檢查。給 SKILL.md 流程第 6 步用，取代人工打分。

用法：
    python3 scripts/check.py 最終稿.md
    cat 最終稿.md | python3 scripts/check.py
    python3 scripts/check.py --source 原稿.md 最終稿.md   # 另外比對事實有沒有掉、有沒有憑空多
    python3 scripts/check.py --patterns 稿.md            # 另外列出 SKILL.md 各模式「注意詞」的命中（只提示，不影響結果）
    python3 scripts/check.py --self-test

只檢查「查得準」的規則：破折號、大陸用語、隱形字元、彎引號、工具痕跡、
emoji 密度、佔位文字。語氣、節奏、人味這種要判斷的，機器不管。
--source 模式再加一道事實比對：原稿的數字、日期、版本、網址、信箱、代碼、
「」引文、程式碼，改寫後要原樣在；改寫後出現原稿沒有的數字、網址、信箱、代碼，
就是捏造。中文數字（三成）換成阿拉伯數字（30%）會被當成新增，這是已知的誤報。
大陸用語表直接從 SKILL.md 模式 34 讀，不在這裡重抄一份。
"""

import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / "SKILL.md"

INVISIBLE = {
    "​": "零寬空格",
    "‌": "零寬不連字",
    "‍": "零寬連字",
    "﻿": "BOM／零寬不斷空格",
    "⁠": "word joiner",
    " ": "不換行空格（換成一般空格）",
    " ": "窄空格",
    " ": "窄不換行空格",
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

EMOJI = re.compile(
    "[\U0001f300-\U0001faff\U00002600-\U000027bf\U0001f1e6-\U0001f1ff⬀-⯿]"
)
CJK = r"㐀-鿿豈-﫿"


def load_vocab(skill_path=SKILL):
    """從 SKILL.md 模式 34 的表格讀大陸用語對照。找不到就回空表。"""
    if not skill_path.exists():
        return []
    body = skill_path.read_text(encoding="utf-8")
    section = re.search(r"^### 34\..*?$(.*?)^### 35\.", body, re.S | re.M)
    if not section:
        return []
    pairs = []
    for left, right in re.findall(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$",
                                  section.group(1), re.M):
        if left in ("大陸用語", "---", ":---") or set(left) <= {"-", ":"}:
            continue
        # 表格裡「程序（軟體語境）」這種註記不是要比對的字串
        term = re.sub(r"（.*?）", "", left).strip()
        for variant in [t for t in re.split(r"[／/]", term) if t]:
            pairs.append((variant, right))
    return pairs


def load_exempt(skill_path=SKILL):
    """模式 34「台灣也用」清單：命中這些詞的片段不算大陸用語。"""
    if not skill_path.exists():
        return []
    m = re.search(r"^\*\*台灣也用（不要改）\*\*：(.+)$",
                  skill_path.read_text(encoding="utf-8"), re.M)
    return [w.strip() for w in m.group(1).split("、") if w.strip()] if m else []


def load_watchwords(skill_path=SKILL):
    """從 SKILL.md 各模式的「**注意詞**」行讀詞。回傳 [(模式編號, 詞)]。
    兩字以下的詞（作為、豐富）太常見，會把提示淹掉，不收。「……」是句型，不是詞。"""
    if not skill_path.exists():
        return []
    body = skill_path.read_text(encoding="utf-8")
    out = []
    for num, block in re.findall(r"^### (\d+)\.(.*?)(?=^### |\Z)", body, re.S | re.M):
        m = re.search(r"^\*\*注意詞\*\*：(.+)$", block, re.M)
        if not m:
            continue
        for w in re.split(r"[、，,；;]", m.group(1).rstrip("。")):
            w = w.strip()
            if len(w) >= 3 and "……" not in w:
                out.append((int(num), w))
    return out


def scan_patterns(text, words=None):
    """注意詞命中，回傳 [(行, 欄, 模式編號, 詞)]。命中不代表有問題，只是該看一眼。"""
    words = load_watchwords() if words is None else words
    prose = strip_protected(text)
    hits = []
    for num, w in words:
        for m in re.finditer(re.escape(w), prose):
            line = prose.count("\n", 0, m.start()) + 1
            col = m.start() - (prose.rfind("\n", 0, m.start()) + 1) + 1
            hits.append((line, col, num, w))
    return sorted(hits)


def strip_protected(text):
    """把程式碼區塊、行內程式碼、URL 換成等長空白，位置不變，內容不掃。"""
    def blank(m):
        return re.sub(r"[^\n]", " ", m.group(0))

    text = re.sub(r"^```.*?^```", blank, text, flags=re.S | re.M)
    text = re.sub(r"`[^`\n]+`", blank, text)
    text = re.sub(r"https?://\S+", blank, text)
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
        add(m.start(), "隱形字元",
            f"U+{ord(ch):04X} {INVISIBLE[ch]}")
    for m in re.finditer("[\U000e0000-\U000e007f]", text):
        add(m.start(), "隱形字元", f"U+{ord(m.group(0)):05X} tag character")

    for m in re.finditer(r"——|--|—", prose):
        add(m.start(), "破折號", f"模式 27：{m.group(0)!r} 是硬規則，改標點或重組句子")

    for m in re.finditer(r"[“”‘’]", prose):
        add(m.start(), "彎引號",
            f"模式 46：{m.group(0)} 換成「」『』")

    for m in re.finditer(f'["\'](?=[{CJK}])|(?<=[{CJK}])["\']', prose):
        add(m.start(), "直引號", "模式 46：中文裡的英文引號，換成「」")

    exempt = [m.span() for w in load_exempt()
              for m in re.finditer(re.escape(w), prose)]
    for term, fix in vocab:
        for m in re.finditer(re.escape(term), prose):
            if any(a <= m.start() and m.end() <= b for a, b in exempt):
                continue
            add(m.start(), "大陸用語", f"模式 34：{term} → {fix}")

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


URL_RE = re.compile(r"https?://[^\s)）」』>\]]+")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
DATE_RE = re.compile(r"\d{4}\s*年\s*\d{1,2}\s*月(?:\s*\d{1,2}\s*日)?|\d{1,2}\s*月\s*\d{1,2}\s*日")
VERSION_RE = re.compile(r"\bv?\d+(?:\.\d+){2,}\b")
NUMBER_RE = re.compile(r"\d[\d,]*(?:\.\d+)?")
CODE_RE = re.compile(r"\b(?=[A-Z0-9]*[A-Z])(?=[A-Z0-9]*\d)[A-Z][A-Z0-9]{3,}\b")
QUOTE_RE = re.compile(r"「[^」]+」|『[^』]+』")
FENCE_RE = re.compile(r"^```.*?^```|`[^`\n]+`", re.S | re.M)


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
    take(URL_RE, "網址", lambda u: u.rstrip(".,;:。，；：！？"))
    take(EMAIL_RE, "信箱", str.lower)
    take(DATE_RE, "日期", lambda d: re.sub(r"\s+", "", d))
    take(VERSION_RE, "版本", lambda v: v.lstrip("v"))
    take(CODE_RE, "代碼")
    # 條列編號和標題記號不是事實
    text = re.sub(r"^\s*(?:\d+[.)、]|#+)\s", "", text, flags=re.M)
    take(NUMBER_RE, "數字", lambda n: n.replace(",", ""))
    return out


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
    return hits


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
    assert rules("他說​好") == {"隱形字元"}
    assert rules("見 https://a.com/?utm_source=chatgpt.com") == {"工具痕跡"}
    assert rules("打造“智慧”城市") == {"彎引號"}
    assert rules('他說"好"') == {"直引號"}
    assert rules("上線啦 🚀🎉🔥") == {"emoji 堆疊"}
    assert rules("上線啦 🚀") == set()
    assert rules("感謝您對【公司名稱】的支持") == {"佔位文字"}
    # 行號要對
    assert scan("正常\n這個軟件", vocab)[0][0] == 2
    # 事實比對
    src = ("2026 年 10 月 1 日起年費由 NT$1,280 調整為 NT$1,580，優惠碼 EARLY2026，"
           "見 https://a.com/x 或 a@b.com。條款：「已付款者不受影響。」")
    ok = ("自 2026年10月1日 起年費從 NT$1,280 調到 NT$1,580，優惠碼 EARLY2026，"
          "細節 https://a.com/x ，信箱 a@b.com。條款：「已付款者不受影響。」")
    assert compare(src, ok) == [], compare(src, ok)
    # 日期縮水（protected-spans 案例實際發生過的失敗）
    cut = ok.replace("2026年10月1日", "10月1日")
    assert any(r == "遺失事實" and "日期" in n for r, n in compare(src, cut))
    # 引文被改寫
    assert any("引文" in n for r, n in compare(src, ok.replace("已付款者", "付過款的人")))
    # 憑空多出來的精確數字
    assert any(r == "新增事實" and "73.6" in n for r, n in compare(src, ok + "有 73.6% 的人同意。"))
    # 條列編號不算新增數字
    assert compare("甲乙", "1. 甲\n2. 乙") == []
    # 注意詞提示
    words = [(10, "專家指出"), (15, "未來可期")]
    assert [h[2:] for h in scan_patterns("專家指出，公司未來可期。", words)] == [(10, "專家指出"), (15, "未來可期")]
    assert scan_patterns("`專家指出`", words) == []
    assert len(load_watchwords()) >= 100, "讀不到注意詞，SKILL.md 格式可能變了"
    # 真的讀得到 SKILL.md 的表
    real = load_vocab()
    assert len(real) >= 150, f"只讀到 {len(real)} 組大陸用語，表格格式可能變了"
    assert ("視頻", "影片") in real
    assert not scan("用戶端與大數據", real) and scan("通過考試的用戶", real)
    print(f"self-test ok（大陸用語表 {len(real)} 組）")


def main(argv):
    if "--self-test" in argv:
        self_test()
        return 0
    if "--source" in argv:
        i = argv.index("--source")
        if len(argv) != i + 3 or i != 0:
            print("用法：check.py --source 原稿.md 最終稿.md", file=sys.stderr)
            return 2
        src_path, draft_path = argv[1], argv[2]
        source = Path(src_path).read_text(encoding="utf-8")
        draft = Path(draft_path).read_text(encoding="utf-8")
        total = report(draft_path, draft)
        for rule, note in compare(source, draft):
            print(f"{draft_path}  {rule}  {note}")
            total.append(rule)
        if total:
            print(f"\n{len(total)} 個破綻。改完再交稿。", file=sys.stderr)
            return 1
        print("機械檢查與事實比對通過（語氣、節奏、人味請自己看）。", file=sys.stderr)
        return 0
    hint = "--patterns" in argv
    paths = [a for a in argv if not a.startswith("-")]
    total = []
    if paths:
        for p in paths:
            total += report(p, Path(p).read_text(encoding="utf-8"))
    else:
        total += report("<stdin>", sys.stdin.read())
    if hint:
        for p in paths:
            for line, col, num, w in scan_patterns(Path(p).read_text(encoding="utf-8")):
                print(f"{p}:{line}:{col}  提示  模式 {num}：{w}")
    if total:
        print(f"\n{len(total)} 個機械破綻。改完再交稿。", file=sys.stderr)
        return 1
    print("機械檢查通過（語氣、節奏、人味請自己看）。", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
