import json, random

START_ID = 3001
END_ID = 3011
SEED = 300

# (question, correct_answer, wrong1, wrong2, wrong3, explanation, stars)
RAW_QUESTIONS = [
    # 老年看護 (6問)
    ("フレイルの5つの表現型（Friedの基準）として正しいのはどれか。",
     "体重減少・疲労感・歩行速度低下・握力低下・身体活動低下",
     "認知症・うつ・転倒・骨粗鬆症・失禁",
     "視力低下・聴力低下・嚥下障害・排尿障害・皮膚障害",
     "高血圧・糖尿病・慢性腎臓病・慢性閉塞性肺疾患・がん",
     "Friedらのフレイル基準は①体重減少②疲労感③歩行速度低下④握力低下⑤身体活動低下の5項目。3項目以上でフレイル、1〜2項目でプレフレイルと判定する。",
     2),
    ("認知症の中核症状として正しいのはどれか。",
     "記憶障害・見当識障害・実行機能障害・失語・失行・失認",
     "幻覚・妄想・徘徊・暴力行為・睡眠障害",
     "不眠・食欲低下・体重減少・意欲低下・自責感",
     "麻痺・感覚障害・運動失調・嚥下障害・言語障害",
     "認知症の中核症状は認知機能障害（記憶・見当識・言語・実行機能など）そのもの。幻覚・徘徊・暴言などは行動・心理症状（BPSD）であり周辺症状と呼ばれる。",
     2),
    ("高齢者の転倒予防に最も効果が高いとされる介入はどれか。",
     "バランス訓練と筋力強化を含む複合的な運動プログラム",
     "車椅子移動への全面変更",
     "拘束帯（身体抑制）の使用",
     "危険を避けるため安静臥床の継続",
     "転倒予防の最良エビデンスは複合的運動プログラム（バランス・筋力・歩行訓練の組み合わせ）。身体抑制は転倒リスクを下げず、筋力低下・せん妄などを引き起こす可能性がある。",
     2),
    ("高齢者のポリファーマシーが問題とされる主な理由はどれか。",
     "薬物相互作用・副作用リスクの増大と服薬アドヒアランスの低下",
     "薬代が増加する経済的問題のみ",
     "薬の保管場所が不足するため",
     "医師の処方作業量が増えるため",
     "高齢者はポリファーマシー（多剤服用、一般的に6種類以上）で薬物相互作用・副作用リスクが増大し、転倒・認知機能低下・QOL低下を引き起こす。処方の見直し（減薬）が推奨される。",
     2),
    ("高齢者の栄養状態評価に用いる専用スクリーニングツールはどれか。",
     "MNA（簡易栄養状態評価表）",
     "BMIのみによる評価",
     "MUST（Malnutrition Universal Screening Tool）",
     "NRS-2002（Nutritional Risk Screening 2002）",
     "MNA（Mini Nutritional Assessment）は65歳以上の高齢者専用の栄養スクリーニングツール。18点未満で低栄養リスク、17点以下で低栄養と判定。BMIと比較してサルコペニアも捉えやすい。",
     2),
    ("嚥下障害のある高齢者への食事提供で適切なのはどれか。",
     "増粘剤でとろみをつけた均一な食形態（嚥下調整食）を提供する",
     "水分はサラサラの状態で提供し飲みやすくする",
     "固形物のみ提供し液体は禁忌とする",
     "経管栄養に切り替えて全経口摂取を禁止する",
     "嚥下障害では水分は誤嚥しやすい。増粘剤でとろみをつけた嚥下調整食の提供が必要。経管栄養は誤嚥リスクが高く経口摂取が困難な場合の選択肢であり、可能な限り経口摂取を維持する。",
     1),
    # 精神看護 (5問)
    ("統合失調症の陽性症状として正しいのはどれか。",
     "幻聴・妄想・思考解体・興奮",
     "感情平板化・無気力・無言・意欲低下",
     "認知機能障害・記憶障害・失見当識",
     "抑うつ気分・睡眠障害・希死念慮",
     "陽性症状は正常機能の過剰・歪み（幻聴・幻視・妄想・解体した思考・興奮）。陰性症状は機能の欠如（感情平板化・無気力・無言・意欲低下）。両者の区別が重要。",
     2),
    ("うつ病患者への看護として最も適切な対応はどれか。",
     "患者のペースに合わせた傾聴を行い「頑張れ」という言葉は控える",
     "積極的に社会復帰を促し活動量を増やす",
     "患者の訴えには即座に解決策を提示する",
     "自殺念慮については患者が自発的に話すまで確認しない",
     "うつ病患者への「頑張れ」はさらなる重荷となる。傾聴・共感が基本。自殺念慮は直接確認することが必要（聞いても自殺を誘発しないという研究がある）。回復期以外の積極的な活動強制は避ける。",
     2),
    ("精神科における「隔離」の実施要件として正しいのはどれか。",
     "医師の指示のもとに治療目的で行い患者の権利に配慮する",
     "看護師の判断で予防的に実施できる",
     "家族の要望があれば医師の指示なく実施できる",
     "患者の同意がなければ絶対に実施できない",
     "精神保健福祉法では12時間を超える隔離には精神保健指定医の指示が必要。隔離は治療目的に限り、日常的な定期的状態確認・環境整備・人権擁護が義務付けられる。",
     2),
    ("アルコール依存症患者の退院支援で最も重要なのはどれか。",
     "自助グループ（断酒会・AA）への参加促進と断酒継続のための環境整備",
     "節酒指導（少量の飲酒を許可する）",
     "家族による24時間の厳格な監視体制の構築",
     "抗酒薬（嫌悪療法）のみによる治療",
     "アルコール依存症の回復目標は「断酒（完全禁酒）」であり節酒ではない。断酒会・AA（Alcoholics Anonymous）などの自助グループへの参加は長期的な断酒継続に有効なエビデンスがある。",
     2),
    ("精神科リハビリテーションにおけるSST（社会生活技能訓練）の目的はどれか。",
     "コミュニケーション能力と社会生活に必要なスキルの習得・強化",
     "薬物療法の効果を増強させること",
     "入院生活に必要な基本的ADLの訓練のみ",
     "認知機能の改善のみを目的とする",
     "SSTはSocial Skills Trainingの略で、社会的スキルを行動療法・ロールプレイで習得する技法。精神症状安定後の地域生活移行支援として有効。対人技術・問題解決能力の向上を目指す。",
     2),
]

# Build questions with balanced answer distribution for 11 questions
TARGET = ['A']*3 + ['B']*3 + ['C']*3 + ['D']*2  # total 11
random.seed(SEED)
random.shuffle(TARGET)

FIELDS = ["老年看護"] * 6 + ["精神看護"] * 5

NEW_QUESTIONS = []
for idx, (question, correct, w1, w2, w3, explanation, stars) in enumerate(RAW_QUESTIONS):
    qid = START_ID + idx
    target_answer = TARGET[idx]
    choices_list = [w1, w2, w3]
    random.seed(SEED + idx)
    random.shuffle(choices_list)
    choices = {}
    wrong_idx = 0
    for opt in ['A', 'B', 'C', 'D']:
        if opt == target_answer:
            choices[opt] = correct
        else:
            choices[opt] = choices_list[wrong_idx]
            wrong_idx += 1
    NEW_QUESTIONS.append({
        "id": qid,
        "category": "一般",
        "field": FIELDS[idx],
        "question": question,
        "choices": choices,
        "answer": target_answer,
        "explanation": explanation,
        "stars": stars
    })

# Verify distribution
from collections import Counter
dist = Counter(q['answer'] for q in NEW_QUESTIONS)
print(f"新規問題数: {len(NEW_QUESTIONS)}, ID: {START_ID}〜{START_ID+len(NEW_QUESTIONS)-1}")
print(f"答え分布: A:{dist['A']} B:{dist['B']} C:{dist['C']} D:{dist['D']}")

# Update HTML file
with open('nursepass_1100.html', 'r', encoding='utf-8') as f:
    content = f.read()
start = content.index('const QUESTIONS = [')
start = content.index('[', start)
depth = 0
for i, c in enumerate(content[start:], start):
    if c == '[': depth += 1
    elif c == ']':
        depth -= 1
        if depth == 0: end = i; break
existing = json.loads(content[start:end+1])
existing = [q for q in existing if not (START_ID <= q['id'] <= END_ID)]
all_questions = existing + NEW_QUESTIONS
new_json = json.dumps(all_questions, ensure_ascii=False, separators=(',', ':'))
new_content = content[:start] + new_json + content[end+1:]
with open('nursepass_1100.html', 'w', encoding='utf-8') as f:
    f.write(new_content)
print(f"✅ バッチ17完了: 合計 {len(all_questions)} 問 (老年看護+6, 精神看護+5)")
