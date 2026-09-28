#!/usr/bin/env python3
"""語義保真與台灣在地化檢查。使用 TypeSafe AI System One (jev-latest)。

針對 SKILL.md 的核心約定「不捏造事實、保留全部細節、道地台灣繁體」進行語義級驗證。
與 scripts/check.py（機械規則檢查）互補。

用法：
    python3 scripts/verify_semantic.py 原文.md 改寫稿.md
    python3 scripts/verify_semantic.py --self-test
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

TYPESAFE_ENDPOINT = os.environ.get(
    "TYPESAFE_ENDPOINT", "https://api.typesafe.ai/v1/system_one"
)
TYPESAFE_MODEL = os.environ.get("TYPESAFE_MODEL", "jev-latest")


def call_typesafe(state: dict, questions: dict, api_key: str = None) -> dict:
    key = api_key or os.environ.get("TYPESAFE_API_KEY")
    if not key:
        print("❌ 錯誤：未設定環境變數 TYPESAFE_API_KEY", file=sys.stderr)
        sys.exit(1)

    payload = json.dumps(
        {
            "model": TYPESAFE_MODEL,
            "state": state,
            "questions": questions,
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        TYPESAFE_ENDPOINT,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key.strip()}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30.0) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        print(f"❌ TypeSafe API 回應錯誤 ({e.code}): {err}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 網路連線失敗: {e}", file=sys.stderr)
        sys.exit(1)


def verify_semantic_fidelity(original: str, rewritten: str, mock_fn=None) -> dict:
    """使用 TypeSafe Choice 與 Noul 評估語義保真度與台灣繁體道地度。"""
    questions = {
        "fact_fidelity": {
            "type": "choice",
            "instructions": (
                "請比較改寫稿與原文的語義與事實。改寫稿是否有捏造未提及的事實、篡改數字/限制，或忠實保留原本意思？"
            ),
            "criteria": {
                "preserves_meaning": "忠實保留所有核心事實、細節與約束，沒有捏造新資訊或顛倒意思",
                "fabricates_facts": "添加了原文完全未提及的事實細節、數據或虛構背景",
                "contradicts_or_omits": "改寫後與原文核心意思矛盾、數字/日期被改錯，或遺漏了關鍵指示",
            },
        },
        "tw_naturalness": {
            "type": "choice",
            "instructions": (
                "評估改寫稿的語言習慣：是否為道地的台灣繁體中文，且擺脫了常見的生硬 AI 翻譯腔與大陸句式？"
            ),
            "criteria": {
                "authentic_tw": "自然流暢的台灣慣用繁體中文，符合台灣生活語境與說話節奏",
                "ai_or_mainland_tone": "仍帶有明顯的大陸語用語意、機械翻譯句法或生硬的 AI 說教腔",
            },
        },
    }

    state = {
        "original_text": original.strip()[:4000],
        "rewritten_text": rewritten.strip()[:4000],
    }

    if mock_fn:
        return mock_fn(state, questions)
    return call_typesafe(state, questions)


def run_checks(original_text: str, rewritten_text: str, mock_fn=None) -> bool:
    resp = verify_semantic_fidelity(original_text, rewritten_text, mock_fn=mock_fn)
    answers = resp.get("answers", {})

    fact = answers.get("fact_fidelity", {})
    tw = answers.get("tw_naturalness", {})

    fact_choice = fact.get("choice", "unknown")
    fact_conf = fact.get("confidence", 0.0)

    tw_choice = tw.get("choice", "unknown")
    tw_conf = tw.get("confidence", 0.0)

    passed = True

    print("\n🔍 TypeSafe AI 語義評估報告 (System One / jev-latest)")
    print("=" * 60)

    # 檢查 1: 事實保真度
    if fact_choice == "preserves_meaning":
        print(f"✅ 事實保真度: 通過 (忠實保留原文語義, 信心度: {fact_conf:.2f})")
    elif fact_choice == "fabricates_facts":
        print(f"❌ 事實保真度: 失敗 - 檢測到捏造未提及的事實 (信心度: {fact_conf:.2f})")
        passed = False
    elif fact_choice == "contradicts_or_omits":
        print(f"❌ 事實保真度: 失敗 - 核心意思矛盾或關鍵細節遺漏 (信心度: {fact_conf:.2f})")
        passed = False
    else:
        print(f"⚠️ 事實保真度: 判定未明 ({fact_choice})")

    # 檢查 2: 台灣在地化與無 AI 腔
    if tw_choice == "authentic_tw":
        print(f"✅ 台灣繁體在地化: 通過 (自然道地, 信心度: {tw_conf:.2f})")
    elif tw_choice == "ai_or_mainland_tone":
        print(f"⚠️ 台灣繁體在地化: 仍有殘留 AI 翻譯腔或大陸語意 (信心度: {tw_conf:.2f})")
        # 標註提醒，若信心度極高則視為需調整
        if tw_conf >= 0.85:
            passed = False
    else:
        print(f"⚠️ 在地化評估: 判定未明 ({tw_choice})")

    print("=" * 60)
    return passed


def self_test():
    """自我測試：驗證模擬回傳與邏輯判斷正確性。"""
    print("執行 verify_semantic.py 自我測試...")

    def mock_pass(state, questions):
        return {
            "model": "jev-latest",
            "answers": {
                "fact_fidelity": {"type": "choice", "choice": "preserves_meaning", "confidence": 0.94},
                "tw_naturalness": {"type": "choice", "choice": "authentic_tw", "confidence": 0.91},
            },
        }

    def mock_fabrication(state, questions):
        return {
            "model": "jev-latest",
            "answers": {
                "fact_fidelity": {"type": "choice", "choice": "fabricates_facts", "confidence": 0.96},
                "tw_naturalness": {"type": "choice", "choice": "authentic_tw", "confidence": 0.88},
            },
        }

    assert run_checks("原文", "改寫", mock_fn=mock_pass) is True
    assert run_checks("原文", "捏造細節改寫", mock_fn=mock_fabrication) is False

    print("✅ 自我測試全部通過！")


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        self_test()
        sys.exit(0)

    if len(sys.argv) < 3:
        print("用法: python3 scripts/verify_semantic.py 原文.md 改寫稿.md", file=sys.stderr)
        print("      python3 scripts/verify_semantic.py --self-test", file=sys.stderr)
        sys.exit(2)

    orig_path = Path(sys.argv[1])
    rewr_path = Path(sys.argv[2])

    if not orig_path.exists():
        print(f"找不到檔案: {orig_path}", file=sys.stderr)
        sys.exit(1)
    if not rewr_path.exists():
        print(f"找不到檔案: {rewr_path}", file=sys.stderr)
        sys.exit(1)

    orig = orig_path.read_text(encoding="utf-8")
    rewr = rewr_path.read_text(encoding="utf-8")

    ok = run_checks(orig, rewr)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
