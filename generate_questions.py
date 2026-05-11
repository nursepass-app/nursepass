#!/usr/bin/env python3
"""
NursePass 問題半自動生成ツール
Claude API を使って看護師国家試験の問題を生成し、
レビュー後に questions.json へ追記する。

使用方法:
  python3 generate_questions.py

依存:
  .venv/bin/python3 (anthropic 0.100.0+)
環境変数:
  ANTHROPIC_API_KEY
"""

import json
import os
import sys
import textwrap
from pathlib import Path

STARS_MASTER_JSON = Path(__file__).parent / "stars_master.json"
DEFAULT_STARS = 2

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic パッケージが見つかりません。")
    print("  source .venv/bin/activate  してから再実行してください。")
    sys.exit(1)

QUESTIONS_JSON = Path(__file__).parent / "questions.json"
GENERATE_COUNT = 20


def load_stars_master() -> dict:
    with open(STARS_MASTER_JSON, encoding="utf-8") as f:
        return json.load(f)


def build_topic_to_stars(master: dict, subject_label: str) -> dict[str, int]:
    """マスターテーブルから {テーマ名: stars} の辞書を生成する。"""
    subject_data = master.get(subject_label, {})
    mapping: dict[str, int] = {}
    for stars_key, topics in subject_data.items():
        stars_val = int(stars_key.replace("stars", ""))
        for topic in topics:
            mapping[topic] = stars_val
    return mapping


def lookup_stars(topic: str, topic_to_stars: dict[str, int]) -> tuple[int, str]:
    """テーマ名でマスターテーブルを照合して (stars値, マッチしたキー) を返す。
    一致なしの場合は (DEFAULT_STARS, "") を返す。
    """
    if not topic:
        return DEFAULT_STARS, ""
    # 1. 完全一致
    if topic in topic_to_stars:
        return topic_to_stars[topic], topic
    # 2. マスターキーが topic に含まれる（前方部分一致）
    for key, stars in topic_to_stars.items():
        if key in topic:
            return stars, key
    # 3. topic がマスターキーに含まれる（逆部分一致）
    for key, stars in topic_to_stars.items():
        if topic in key:
            return stars, key
    return DEFAULT_STARS, ""


def build_topic_list_for_prompt(master: dict, subject_label: str) -> str:
    """システムプロンプト用のテーマ一覧文字列を生成する。"""
    subject_data = master.get(subject_label, {})
    lines = []
    label_map = {"stars3": "★★★(stars=3)", "stars2": "★★(stars=2)", "stars1": "★(stars=1)"}
    for stars_key in ("stars3", "stars2", "stars1"):
        topics = subject_data.get(stars_key, [])
        if topics:
            lines.append(f"【{label_map[stars_key]}】")
            lines.extend(f"  {t}" for t in topics)
    return "\n".join(lines)

SUBJECTS = {
    "1": {
        "label": "必修・基礎看護学",
        "category": "必修",
        "field": "必修・基礎看護学",
        "description": (
            "看護師国家試験「必修問題」の「基礎看護学」領域。"
            "バイタルサイン・感染予防・清潔ケア・体位・輸液・薬剤管理・"
            "看護過程・フィジカルアセスメントなど"
        ),
    },
    "2": {
        "label": "必修・健康支援と社会保障制度",
        "category": "必修",
        "field": "必修・健康支援と社会保障制度",
        "description": (
            "看護師国家試験「必修問題」の「健康支援と社会保障制度」領域。"
            "医療保険制度・介護保険・感染症法・精神保健福祉法・"
            "母子保健法・健康増進法・地域保健法・社会福祉など"
        ),
    },
}

SYSTEM_PROMPT_TEMPLATE = """あなたは看護師国家試験（日本）の問題作成専門家です。
指示された科目・領域の必修問題を正確かつ実践的に作成してください。

【問題作成の厳密なルール】
1. 実際の看護師国家試験の出題形式（4択一問一答）に完全に準拠する
2. 正解はA〜Dのいずれか1つのみ
3. 選択肢は紛らわしくなく、正解が明確であること
4. 解説は100〜150字程度で、なぜ正解なのかを明確に説明する
5. topic には下記マスターテーブルのテーマ名をそのまま設定する
   （stars の確定はシステム側で行うため、stars は仮置きで構わない）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
■ {subject_label}  テーマ・マスターテーブル
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{topic_list}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【topic フィールドの設定】
- 上記マスターテーブルのテーマ名を「完全一致」で設定してください
- 問題のメインテーマに最も近い行を1つ選ぶ
- テーブルにないテーマの場合は最も近い親テーマを選ぶ

【出力形式】
必ず以下のJSON配列形式のみで出力してください。余分なテキスト・マークダウンは不要です。
[
  {{
    "question": "問題文（〜はどれか。で終わる）",
    "choices": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
    "answer": "A",
    "explanation": "解説文（100〜150字）",
    "stars": 2,
    "topic": "マスターテーブルのテーマ名（完全一致）"
  }},
  ...
]"""


def build_system_prompt(subject_label: str, master: dict) -> str:
    topic_list = build_topic_list_for_prompt(master, subject_label)
    return SYSTEM_PROMPT_TEMPLATE.format(
        subject_label=subject_label,
        topic_list=topic_list,
    )


def load_questions() -> list[dict]:
    with open(QUESTIONS_JSON, encoding="utf-8") as f:
        return json.load(f)


def save_questions(questions: list[dict]) -> None:
    with open(QUESTIONS_JSON, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)


def get_next_id(questions: list[dict]) -> int:
    return max(q["id"] for q in questions) + 1


def get_existing_question_texts(questions: list[dict], field: str) -> list[str]:
    return [q["question"] for q in questions if q["field"] == field]


def generate_questions_via_api(
    subject: dict, existing_texts: list[str], count: int = 20
) -> list[dict]:
    """Claude API を呼び出して問題を生成し、マスターテーブルで stars を確定する。"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: 環境変数 ANTHROPIC_API_KEY が設定されていません。")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    master = load_stars_master()
    topic_to_stars = build_topic_to_stars(master, subject["label"])
    system_prompt = build_system_prompt(subject["label"], master)

    client = anthropic.Anthropic(api_key=api_key)
    existing_sample = "\n".join(f"- {t}" for t in existing_texts[:30])

    user_prompt = textwrap.dedent(f"""
        科目: {subject['label']}
        説明: {subject['description']}

        以下は既存の問題文（重複防止のために参照してください）:
        {existing_sample}

        上記と重複しない新しい問題を {count} 問作成してください。
        JSON配列のみを出力してください。
    """).strip()

    print(f"  Claude API に接続中... ({count}問生成リクエスト)")

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = message.content[0].text.strip()

    # JSON部分を抽出（```json ... ``` が含まれる場合も対応）
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    generated = json.loads(raw)

    # マスターテーブルで stars を確定（Claudeの仮置き値を上書き）
    matched = unmatched = 0
    for q in generated:
        stars, matched_key = lookup_stars(q.get("topic", ""), topic_to_stars)
        q["stars"] = stars
        q["matched_key"] = matched_key  # 表示専用
        if matched_key:
            matched += 1
        else:
            unmatched += 1

    print(f"  stars 照合: {matched}問マッチ / {unmatched}問デフォルト(stars={DEFAULT_STARS})")
    return generated


def display_question(idx: int, q: dict, total: int) -> None:
    """問題を整形して表示する。"""
    stars_str = "★" * q["stars"] + "☆" * (3 - q["stars"])
    print(f"\n{'─'*60}")
    topic_raw = q.get("topic", "")
    matched = q.get("matched_key", "")
    if matched:
        topic_str = f"\n  テーマ: {topic_raw}  →  [{matched}] (マスター照合)"
    elif topic_raw:
        topic_str = f"\n  テーマ: {topic_raw}  →  デフォルト stars={DEFAULT_STARS}"
    else:
        topic_str = ""
    print(f"[{idx}/{total}]  重要度: {stars_str} (stars={q['stars']}){topic_str}")
    print(f"\n{q['question']}")
    for key, val in q["choices"].items():
        mark = " ◀ 正解" if key == q["answer"] else ""
        print(f"  {key}: {val}{mark}")
    print(f"\n解説: {q['explanation']}")
    print(f"{'─'*60}")


def review_and_append(subject: dict, generated: list[dict]) -> None:
    """生成した問題をインタラクティブにレビューして questions.json に追記する。"""
    questions = load_questions()
    next_id = get_next_id(questions)
    approved = []
    total = len(generated)

    print(f"\n{'='*60}")
    print(f"  {total}問生成しました。1問ずつレビューしてください。")
    print(f"  y = 追加  n = スキップ  s = stars変更  e = 全編集  q = 終了して保存")
    print(f"{'='*60}")

    for i, q in enumerate(generated, 1):
        display_question(i, q, total)

        while True:
            choice = input("\n  操作を選んでください [y/n/s/e/q]: ").strip().lower()
            if choice == "y":
                entry = {
                    "id": next_id + len(approved),
                    "category": subject["category"],
                    "field": subject["field"],
                    "question": q["question"],
                    "choices": q["choices"],
                    "answer": q["answer"],
                    "explanation": q["explanation"],
                    "stars": q["stars"],
                }
                approved.append(entry)
                print(f"  ✓ 追加しました (id={entry['id']})")
                break
            elif choice == "n":
                print("  スキップしました。")
                break
            elif choice == "s":
                stars_now = "★" * q["stars"] + "☆" * (3 - q["stars"])
                print(f"  現在の stars: {stars_now} ({q['stars']})")
                print("  新しい stars を入力してください（1〜3、空白でキャンセル）:")
                new_stars = input("  >> ").strip()
                if new_stars in ("1", "2", "3"):
                    q["stars"] = int(new_stars)
                    stars_new = "★" * q["stars"] + "☆" * (3 - q["stars"])
                    print(f"  ✓ stars を {stars_new} ({q['stars']}) に変更しました。")
                elif new_stars == "":
                    print("  キャンセルしました。")
                else:
                    print("  1〜3 の数字を入力してください。")
            elif choice == "e":
                print("  問題文を入力してください（空白でそのまま）:")
                new_q = input("  >> ").strip()
                if new_q:
                    q["question"] = new_q
                print("  解説を入力してください（空白でそのまま）:")
                new_exp = input("  >> ").strip()
                if new_exp:
                    q["explanation"] = new_exp
                print("  stars を入力してください（1〜3、空白でそのまま）:")
                new_stars = input("  >> ").strip()
                if new_stars in ("1", "2", "3"):
                    q["stars"] = int(new_stars)
                display_question(i, q, total)
            elif choice == "q":
                print("\n  レビューを終了します。")
                break
            else:
                print("  y / n / s / e / q のいずれかを入力してください。")

        if choice == "q":
            break

    if not approved:
        print("\n追加する問題がありませんでした。questions.json は変更していません。")
        return

    questions.extend(approved)
    save_questions(questions)
    print(f"\n{'='*60}")
    print(f"  {len(approved)}問を questions.json に追記しました。")
    print(f"  追加 ID: {approved[0]['id']} 〜 {approved[-1]['id']}")
    print(f"  総問題数: {len(questions)}")
    print(f"{'='*60}")


def select_subject() -> dict:
    print("\n" + "="*60)
    print("  NursePass 問題生成ツール")
    print("="*60)
    print("\n科目を選択してください:\n")
    for key, subj in SUBJECTS.items():
        print(f"  {key}. {subj['label']}")
    print()

    while True:
        choice = input(">> ").strip()
        if choice in SUBJECTS:
            return SUBJECTS[choice]
        print(f"  {', '.join(SUBJECTS.keys())} のいずれかを入力してください。")


def main() -> None:
    subject = select_subject()
    print(f"\n科目: {subject['label']} を選択しました。")
    print(f"{GENERATE_COUNT}問を生成します...\n")

    questions = load_questions()
    existing_texts = get_existing_question_texts(questions, subject["field"])
    print(f"  既存問題数（同科目）: {len(existing_texts)}問")

    try:
        generated = generate_questions_via_api(subject, existing_texts, GENERATE_COUNT)
    except json.JSONDecodeError as e:
        print(f"ERROR: APIの応答をJSONとして解析できませんでした: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: API呼び出しに失敗しました: {e}")
        sys.exit(1)

    print(f"  {len(generated)}問の生成が完了しました。")

    review_and_append(subject, generated)


if __name__ == "__main__":
    main()
