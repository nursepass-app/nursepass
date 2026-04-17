#!/usr/bin/env python3
"""Round 43: Bottom navigation + UI improvements (看護roo style)"""

with open('nursepass_1100.html','r',encoding='utf-8') as f:
    html = f.read()

original_len = len(html)

# ===========================
# 1. Add padding-bottom to body CSS
# ===========================
old = "body{min-height:100vh;background:linear-gradient(135deg,#F5EFE8 0%,#EDE0D0 50%,#E8D8C8 100%);font-family:'Noto Sans JP',sans-serif;padding:16px;position:relative;overflow-x:hidden}"
new = "body{min-height:100vh;background:linear-gradient(135deg,#F5EFE8 0%,#EDE0D0 50%,#E8D8C8 100%);font-family:'Noto Sans JP',sans-serif;padding:16px;padding-bottom:80px;position:relative;overflow-x:hidden}"
assert old in html, "body CSS not found"
html = html.replace(old, new, 1)
print("✓ body padding-bottom added")

# ===========================
# 2. Add bottom nav CSS before </style>
# ===========================
bottom_nav_css = """
/* BOTTOM NAV */
.bottom-nav{position:fixed;bottom:0;left:0;right:0;z-index:999;background:rgba(255,252,248,0.97);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border-top:1px solid rgba(217,197,178,0.4);display:flex;justify-content:space-around;align-items:stretch;height:62px;box-shadow:0 -2px 16px rgba(184,160,144,.15)}
.bn-btn{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;background:none;border:none;cursor:pointer;font-family:'Noto Sans JP',sans-serif;padding:6px 4px;transition:.2s;position:relative}
.bn-icon{font-size:20px;line-height:1;transition:.2s}
.bn-label{font-size:10px;color:#8A7A70;font-weight:500;transition:.2s}
.bn-btn.active .bn-icon{transform:scale(1.1)}
.bn-btn.active .bn-label{color:#8A6A50;font-weight:700}
.bn-btn.active::after{content:'';position:absolute;top:0;left:50%;transform:translateX(-50%);width:32px;height:3px;background:linear-gradient(135deg,#D9C5B2,#B8A090);border-radius:0 0 4px 4px}
.bn-badge{position:absolute;top:4px;right:calc(50% - 18px);background:#ef4444;color:white;font-size:9px;font-weight:700;border-radius:10px;padding:1px 5px;min-width:16px;text-align:center;line-height:1.4}
"""

old = "</style>\n</head>"
new = bottom_nav_css + "</style>\n</head>"
assert old in html, "</style></head> not found"
html = html.replace(old, new, 1)
print("✓ bottom nav CSS added")

# ===========================
# 3. Remove top .tabs div
# ===========================
old = """
  <div class="tabs">
    <button class="tab active" onclick="switchTab('home')" id="tabBtnHome">ホーム</button>
    <button class="tab" onclick="switchTab('weak')" id="tabBtnWeak">苦手</button>
    <button class="tab" onclick="switchTab('stats')" id="tabBtnStats">記録</button>
    <button class="tab" onclick="switchTab('noa')" style="color:#8A6A50;font-weight:700" id="tabBtnNoa">ヒカリ</button>
  </div>
"""
new = "\n"
assert old in html, "top tabs div not found"
html = html.replace(old, new, 1)
print("✓ top tabs removed")

# ===========================
# 4. Add bottom nav HTML (before closing </div> of .wrap + before modal)
# ===========================
old = """  <div id="quizArea" style="display:none;margin-top:0"></div>
  <div id="jokyoArea" style="display:none;margin-top:0"></div>
  <div id="flashArea" style="display:none;margin-top:0"></div>
</div>"""
new = """  <div id="quizArea" style="display:none;margin-top:0"></div>
  <div id="jokyoArea" style="display:none;margin-top:0"></div>
  <div id="flashArea" style="display:none;margin-top:0"></div>
</div>
<nav class="bottom-nav" id="bottomNav">
  <button class="bn-btn active" data-tab="home" onclick="switchTab('home')">
    <span class="bn-icon">🏠</span><span class="bn-label">ホーム</span>
  </button>
  <button class="bn-btn" data-tab="weak" onclick="switchTab('weak')">
    <span class="bn-icon">📚</span><span class="bn-label">復習</span>
    <span class="bn-badge" id="bnWeakBadge" style="display:none"></span>
  </button>
  <button class="bn-btn" data-tab="stats" onclick="switchTab('stats')">
    <span class="bn-icon">📊</span><span class="bn-label">記録</span>
  </button>
  <button class="bn-btn" data-tab="noa" onclick="switchTab('noa')">
    <span class="bn-icon">✨</span><span class="bn-label">ヒカリ</span>
  </button>
</nav>"""
assert old in html, "wrap closing div not found"
html = html.replace(old, new, 1)
print("✓ bottom nav HTML added")

# ===========================
# 5. Update switchTab() to use .bn-btn
# ===========================
old = """  document.querySelectorAll('.tab').forEach((b,i)=>{
    b.classList.toggle('active',['home','weak','stats','noa'][i]===t);
  });"""
new = """  document.querySelectorAll('.bn-btn').forEach(b=>{
    b.classList.toggle('active',b.dataset.tab===t);
  });
  const bn=document.getElementById('bottomNav');
  if(bn) bn.style.display='';"""
assert old in html, "switchTab .tab forEach not found"
html = html.replace(old, new, 1)
print("✓ switchTab updated")

# ===========================
# 6. Update endFlash() .tab reference
# ===========================
old = "  document.querySelectorAll('.tab').forEach((b,i)=>b.classList.toggle('active',i===0));\n  document.querySelectorAll('.sub-tab').forEach(b=>{\n    b.classList.toggle('active',b.dataset.cat===currentCategory);\n  });\n  renderHomeSummary();\n  renderExamCountdown();\n  renderGoalBar();renderNoaCard();"
new = "  document.querySelectorAll('.bn-btn').forEach(b=>b.classList.toggle('active',b.dataset.tab==='home'));\n  const bn_ef=document.getElementById('bottomNav');\n  if(bn_ef) bn_ef.style.display='';\n  document.querySelectorAll('.sub-tab').forEach(b=>{\n    b.classList.toggle('active',b.dataset.cat===currentCategory);\n  });\n  renderHomeSummary();\n  renderExamCountdown();\n  renderGoalBar();renderNoaCard();"
assert old in html, "endFlash .tab forEach not found"
html = html.replace(old, new, 1)
print("✓ endFlash updated")

# ===========================
# 7. Update quiz start: hide bottom nav + remove tab active
# ===========================
old = "  document.querySelectorAll('.tab').forEach(b=>b.classList.remove('active'));\n  const qa=document.getElementById('quizArea');\n  qa.style.display='block';"
new = "  document.querySelectorAll('.bn-btn').forEach(b=>b.classList.remove('active'));\n  const bn_qs=document.getElementById('bottomNav');\n  if(bn_qs) bn_qs.style.display='none';\n  const qa=document.getElementById('quizArea');\n  qa.style.display='block';"
assert old in html, "quiz start .tab forEach not found"
html = html.replace(old, new, 1)
print("✓ quiz start (showQuiz) updated")

# ===========================
# 8. Update end quiz (goHome) .tab reference
# ===========================
old = """  document.getElementById('quizArea').style.display='none';
  document.getElementById('jokyoArea').style.display='none';
  document.getElementById('flashArea').style.display='none';
  document.getElementById('tabHome').style.display='block';
  document.querySelectorAll('.tab').forEach((b,i)=>b.classList.toggle('active',i===0));
  document.querySelectorAll('.sub-tab').forEach(b=>{
    b.classList.toggle('active',b.dataset.cat===currentCategory);
  });
  renderHomeSummary();
  renderExamCountdown();
  renderGoalBar();renderNoaCard();
  initModeButtons();
}"""
new = """  document.getElementById('quizArea').style.display='none';
  document.getElementById('jokyoArea').style.display='none';
  document.getElementById('flashArea').style.display='none';
  document.getElementById('tabHome').style.display='block';
  document.querySelectorAll('.bn-btn').forEach(b=>b.classList.toggle('active',b.dataset.tab==='home'));
  const bn_gh=document.getElementById('bottomNav');
  if(bn_gh) bn_gh.style.display='';
  document.querySelectorAll('.sub-tab').forEach(b=>{
    b.classList.toggle('active',b.dataset.cat===currentCategory);
  });
  renderHomeSummary();
  renderExamCountdown();
  renderGoalBar();renderNoaCard();
  initModeButtons();
}"""
assert old in html, "goHome .tab forEach not found"
html = html.replace(old, new, 1)
print("✓ goHome updated")

# ===========================
# 9. Update field drill tab references
# ===========================
old = """  // Switch to home tab first
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.getElementById('tabHome').style.display='';
  document.getElementById('tabWeak').style.display='none';
  document.getElementById('tabStats').style.display='none';
  document.getElementById('tabNoa').style.display='none';"""
new = """  // Switch to home tab first
  document.querySelectorAll('.bn-btn').forEach(b=>b.classList.remove('active'));
  const bn_fd=document.getElementById('bottomNav');
  if(bn_fd) bn_fd.style.display='none';
  document.getElementById('tabHome').style.display='';
  document.getElementById('tabWeak').style.display='none';
  document.getElementById('tabStats').style.display='none';
  document.getElementById('tabNoa').style.display='none';"""
assert old in html, "field drill .tab forEach not found"
html = html.replace(old, new, 1)
print("✓ field drill updated")

# ===========================
# 10. Update startJokyoMode() .tab references
# ===========================
old = """  var tabs=document.querySelectorAll('.tab');
  for(var i=0;i<tabs.length;i++)tabs[i].classList.remove('active');
  document.getElementById('tabHome').style.display='none';"""
new = """  document.querySelectorAll('.bn-btn').forEach(function(b){b.classList.remove('active');});
  var bn_jm=document.getElementById('bottomNav');
  if(bn_jm) bn_jm.style.display='none';
  document.getElementById('tabHome').style.display='none';"""
assert old in html, "startJokyoMode .tab not found"
html = html.replace(old, new, 1)
print("✓ startJokyoMode updated")

# ===========================
# 11. Update endJok() .tab reference
# ===========================
old = """  document.getElementById('jokyoArea').style.display='none';
  document.getElementById('tabHome').style.display='block';
  document.querySelectorAll('.tab').forEach((b,i)=>b.classList.toggle('active',i===0));
  document.querySelectorAll('.sub-tab').forEach(b=>{
    b.classList.toggle('active',b.dataset.cat===currentCategory);
  });
}"""
new = """  document.getElementById('jokyoArea').style.display='none';
  document.getElementById('tabHome').style.display='block';
  document.querySelectorAll('.bn-btn').forEach(b=>b.classList.toggle('active',b.dataset.tab==='home'));
  const bn_ej=document.getElementById('bottomNav');
  if(bn_ej) bn_ej.style.display='';
  document.querySelectorAll('.sub-tab').forEach(b=>{
    b.classList.toggle('active',b.dataset.cat===currentCategory);
  });
}"""
assert old in html, "endJok .tab not found"
html = html.replace(old, new, 1)
print("✓ endJok updated")

# ===========================
# 12. Update weak badge render: add badge to bottom nav
# ===========================
# Find renderWeak or the badge logic. Let's add a helper after renderWeak() call
# We'll add updateBnWeakBadge() call inside renderWeak()
# First find where renderWeak is defined
old = "function renderWeak(){"
new = """function updateBnWeakBadge(){
  try{
    const h=JSON.parse(localStorage.getItem('np_history')||'{}');
    const wrongCount=QUESTIONS.filter(q=>h[String(q.id)]&&h[String(q.id)].wrong>0&&!isMastered(String(q.id))).length;
    const el=document.getElementById('bnWeakBadge');
    if(el){el.textContent=wrongCount>99?'99+':String(wrongCount);el.style.display=wrongCount>0?'':'none';}
  }catch(e){}
}
function renderWeak(){"""
assert old in html, "renderWeak function not found"
html = html.replace(old, new, 1)
print("✓ updateBnWeakBadge helper added")

# ===========================
# 13. Call updateBnWeakBadge in switchTab when tab='weak'
# ===========================
old = "  if(t==='weak') renderWeak();\n  if(t==='stats') renderStats();\n  if(t==='noa') initChat();"
new = "  if(t==='weak'){renderWeak();updateBnWeakBadge();}\n  if(t==='stats') renderStats();\n  if(t==='noa') initChat();"
assert old in html, "switchTab if(weak) not found"
html = html.replace(old, new, 1)
print("✓ switchTab weak badge update added")

# ===========================
# 14. Call updateBnWeakBadge in DOMContentLoaded
# ===========================
old = "  renderHomeSummary();"
# Find DOMContentLoaded context - look for the first occurrence of renderHomeSummary
idx = html.find("document.addEventListener('DOMContentLoaded'")
idx2 = html.find("renderHomeSummary();", idx)
if idx2 > 0 and idx2 < idx + 5000:
    old_ctx = "  renderHomeSummary();"
    # We'll add the call after renderHomeSummary in the DOMContentLoaded section
    # Find specifically in DOMContentLoaded
    dom_section = html[idx:idx+5000]
    if "renderHomeSummary();" in dom_section:
        # Replace the first occurrence after DOMContentLoaded
        prefix = html[:idx]
        suffix = html[idx:]
        suffix = suffix.replace("  renderHomeSummary();", "  renderHomeSummary();\n  updateBnWeakBadge();", 1)
        html = prefix + suffix
        print("✓ updateBnWeakBadge called on load")
    else:
        print("! could not find renderHomeSummary in DOMContentLoaded - skipping")
else:
    print("! DOMContentLoaded not found near renderHomeSummary - skipping")

# ===========================
# 15. Add margin-bottom to .nav so content doesn't crowd bottom nav
# ===========================
old = ".nav{display:flex;align-items:center;gap:10px;padding:12px 0 16px}"
new = ".nav{display:flex;align-items:center;gap:10px;padding:12px 0 12px}"
assert old in html, "nav CSS not found"
html = html.replace(old, new, 1)
print("✓ nav padding adjusted")

# ===========================
# 16. Remove .tabs CSS (no longer needed, but harmless to keep - just hide)
# ===========================
# Let's just hide it to avoid any visual artifacts
old = ".tabs{display:flex;gap:6px;margin-bottom:16px;background:rgba(255,255,255,0.82);border-radius:16px;padding:4px}"
new = ".tabs{display:none}"
assert old in html, "tabs CSS not found"
html = html.replace(old, new, 1)
print("✓ old .tabs CSS hidden")

# ===========================
# Verify final length
# ===========================
print(f"\nOriginal length: {original_len}")
print(f"New length: {len(html)}")
print(f"Delta: +{len(html)-original_len}")

with open('nursepass_1100.html','w',encoding='utf-8') as f:
    f.write(html)
print("\n✅ All changes written to nursepass_1100.html")
