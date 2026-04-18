#!/usr/bin/env python3
"""Apply mobile fix, emoji removal, feedback animation"""

with open('nursepass_1100.html','r',encoding='utf-8') as f:
    html = f.read()

original_len = len(html)

# ===========================
# FIX-0: Subject screen touch-blocking fix
# The position:fixed;inset:0;-webkit-overflow-scrolling:touch creates a WebKit
# native scroll container that intercepts ALL touches even when display:none.
# Fix: add pointer-events:none by default; remove -webkit-overflow-scrolling from CSS
# ===========================
old = ".subject-screen{position:fixed;inset:0;z-index:800;background:linear-gradient(135deg,#F5EFE8 0%,#EDE0D0 50%,#E8D8C8 100%);overflow-y:auto;-webkit-overflow-scrolling:touch}"
new = ".subject-screen{position:fixed;inset:0;z-index:800;background:linear-gradient(135deg,#F5EFE8 0%,#EDE0D0 50%,#E8D8C8 100%);overflow-y:auto;pointer-events:none;display:none}"
assert old in html, "subject-screen CSS not found"
html = html.replace(old, new, 1)
print("✓ subject-screen: removed -webkit-overflow-scrolling, added pointer-events:none")

# Remove the display:none from the HTML element (CSS now handles it)
old = '<div id="subjectScreen" class="subject-screen" style="display:none">'
new = '<div id="subjectScreen" class="subject-screen">'
assert old in html, "subjectScreen HTML not found"
html = html.replace(old, new, 1)
print("✓ subjectScreen: moved display control to CSS")

# Update openSubjectScreen to enable pointer-events
old = """function openSubjectScreen(){
  renderSubjectList();
  document.getElementById('subjectScreen').style.display='block';
  const bn=document.getElementById('bottomNav');
  if(bn) bn.style.display='none';
  document.getElementById('tabHome').style.display='none';
  document.getElementById('tabWeak').style.display='none';
  document.getElementById('tabStats').style.display='none';
  document.getElementById('tabNoa').style.display='none';
}"""
new = """function openSubjectScreen(){
  renderSubjectList();
  const ss=document.getElementById('subjectScreen');
  ss.style.display='block';ss.style.pointerEvents='auto';
  const bn=document.getElementById('bottomNav');
  if(bn) bn.style.display='none';
  document.getElementById('tabHome').style.display='none';
  document.getElementById('tabWeak').style.display='none';
  document.getElementById('tabStats').style.display='none';
  document.getElementById('tabNoa').style.display='none';
}"""
assert old in html, "openSubjectScreen not found"
html = html.replace(old, new, 1)
print("✓ openSubjectScreen: set pointerEvents=auto when shown")

# Update closeSubjectScreen to disable pointer-events
old = """function closeSubjectScreen(){
  document.getElementById('subjectScreen').style.display='none';
  document.getElementById('tabHome').style.display='block';"""
new = """function closeSubjectScreen(){
  const ss=document.getElementById('subjectScreen');
  ss.style.display='none';ss.style.pointerEvents='none';
  document.getElementById('tabHome').style.display='block';"""
assert old in html, "closeSubjectScreen not found"
html = html.replace(old, new, 1)
print("✓ closeSubjectScreen: set pointerEvents=none when hidden")

# ===========================
# FIX-0b: Additional mobile touch robustness
# Add ontouchstart="" body attribute to activate iOS click events
# ===========================
old = '<body>'
new = '<body ontouchstart="">'
assert old in html, "<body> tag not found"
html = html.replace(old, new, 1)
print("✓ body: added ontouchstart='' (iOS click activation)")

# ===========================
# FIX-0c: Add touchstart event delegation in JS
# Ensures click fires on touch devices even if onclick sometimes misses
# ===========================
old = "// iOS touch event fix: ensure buttons receive click events via touchend\n"
# Check if already exists
if old not in html:
    # Find the script end to insert our touch fix
    old2 = "// localStorage fallback: iOS private browsing throws SecurityError on access"
    new2 = """// Mobile touch robustness: dispatch click on touchend for buttons
// Prevents iOS "ghost click" delay and ensures onclick fires reliably
(function(){
  var touched=null;
  document.addEventListener('touchstart',function(e){
    var el=e.target;
    while(el&&el.tagName!=='BUTTON'){el=el.parentElement;}
    touched=el||null;
  },{passive:true,capture:true});
  document.addEventListener('touchend',function(e){
    var el=e.target;
    while(el&&el.tagName!=='BUTTON'){el=el.parentElement;}
    if(el&&el===touched&&!el.disabled){
      var now=Date.now();
      if(!el._t||now-el._t>250){el._t=now;el.click();}
    }
    touched=null;
  },{passive:true,capture:true});
})();
// localStorage fallback: iOS private browsing throws SecurityError on access"""
    assert old2 in html, "localStorage fallback anchor not found"
    html = html.replace(old2, new2, 1)
    print("✓ Touch event delegation added")
else:
    print("✓ Touch event delegation already present")

# ===========================
# FIX-1: Remove emojis from subject card icons (keep ★ for 必修問題)
# ===========================
old = """const SUBJECT_LIST=[
  {key:'all',name:'すべてランダム',icon:'🎲',color:'#B8A090',
   filter:null},
  {key:'hisshu',name:'必修問題',icon:'⭐',color:'#D9A060',
   filter:q=>q.category==='必修'},
  {key:'jintai',name:'人体の構造と機能',icon:'🫀',color:'#5BAD92',
   filter:q=>q.field.includes('人体の構造と機能')||q.field==='解剖生理'||q.field==='栄養・代謝'},
  {key:'shippei',name:'疾病の成り立ちと回復の促進',icon:'🏥',color:'#E07070',
   filter:q=>['疾患別看護','周手術期','救急・クリティカル','薬理・与薬','検査・診断'].includes(q.field)},
  {key:'kenkou',name:'健康支援と社会保障制度',icon:'🏛',color:'#9B59B6',
   filter:q=>q.field.includes('健康支援と社会保障制度')||q.field==='看護倫理・法律'},
  {key:'kiso',name:'基礎看護学',icon:'📋',color:'#5B9BD5',
   filter:q=>q.field.includes('基礎看護')||['コミュニケーション','リハビリ・ADL','感染管理'].includes(q.field)},
  {key:'seijin',name:'成人看護学',icon:'🧑‍⚕️',color:'#E67E22',
   filter:q=>q.field.includes('成人看護')},
  {key:'rounen',name:'老年看護学',icon:'👴',color:'#F5A623',
   filter:q=>q.field.includes('老年看護')},
  {key:'shoni',name:'小児看護学',icon:'👶',color:'#FF7B9C',
   filter:q=>q.field.includes('小児看護')},
  {key:'boshi',name:'母性看護学',icon:'🤱',color:'#C0392B',
   filter:q=>q.field.includes('母性看護')},
  {key:'seishin',name:'精神看護学',icon:'🧠',color:'#8E44AD',
   filter:q=>q.field.includes('精神看護')},
  {key:'zaitan',name:'地域・在宅看護論',icon:'🏡',color:'#27AE60',
   filter:q=>q.field.includes('在宅看護')||q.field==='在宅・地域'},
  {key:'tougou',name:'看護の統合と実践',icon:'🎯',color:'#E74C3C',
   filter:q=>q.field.includes('看護の統合と実践')},
];"""
new = """const SUBJECT_LIST=[
  {key:'all',name:'すべてランダム',icon:'',color:'#B8A090',
   filter:null},
  {key:'hisshu',name:'★ 必修問題',icon:'',color:'#D9A060',
   filter:q=>q.category==='必修'},
  {key:'jintai',name:'人体の構造と機能',icon:'',color:'#5BAD92',
   filter:q=>q.field.includes('人体の構造と機能')||q.field==='解剖生理'||q.field==='栄養・代謝'},
  {key:'shippei',name:'疾病の成り立ちと回復の促進',icon:'',color:'#E07070',
   filter:q=>['疾患別看護','周手術期','救急・クリティカル','薬理・与薬','検査・診断'].includes(q.field)},
  {key:'kenkou',name:'健康支援と社会保障制度',icon:'',color:'#9B59B6',
   filter:q=>q.field.includes('健康支援と社会保障制度')||q.field==='看護倫理・法律'},
  {key:'kiso',name:'基礎看護学',icon:'',color:'#5B9BD5',
   filter:q=>q.field.includes('基礎看護')||['コミュニケーション','リハビリ・ADL','感染管理'].includes(q.field)},
  {key:'seijin',name:'成人看護学',icon:'',color:'#E67E22',
   filter:q=>q.field.includes('成人看護')},
  {key:'rounen',name:'老年看護学',icon:'',color:'#F5A623',
   filter:q=>q.field.includes('老年看護')},
  {key:'shoni',name:'小児看護学',icon:'',color:'#FF7B9C',
   filter:q=>q.field.includes('小児看護')},
  {key:'boshi',name:'母性看護学',icon:'',color:'#C0392B',
   filter:q=>q.field.includes('母性看護')},
  {key:'seishin',name:'精神看護学',icon:'',color:'#8E44AD',
   filter:q=>q.field.includes('精神看護')},
  {key:'zaitan',name:'地域・在宅看護論',icon:'',color:'#27AE60',
   filter:q=>q.field.includes('在宅看護')||q.field==='在宅・地域'},
  {key:'tougou',name:'看護の統合と実践',icon:'',color:'#E74C3C',
   filter:q=>q.field.includes('看護の統合と実践')},
];"""
assert old in html, "SUBJECT_LIST not found"
html = html.replace(old, new, 1)
print("✓ SUBJECT_LIST: emojis removed (★ kept for 必修問題)")

# Also update the subject card rendering to hide icon span when empty
old = """    html+=`<div class="subject-card${isAll?' all-card':''}" onclick="startSubjectQuiz('${subj.key}')">
      <span class="subject-icon">${subj.icon}</span>"""
new = """    html+=`<div class="subject-card${isAll?' all-card':''}" onclick="startSubjectQuiz('${subj.key}')">
      ${subj.icon?`<span class="subject-icon">${subj.icon}</span>`:''}"""
assert old in html, "subject card icon span not found"
html = html.replace(old, new, 1)
print("✓ Subject card: icon span hidden when empty")

# ===========================
# FIX-2: Correct/Incorrect feedback animation
# ===========================

# First add CSS for the animations
feedback_css = """
/* ===== ANSWER FEEDBACK ANIMATIONS ===== */
@keyframes correctZoom{0%{opacity:0;transform:translate(-50%,-50%) scale(.3);}40%{opacity:1;transform:translate(-50%,-50%) scale(1.15);}70%{transform:translate(-50%,-50%) scale(.95);}100%{opacity:1;transform:translate(-50%,-50%) scale(1);}}
@keyframes correctFade{0%{opacity:1;}100%{opacity:0;transform:translate(-50%,-50%) scale(1.1);}}
@keyframes wrongSlide{0%{opacity:0;transform:translateX(-50%) translateY(16px);}30%{opacity:1;transform:translateX(-50%) translateY(0);}80%{opacity:1;}100%{opacity:0;transform:translateX(-50%) translateY(-8px);}}
.answer-feedback-correct{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);font-size:130px;font-weight:900;color:#4CAF50;line-height:1;z-index:9999;pointer-events:none;text-shadow:0 4px 24px rgba(76,175,80,0.35);}
.answer-feedback-wrong{position:fixed;bottom:120px;left:50%;transform:translateX(-50%);font-size:60px;font-weight:700;color:#999999;line-height:1;z-index:9999;pointer-events:none;}
"""

old = "</style>\n</head>"
new = feedback_css + "</style>\n</head>"
assert old in html, "</style></head> not found"
html = html.replace(old, new, 1)
print("✓ Feedback animation CSS added")

# Add the showAnswerFeedback function before answer()
old = "function answer(key){"
new = """function showAnswerFeedback(correct){
  // Remove any existing feedback
  document.querySelectorAll('.answer-feedback-correct,.answer-feedback-wrong').forEach(e=>e.remove());
  const el=document.createElement('div');
  if(correct){
    el.className='answer-feedback-correct';
    el.textContent='◎';
    document.body.appendChild(el);
    // Phase 1: zoom in (0.5s)
    el.style.animation='correctZoom .5s cubic-bezier(.17,.67,.35,1.3) forwards';
    // Phase 2: hold then fade out
    setTimeout(()=>{
      el.style.animation='correctFade .5s ease-in forwards';
      setTimeout(()=>el.remove(),500);
    },1000);
  } else {
    el.className='answer-feedback-wrong';
    el.textContent='×';
    document.body.appendChild(el);
    el.style.animation='wrongSlide .9s ease forwards';
    setTimeout(()=>el.remove(),900);
  }
}
function answer(key){"""
assert "function answer(key){" in html, "answer() not found"
html = html.replace("function answer(key){", new, 1)
print("✓ showAnswerFeedback function added")

# Call showAnswerFeedback from answer() after haptic/sound calls
old = "  haptic(correct);\n  playAnswerSound(correct);"
new = "  haptic(correct);\n  playAnswerSound(correct);\n  showAnswerFeedback(correct);"
assert old in html, "haptic/sound call not found"
html = html.replace(old, new, 1)
print("✓ showAnswerFeedback called from answer()")

# ===========================
# Verify and write
# ===========================
assert 'ontouchstart=""' in html, "body ontouchstart missing"
assert 'pointer-events:none' in html, "pointer-events:none missing"
assert 'showAnswerFeedback' in html, "showAnswerFeedback missing"
assert '★ 必修問題' in html, "★ 必修問題 missing"

print(f"\nOriginal: {original_len} chars")
print(f"New:      {len(html)} chars")
print(f"Delta:    +{len(html)-original_len}")

with open('nursepass_1100.html','w',encoding='utf-8') as f:
    f.write(html)
print("\n✅ All changes written successfully")
