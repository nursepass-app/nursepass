#!/usr/bin/env python3
"""
NursePass 問題半自動生成ツール
Claude API を使って看護師国家試験の問題を生成し、
レビュー後に questions.json へ追記する。

【生成モード】
  python3 generate_questions.py --subject "基礎看護学" --count 5
  → generated_YYYYMMDD_HHMMSS.json に保存し全問を表示

【承認モード】
  python3 generate_questions.py --approve generated_*.json [--reject 2,4]
  → questions.json に追記（--reject で除外する問題番号を指定）

依存:
  .venv/bin/python3 (anthropic 0.100.0+)
環境変数:
  ANTHROPIC_API_KEY
"""

import argparse
import json
import os
import sys
import textwrap
from collections import Counter
from datetime import datetime
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


def find_subject(query: str) -> dict:
    """--subject 引数から科目情報を解決する（番号・完全一致・部分一致に対応）。"""
    # 番号指定（1, 2）
    if query in SUBJECTS:
        return SUBJECTS[query]

    # SUBJECTS のラベルで完全一致
    for s in SUBJECTS.values():
        if s["label"] == query:
            return s

    # questions.json の全フィールドで部分一致
    with open(QUESTIONS_JSON, encoding="utf-8") as f:
        data = json.load(f)

    all_fields = sorted(set(q["field"] for q in data))

    if query in all_fields:
        matched_field = query
    else:
        candidates = [f for f in all_fields if query in f]
        if len(candidates) == 1:
            matched_field = candidates[0]
        elif len(candidates) > 1:
            print(f"複数の科目が候補として見つかりました（より具体的に指定してください）:")
            for c in candidates:
                print(f"  {c}")
            sys.exit(1)
        else:
            print(f"科目 '{query}' が見つかりません。利用可能な科目:")
            for f in all_fields:
                print(f"  {f}")
            sys.exit(1)

    cats = Counter(q["category"] for q in data if q["field"] == matched_field)
    category = cats.most_common(1)[0][0]
    return {
        "label": matched_field,
        "category": category,
        "field": matched_field,
        "description": f"看護師国家試験「{category}問題」の「{matched_field}」領域。",
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


def save_generated(subject: dict, generated: list[dict]) -> Path:
    """生成した問題を中間ファイルに保存して返す。"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = Path(__file__).parent / f"generated_{timestamp}.json"
    payload = {
        "subject": subject,
        "generated_at": datetime.now().isoformat(),
        "questions": [dict(idx=i + 1, **q) for i, q in enumerate(generated)],
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return out_path


def approve_from_file(file_path: Path, reject_indices: set[int]) -> None:
    """生成済みファイルから問題を読み込み、questions.json に追記する。"""
    with open(file_path, encoding="utf-8") as f:
        payload = json.load(f)

    subject = payload["subject"]
    candidates = payload["questions"]
    total = len(candidates)
    approved_qs = [q for q in candidates if q["idx"] not in reject_indices]

    if not approved_qs:
        print("承認する問題がありません。questions.json は変更していません。")
        return

    questions = load_questions()
    next_id = get_next_id(questions)

    entries = []
    for i, q in enumerate(approved_qs):
        entries.append({
            "id": next_id + i,
            "category": subject["category"],
            "field": subject["field"],
            "question": q["question"],
            "choices": q["choices"],
            "answer": q["answer"],
            "explanation": q["explanation"],
            "stars": q["stars"],
        })

    questions.extend(entries)
    save_questions(questions)

    skipped = total - len(approved_qs)
    print(f"\n{'='*60}")
    print(f"  {len(entries)}問を questions.json に追記しました。")
    if skipped:
        print(f"  スキップ: {skipped}問（--reject {','.join(str(i) for i in sorted(reject_indices))}）")
    print(f"  追加 ID: {entries[0]['id']} 〜 {entries[-1]['id']}")
    print(f"  総問題数: {len(questions)}")
    print(f"{'='*60}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="NursePass 問題半自動生成ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            【生成モード】
              python3 generate_questions.py --subject "基礎看護学" --count 5

            【承認モード】
              python3 generate_questions.py --approve generated_*.json
              python3 generate_questions.py --approve generated_*.json --reject 2,4
        """),
    )
    parser.add_argument("--subject", "-s", help="科目名（部分一致可）")
    parser.add_argument("--count", "-n", type=int, default=GENERATE_COUNT,
                        help=f"生成問題数（デフォルト: {GENERATE_COUNT}）")
    parser.add_argument("--approve", metavar="FILE",
                        help="生成済みJSONを承認して questions.json に追記")
    parser.add_argument("--reject", default="",
                        help="除外する問題番号（カンマ区切り: 2,4,7）。--approve と併用")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # ── 承認モード ──────────────────────────────────────
    if args.approve:
        file_path = Path(args.approve)
        if not file_path.exists():
            print(f"ERROR: ファイルが見つかりません: {file_path}")
            sys.exit(1)

        reject_indices: set[int] = set()
        if args.reject:
            try:
                reject_indices = {int(x.strip()) for x in args.reject.split(",") if x.strip()}
            except ValueError:
                print("ERROR: --reject には整数をカンマ区切りで指定してください（例: 2,4,7）")
                sys.exit(1)

        with open(file_path, encoding="utf-8") as f:
            payload = json.load(f)
        total = len(payload["questions"])

        print(f"\n{'='*60}")
        print(f"  承認モード: {file_path.name}")
        print(f"  科目: {payload['subject']['label']}")
        print(f"  問題数: {total}問  除外: {sorted(reject_indices) or 'なし'}")
        print(f"{'='*60}")

        for q in payload["questions"]:
            skip = " ← スキップ" if q["idx"] in reject_indices else ""
            display_question(q["idx"], q, total)
            if skip:
                print(f"  [除外]{skip}")

        approve_from_file(file_path, reject_indices)
        return

    # ── 生成モード ──────────────────────────────────────
    if not args.subject:
        print("ERROR: --subject を指定してください。")
        print("  例: python3 generate_questions.py --subject \"基礎看護学\" --count 5")
        sys.exit(1)

    subject = find_subject(args.subject)
    count = args.count

    print(f"\n{'='*60}")
    print(f"  NursePass 問題生成ツール")
    print(f"  科目: {subject['label']}  問題数: {count}問")
    print(f"{'='*60}\n")

    questions = load_questions()
    existing_texts = get_existing_question_texts(questions, subject["field"])
    print(f"  既存問題数（同科目）: {len(existing_texts)}問")

    try:
        generated = generate_questions_via_api(subject, existing_texts, count)
    except json.JSONDecodeError as e:
        print(f"ERROR: APIの応答をJSONとして解析できませんでした: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: API呼び出しに失敗しました: {e}")
        sys.exit(1)

    print(f"  {len(generated)}問の生成が完了しました。\n")

    for i, q in enumerate(generated, 1):
        display_question(i, q, len(generated))

    out_path = save_generated(subject, generated)
    print(f"\n{'='*60}")
    print(f"  生成ファイル: {out_path.name}")
    print(f"  レビュー後、以下のコマンドで承認してください:")
    print(f"    python3 generate_questions.py --approve {out_path.name}")
    print(f"    python3 generate_questions.py --approve {out_path.name} --reject 2,4")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
