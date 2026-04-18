#!/usr/bin/env python3
"""Round 44: Simplified home screen + gachi auto-next"""

with open('nursepass_1100.html', 'r', encoding='utf-8') as f:
    html = f.read()

original_len = len(html)

# ========== 1. ADD CSS for new home layout ==========
new_css = """
/* HOME SIMPLE */
.home-main-btn{width:100%;padding:22px;background:linear-gradient(135deg,#D9C5B2,#B8A090);color:white;border:none;border-radius:20px;font-size:20px;font-weight:700;cursor:pointer;font-family:'Noto Sans JP',sans-serif;box-shadow:0 6px 24px rgba(184,160,144,.35);letter-spacing:.02em;transition:.15s;text-align:center}
.home-main-btn:active{transform:scale(.98);opacity:.92}
.home-mid-btn{padding:18px 12px;background:linear-gradient(135deg,rgba(245,239,232,0.98),rgba(237,224,212,0.95));border:1.5px solid rgba(217,197,178,0.6);border-radius:18px;cursor:pointer;font-family:'Noto Sans JP',sans-serif;display:flex;flex-direction:column;align-items:center;gap:6px;box-shadow:0 2px 8px rgba(184,160,144,.1);transition:.15s;width:100%}
.home-mid-btn:active{transform:scale(.97)}
.home-mid-btn .btn-icon{font-size:22px;line-height:1}
.home-mid-btn .btn-lbl{font-size:16px;font-weight:700;color:#4A3828}
"""

old_css_end = "\n/* BOTTOM NAV */"
assert old_css_end in html, "CSS anchor not found"
html = html.replace(old_css_end, new_css + "\n/* BOTTOM NAV */", 1)
print("✓ home CSS added")

# ========== 2. Remove hapticBtn from nav ==========
old_nav = """      <button onclick="toggleHaptic()" id="hapticBtn" title="バイブレーション" style="background:none;border:none;cursor:pointer;font-size:16px;padding:2px 4px;line-height:1;border-radius:8px;opacity:0.6">📳</button>
      """
new_nav = """      """
assert old_nav in html, "hapticBtn not found"
html = html.replace(old_nav, new_nav, 1)
print("✓ hapticBtn removed from nav")

# ========== 3. Replace #tabHome content ==========
old_home = """  <div id="tabHome">
    <!-- モード切替スイッチ -->
    <div class="mode-switch-wrap" id="modeSwitchBar">
      <button class="mode-switch-btn active hikari" id="modeBtnHikari" onclick="setQuizMode('hikari')">🌸 ヒカリモード</button>
      <button class="mode-switch-btn gachi" id="modeBtnGachi" onclick="setQuizMode('gachi')">⚡ ガチモード</button>
    </div>
    <!-- ヒカリのひとこと: 1行コンパクトバナー -->
    <div id="hikariHintBar" style="background:rgba(255,255,255,0.82);border:1.5px solid rgba(217,197,178,0.5);border-radius:14px;padding:9px 16px;margin-bottom:10px;display:flex;align-items:center;gap:10px">
      <span style="font-size:16px;flex-shrink:0">🌸</span>
      <span id="hikariHintText" style="font-size:12px;color:#4A3828;font-weight:500;line-height:1.4;flex:1"></span>
    </div>
    <!-- カテゴリ選択タブ（最上部に移動） -->
    <div class="sub-tabs" style="margin-bottom:10px">
      <button class="sub-tab active" data-cat="必修" onclick="selectCategory('必修')">必修<span class="cat-count" id="catCount必修"></span></button>
      <button class="sub-tab" data-cat="一般" onclick="selectCategory('一般')">一般<span class="cat-count" id="catCount一般"></span></button>
      <button class="sub-tab" data-cat="状況設定" onclick="selectCategory('状況設定')">状況設定<span class="cat-count" id="catCount状況設定"></span></button>
    </div>
    <!-- クイックスタートグリッド: スクロールなしで全ボタン表示 -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:8px">
      <button onclick="startQuizWithCount('random',5)" style="padding:16px 12px;background:linear-gradient(135deg,rgba(245,239,232,0.98),rgba(237,224,212,0.95));border:1.5px solid rgba(217,197,178,0.6);border-radius:18px;cursor:pointer;text-align:left;font-family:'Noto Sans JP',sans-serif;display:flex;align-items:center;gap:10px;box-shadow:0 2px 8px rgba(184,160,144,.1)">
        <span style="font-size:24px">🎲</span>
        <div><div style="font-size:14px;font-weight:700;color:#4A3828">ランダム5問</div><div style="font-size:10px;color:#8A6A50;margin-top:2px">まず一問から</div></div>
      </button>
      <button onclick="pickCount('field','分野別')" style="padding:16px 12px;background:linear-gradient(135deg,rgba(245,239,232,0.98),rgba(237,224,212,0.95));border:1.5px solid rgba(217,197,178,0.6);border-radius:18px;cursor:pointer;text-align:left;font-family:'Noto Sans JP',sans-serif;display:flex;align-items:center;gap:10px;box-shadow:0 2px 8px rgba(184,160,144,.1)">
        <span style="font-size:24px">📖</span>
        <div><div style="font-size:14px;font-weight:700;color:#4A3828">分野別</div><div style="font-size:10px;color:#8A6A50;margin-top:2px">得意・苦手を選んで</div></div>
      </button>
      <button onclick="startQuiz('weak')" style="padding:16px 12px;background:linear-gradient(135deg,rgba(255,245,245,0.98),rgba(255,235,230,0.9));border:1.5px solid rgba(248,113,113,0.3);border-radius:18px;cursor:pointer;text-align:left;font-family:'Noto Sans JP',sans-serif;display:flex;align-items:center;gap:10px;box-shadow:0 2px 8px rgba(248,113,113,.08)">
        <span style="font-size:24px">💪</span>
        <div><div style="font-size:14px;font-weight:700;color:#4A3828">苦手強化</div><div style="font-size:10px;color:#8A6A50;margin-top:2px">間違えた問題だけ</div></div>
      </button>
      <button onclick="startMainExam()" style="padding:16px 12px;background:linear-gradient(135deg,rgba(240,247,255,0.98),rgba(219,234,254,0.9));border:1.5px solid rgba(59,130,246,0.3);border-radius:18px;cursor:pointer;text-align:left;font-family:'Noto Sans JP',sans-serif;display:flex;align-items:center;gap:10px;box-shadow:0 2px 8px rgba(59,130,246,.08)">
        <span style="font-size:24px">📝</span>
        <div><div style="font-size:14px;font-weight:700;color:#4A3828">本番形式</div><div style="font-size:10px;color:#8A6A50;margin-top:2px" id="mainExamDesc">50問チャレンジ</div></div>
      </button>
    </div>
    <!-- 暗記カードボタン (full width) -->
    <button onclick="showFlashCards()" style="width:100%;padding:12px 16px;background:linear-gradient(135deg,rgba(253,242,255,0.92),rgba(245,232,255,0.82));border:1.5px solid rgba(200,170,230,0.4);border-radius:16px;cursor:pointer;font-family:'Noto Sans JP',sans-serif;display:flex;align-items:center;gap:12px;margin-bottom:14px;box-shadow:0 2px 8px rgba(180,120,220,.08)">
      <span style="font-size:22px">🃏</span>
      <div style="text-align:left"><div style="font-size:13px;font-weight:700;color:#4A3050">暗記カード</div><div style="font-size:10px;color:#7B5090;margin-top:2px">検査値・薬物・看護技術などを用語カードで確認</div></div>
    </button>
    <!-- 統計サマリー（クイックボタンの下） -->
    <div class="home-summary">
      <div class="summary-card" onclick="showStreakDetail()"><div class="summary-val" id="streakDisp">0</div><div class="summary-lbl">🔥 連続学習日<span id="bestStreakLbl" style="display:block;font-size:9px;color:#aaa;margin-top:1px"></span></div></div>
      <div class="summary-card"><div class="summary-val" id="todayDisp">0</div><div class="summary-lbl">📝 今日の問題数</div></div>
      <div class="summary-card" onclick="showCoverageModal()" style="cursor:pointer"><div class="summary-val" id="coverDisp">0%</div><div class="summary-lbl">✅ カバー率<span style="display:block;font-size:9px;color:#aaa;margin-top:1px">タップで内訳</span></div></div>
      <div class="summary-card"><div class="summary-val" id="studyTimeDisp" style="font-size:16px">0分</div><div class="summary-lbl">⏱ 今日の学習時間<span id="accDeltaDisp" style="display:block;margin-top:2px"></span></div></div>
      <div class="summary-card" onclick="showPassScoreDetail()" style="grid-column:1/-1;background:linear-gradient(135deg,rgba(245,239,232,0.9),rgba(237,224,212,0.8));cursor:pointer"><div class="summary-val" id="passScoreDisp" style="font-size:22px">--</div><div class="summary-lbl">🎯 合格予測スコア<span class="pass-lbl-sub" style="display:block;font-size:9px;margin-top:2px"></span></div><div id="passScoreBreakdown" style="display:none;margin-top:8px;text-align:left;font-size:10px"></div></div>
    </div>
    <div style="text-align:center;font-size:12px;margin-bottom:10px" id="examCountdown"></div>
    <div id="passGaugeCard" style="margin-bottom:10px"></div>
    <div id="noaCard" style="margin-bottom:10px"></div>
    <div id="dailyTipCard" style="margin-bottom:10px"></div>
    <div style="background:rgba(255,255,255,0.85);border:1px solid rgba(85,80,77,0.15);border-radius:14px;padding:10px 14px;margin-bottom:10px" id="goalBar"></div>
    <div id="pomodoroWidget" style="margin-bottom:10px"></div>
    <div id="todayPlanCard" style="margin-bottom:10px"></div>
    <div id="questionOfDayCard" style="margin-bottom:10px"></div>
    <div id="miniReviewCard" style="margin-bottom:10px"></div>
    <div id="todayTimelineCard" style="margin-bottom:10px"></div>
    <div class="search-wrap">
      <span style="font-size:16px;color:#aaa">🔍</span>
      <input class="search-input" id="searchInput" placeholder="キーワード検索 / #123でID直接検索" oninput="onSearchInput(this.value)" autocomplete="off">
      <button onclick="clearSearch()" style="background:none;border:none;color:#aaa;font-size:14px;cursor:pointer;padding:2px 4px;display:none" id="searchClear">✕</button>
    </div>
    <div id="searchPresetChips" style="display:flex;flex-wrap:wrap;gap:5px;margin-bottom:10px"></div>
    <div class="search-results" id="searchResults"></div>
    <div id="weakFieldQuick" style="margin-bottom:10px"></div>
    <div id="dailyBanner" style="margin-bottom:10px"></div>
    <!-- 本番模擬試験ボタン（下部に移動） -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px">
      <button onclick="startQuiz('mock')" style="padding:14px 12px;background:linear-gradient(135deg,#6B5040,#8A6A50);color:white;border:none;border-radius:18px;font-size:13px;font-weight:700;cursor:pointer;font-family:'Noto Sans JP',sans-serif;box-shadow:0 4px 16px rgba(107,80,64,0.3);display:flex;align-items:center;justify-content:center;gap:8px">
        <span style="font-size:18px">📝</span>
        <div style="text-align:left"><div>本番模擬試験</div><div style="font-size:10px;font-weight:400;opacity:0.85">125問（120分）</div></div>
      </button>
      <button onclick="startQuiz('minimock')" style="padding:14px 12px;background:linear-gradient(135deg,#4A7A90,#5A8FAA);color:white;border:none;border-radius:18px;font-size:13px;font-weight:700;cursor:pointer;font-family:'Noto Sans JP',sans-serif;box-shadow:0 4px 16px rgba(74,122,144,0.3);display:flex;align-items:center;justify-content:center;gap:8px">
        <span style="font-size:18px">⚡</span>
        <div style="text-align:left"><div>ミニ模擬試験</div><div style="font-size:10px;font-weight:400;opacity:0.85">25問（30分）</div></div>
      </button>
    </div>
    <!-- 全モード・分野選択 -->
    <div class="card">
      <div style="padding:10px 16px 4px;font-size:11px;font-weight:700;color:#8A6A50;letter-spacing:.04em">▸ 全モード・分野選択</div>
      <div class="field-select">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
          <div class="field-label" style="margin-bottom:0">▸ 分野を選ぶ（複数選択可・未選択で全分野）</div>
          <button onclick="toggleSkipMastered()" class="skip-mastered-btn" style="padding:3px 9px;background:rgba(240,232,222,0.8);border:1px solid rgba(85,80,77,0.2);border-radius:10px;font-size:10px;color:#8A6A50;cursor:pointer;font-family:'Noto Sans JP',sans-serif;white-space:nowrap">⬜ 習得済みも出題</button>
        </div>
        <div class="field-chips" id="fieldChips"></div>
      </div>
      <div id="sessionGoalBar" style="margin-bottom:8px;display:flex;align-items:center;gap:5px;flex-wrap:wrap"></div>
      <div class="mode-grid" id="modeGrid"></div>
    </div>
  </div>"""

new_home = """  <div id="tabHome">
    <!-- エリア2: ヒカリのひとこと -->
    <div id="hikariHintBar" style="background:rgba(255,255,255,0.82);border:1.5px solid rgba(217,197,178,0.5);border-radius:14px;padding:10px 16px;margin-bottom:12px;display:flex;align-items:center;gap:10px">
      <span style="font-size:18px;flex-shrink:0">🌸</span>
      <span id="hikariHintText" style="font-size:13px;color:#4A3828;font-weight:500;line-height:1.4;flex:1"></span>
    </div>
    <!-- エリア3: モード切替 -->
    <div class="mode-switch-wrap" id="modeSwitchBar" style="margin-bottom:18px">
      <button class="mode-switch-btn active hikari" id="modeBtnHikari" onclick="setQuizMode('hikari')">🌸 やさしく</button>
      <button class="mode-switch-btn gachi" id="modeBtnGachi" onclick="setQuizMode('gachi')">⚡ ガチ</button>
    </div>
    <!-- エリア4: メインボタン -->
    <div style="display:flex;flex-direction:column;gap:12px">
      <button onclick="startQuizWithCount('random',5)" class="home-main-btn">▶ 今日の5問を始める</button>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
        <button onclick="pickCount('field','分野別')" class="home-mid-btn">
          <span class="btn-icon">📚</span><span class="btn-lbl">分野別</span>
        </button>
        <button onclick="startQuiz('weak')" class="home-mid-btn" style="background:linear-gradient(135deg,rgba(255,245,245,0.98),rgba(255,235,230,0.9));border-color:rgba(248,113,113,0.35)">
          <span class="btn-icon">⚠️</span><span class="btn-lbl">苦手強化</span>
        </button>
      </div>
      <!-- カテゴリタブ -->
      <div class="sub-tabs" style="padding:0;margin-top:2px">
        <button class="sub-tab active" data-cat="必修" onclick="selectCategory('必修')">必修<span class="cat-count" id="catCount必修"></span></button>
        <button class="sub-tab" data-cat="一般" onclick="selectCategory('一般')">一般<span class="cat-count" id="catCount一般"></span></button>
        <button class="sub-tab" data-cat="状況設定" onclick="selectCategory('状況設定')">状況設定<span class="cat-count" id="catCount状況設定"></span></button>
      </div>
    </div>
    <!-- 非表示: JS用レガシーID群 -->
    <div style="display:none">
      <span id="streakDisp"></span><span id="todayDisp"></span><span id="coverDisp"></span>
      <span id="studyTimeDisp"></span><span id="passScoreDisp"></span>
      <span id="bestStreakLbl"></span><span id="accDeltaDisp"></span><span id="passScoreBreakdown"></span>
      <div id="examCountdown"></div><div id="passGaugeCard"></div><div id="noaCard"></div>
      <div id="dailyTipCard"></div><div id="goalBar"></div><div id="pomodoroWidget"></div>
      <div id="todayPlanCard"></div><div id="questionOfDayCard"></div><div id="miniReviewCard"></div>
      <div id="todayTimelineCard"></div><div id="searchPresetChips"></div>
      <div id="searchResults"></div><div id="weakFieldQuick"></div><div id="dailyBanner"></div>
      <div id="fieldChips"></div><div id="sessionGoalBar"></div>
      <span id="mainExamDesc"></span>
      <div class="mode-grid" id="modeGrid"></div>
    </div>
  </div>"""

assert old_home in html, "tabHome content not found"
html = html.replace(old_home, new_home, 1)
print("✓ tabHome replaced with simple layout")

# ========== 4. Fix initChips() null check ==========
old_chips = "function initChips(){\n  const c=document.getElementById('fieldChips');\n  c.innerHTML='';"
new_chips = "function initChips(){\n  const c=document.getElementById('fieldChips');\n  if(!c) return;\n  c.innerHTML='';"
assert old_chips in html, "initChips not found"
html = html.replace(old_chips, new_chips, 1)
print("✓ initChips null check added")

# ========== 5. Fix initModeButtons() null check ==========
old_mg = "function initModeButtons(){\n  renderDailyBanner();\n  const mg=document.getElementById('modeGrid');"
new_mg = "function initModeButtons(){\n  renderDailyBanner();\n  const mg=document.getElementById('modeGrid');\n  if(!mg) return;"
assert old_mg in html, "initModeButtons not found"
html = html.replace(old_mg, new_mg, 1)
print("✓ initModeButtons null check added")

# ========== 6. Fix showResumeBanner() insert point ==========
# Change to insert at top of #tabHome instead of before #modeGrid
old_resume = """  const mg=document.getElementById('modeGrid');
  if(mg&&mg.parentNode) mg.parentNode.insertBefore(banner,mg);
}"""
new_resume = """  const th=document.getElementById('tabHome');
  if(th) th.insertBefore(banner,th.firstChild);
}"""
assert old_resume in html, "showResumeBanner insert not found"
html = html.replace(old_resume, new_resume, 1)
print("✓ showResumeBanner insert point fixed")

# ========== 7. ガチモード: auto-advance after answer ==========
old_gachi = """  if(quizMode==='gachi'){
    // ガチモード: シンプル大ボタン（5問区切りなし）
    const nb=document.createElement('button');
    nb.className='gachi-next-btn';nb.id='nextBtn';
    nb.textContent=(isLast||streak10End)?'結果 →':'→';
    nb.onclick=(isLast||streak10End)?finishQuiz:nextQ;
    res.after(nb);
    // 画面タップでも次へ
    nb.addEventListener('touchstart',()=>{},{ passive:true });
  }"""
new_gachi = """  if(quizMode==='gachi'){
    // ガチモード: 最終問題はボタン、それ以外は自動送り
    const isLastQ=isLast||streak10End;
    const nb=document.createElement('button');
    nb.className='gachi-next-btn';nb.id='nextBtn';
    if(isLastQ){
      nb.textContent='結果を見る →';
      nb.onclick=finishQuiz;
      nb.style.background=correct?'linear-gradient(135deg,#16a34a,#15803d)':'linear-gradient(135deg,#dc2626,#b91c1c)';
      res.after(nb);
    } else {
      // 自動送り: 正解1.5秒、不正解2.5秒
      let gachiRemain=correct?1.5:2.5;
      nb.style.background=correct?'linear-gradient(135deg,#16a34a,#15803d)':'linear-gradient(135deg,#dc2626,#b91c1c)';
      nb.textContent=`次へ (${gachiRemain.toFixed(1)})`;
      nb.onclick=()=>{if(autoAdvanceTimer){clearInterval(autoAdvanceTimer);autoAdvanceTimer=null;}nextQ();};
      res.after(nb);
      autoAdvanceTimer=setInterval(()=>{
        gachiRemain-=0.1;
        if(gachiRemain<=0){clearInterval(autoAdvanceTimer);autoAdvanceTimer=null;nextQ();return;}
        const btn2=document.getElementById('nextBtn');
        if(btn2) btn2.textContent=`次へ (${gachiRemain.toFixed(1)})`;
      },100);
    }
  }"""
assert old_gachi in html, "gachi mode block not found"
html = html.replace(old_gachi, new_gachi, 1)
print("✓ gachi mode auto-advance added")

# ========== 8. Remove logo-sub "のあ先生" reference if any, update to clean style ==========
# Also simplify nav: remove font size btn and dark btn to keep only logo+rate
# Actually user didn't ask to remove those - keep dark/font btns, just remove haptic (already done)

# ========== 9. Update sub-tab padding (remove default padding since we set padding:0 in new home) ==========
# The sub-tabs have padding:12px 16px 8px in CSS, we override inline - that's fine

# ========== 10. Make body use 100vh layout properly ==========
# The wrap has padding:16px and padding-bottom:80px
# Nav is about 50px, hint ~44px, mode ~36px, main area ~180px = ~310px total
# Should fit on mobile screens (667px+)

print(f"\nOriginal: {original_len}, New: {len(html)}, Delta: {len(html)-original_len:+d}")

with open('nursepass_1100.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("✅ Written to nursepass_1100.html")
