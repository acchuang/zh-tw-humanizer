#!/usr/bin/env python3
"""機械可驗的破綻檢查。給 SKILL.md 流程第 6 步用，取代人工打分。

用法：
    python3 scripts/check.py 最終稿.md
    cat 最終稿.md | python3 scripts/check.py
    python3 scripts/check.py --self-test

只檢查「查得準」的規則：破折號、大陸用語、隱形字元、彎引號、工具痕跡、
emoji 密度、佔位文字。語氣、節奏、人味這種要判斷的，機器不管。
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

    for term, fix in vocab:
        for m in re.finditer(re.escape(term), prose):
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
    # 真的讀得到 SKILL.md 的表
    real = load_vocab()
    assert len(real) >= 45, f"只讀到 {len(real)} 組大陸用語，表格格式可能變了"
    assert ("視頻", "影片") in real
    print(f"self-test ok（大陸用語表 {len(real)} 組）")


def main(argv):
    if "--self-test" in argv:
        self_test()
        return 0
    paths = [a for a in argv if not a.startswith("-")]
    total = []
    if paths:
        for p in paths:
            total += report(p, Path(p).read_text(encoding="utf-8"))
    else:
        total += report("<stdin>", sys.stdin.read())
    if total:
        print(f"\n{len(total)} 個機械破綻。改完再交稿。", file=sys.stderr)
        return 1
    print("機械檢查通過（語氣、節奏、人味請自己看）。", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
