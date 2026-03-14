import base64, os

def _logo_b64():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
    try:
        with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

_B64     = _logo_b64()
LOGO_IMG = f'<img src="data:image/png;base64,{_B64}" alt="11%" style="height:36px;width:auto;">' if _B64 else '<span style="font-family:\'Bebas Neue\',sans-serif;font-size:1.6rem;color:#4ade80;letter-spacing:0.05em;">11%</span>'
LOGO_B64 = _B64

PLOTLY_THEME = dict(
    paper_bgcolor="#0d0f11",
    plot_bgcolor="#0d0f11",
    font=dict(family="IBM Plex Mono", color="#4b5563", size=11),
    xaxis=dict(gridcolor="#1a1e24", linecolor="#1f2530", zerolinecolor="#1f2530"),
    yaxis=dict(gridcolor="#1a1e24", linecolor="#1f2530", zerolinecolor="#1f2530"),
    margin=dict(l=48, r=16, t=40, b=40),
)

SHARED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Bebas+Neue&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');

:root {
  --green:      #4ade80;
  --green2:     #22c55e;
  --green3:     #16a34a;
  --red:        #f87171;
  --red2:       #ef4444;
  --blue:       #60a5fa;
  --yellow:     #fbbf24;
  --purple:     #a78bfa;
  --bg:         #0d0f11;
  --bg2:        #12151a;
  --bg3:        #171b22;
  --surface:    #1a1e26;
  --surface2:   #1f2530;
  --border:     #1f2530;
  --border2:    #252d3a;
  --text:       #e2e8f0;
  --text2:      #94a3b8;
  --muted:      #4b5563;
  --dim:        #374151;
}

#MainMenu, footer, header { visibility:hidden!important; display:none!important; }
[data-testid="stSidebar"],[data-testid="stSidebarNav"],[data-testid="collapsedControl"],
section[data-testid="stSidebar"],[data-testid="stSidebarUserContent"] {
    display:none!important;width:0!important;min-width:0!important;
    max-width:0!important;opacity:0!important;visibility:hidden!important;pointer-events:none!important;
}
[data-testid="stAppViewContainer"] > section:first-child{display:none!important;}
.stDeployButton{display:none!important;}
[data-testid="stDecoration"]{display:none!important;}

html,body,[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
.main .block-container{background:#0d0f11!important;}

.block-container{
    padding-top:2.5rem!important;padding-bottom:3rem!important;
    padding-left:2.5rem!important;padding-right:2.5rem!important;
    max-width:100%!important;
}
*{box-sizing:border-box;}
body{color:var(--text);font-family:'Inter',sans-serif;}
::-webkit-scrollbar{width:4px;height:4px;}
::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:var(--surface2);border-radius:2px;}

@keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes pulse{0%,100%{opacity:1;box-shadow:0 0 6px var(--green)}50%{opacity:0.35;box-shadow:none}}
@keyframes ticker{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}

.page-hero{
    background:linear-gradient(135deg,var(--bg2) 0%,var(--bg3) 100%);
    border:1px solid var(--border);border-radius:12px;
    padding:2rem 2.5rem;margin-bottom:1.8rem;
    position:relative;overflow:hidden;animation:fadeUp 0.35s ease both;
}
.page-hero::before{
    content:'';position:absolute;top:0;left:0;right:0;height:1px;
    background:linear-gradient(90deg,transparent,var(--green),transparent);opacity:0.4;
}
.page-hero::after{
    content:'';position:absolute;bottom:0;left:0;right:0;height:1px;
    background:linear-gradient(90deg,transparent,rgba(248,113,113,0.3),transparent);
}
.page-hero-eyebrow{font-family:'IBM Plex Mono',monospace;font-size:0.5rem;text-transform:uppercase;letter-spacing:0.3em;color:var(--green);margin-bottom:0.4rem;opacity:0.7;}
.page-hero h1{font-family:'Bebas Neue',sans-serif;font-size:2.8rem;letter-spacing:0.04em;line-height:1;color:var(--text);margin:0 0 0.4rem 0;}
.page-hero p{font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:var(--muted);line-height:1.8;max-width:580px;margin:0;}

.sec-t{font-family:'IBM Plex Mono',monospace;font-size:0.5rem;text-transform:uppercase;letter-spacing:0.25em;color:var(--dim);padding:1.1rem 0 0.65rem;border-top:1px solid var(--surface);margin-top:0.4rem;}

.metric-card{
    background:linear-gradient(135deg,var(--bg2),var(--bg3));
    border:1px solid var(--border);border-radius:10px;
    padding:1.2rem 1.4rem;
    transition:border-color 0.2s,transform 0.2s,box-shadow 0.2s;
    animation:fadeUp 0.4s ease both;position:relative;overflow:hidden;
}
.metric-card::after{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,var(--green),transparent);opacity:0;transition:opacity 0.2s;}
.metric-card:hover{border-color:var(--border2);transform:translateY(-2px);box-shadow:0 8px 30px rgba(0,0,0,0.4);}
.metric-card:hover::after{opacity:0.5;}
.metric-val{font-family:'IBM Plex Mono',monospace;font-size:1.9rem;font-weight:700;line-height:1;}
.metric-val.pos{color:var(--green);text-shadow:0 0 20px rgba(74,222,128,0.3);}
.metric-val.neg{color:var(--red);text-shadow:0 0 20px rgba(248,113,113,0.3);}
.metric-val.neu{color:var(--text);}
.metric-lbl{font-family:'IBM Plex Mono',monospace;font-size:0.48rem;text-transform:uppercase;letter-spacing:0.2em;color:var(--dim);margin-top:0.3rem;}
.metric-sub{font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:var(--muted);margin-top:0.15rem;}

.info-box{background:rgba(96,165,250,0.05);border:1px solid rgba(96,165,250,0.2);border-left:3px solid rgba(96,165,250,0.5);border-radius:8px;padding:0.75rem 1rem;font-size:0.77rem;color:var(--muted);line-height:1.6;}
.warn-box{background:rgba(251,191,36,0.05);border:1px solid rgba(251,191,36,0.2);border-left:3px solid rgba(251,191,36,0.5);border-radius:8px;padding:0.75rem 1rem;font-size:0.77rem;color:var(--muted);line-height:1.6;}
.success-box{background:rgba(74,222,128,0.04);border:1px solid rgba(74,222,128,0.2);border-left:3px solid var(--green);border-radius:8px;padding:0.75rem 1rem;font-size:0.77rem;color:var(--muted);line-height:1.6;}
.danger-box{background:rgba(248,113,113,0.04);border:1px solid rgba(248,113,113,0.2);border-left:3px solid var(--red);border-radius:8px;padding:0.75rem 1rem;font-size:0.77rem;color:var(--muted);line-height:1.6;}

.tag{display:inline-block;font-family:'IBM Plex Mono',monospace;font-size:0.48rem;text-transform:uppercase;letter-spacing:0.1em;padding:2px 7px;border-radius:3px;}
.tag-green{background:rgba(74,222,128,0.08);color:var(--green);border:1px solid rgba(74,222,128,0.2);}
.tag-red{background:rgba(248,113,113,0.08);color:var(--red);border:1px solid rgba(248,113,113,0.2);}
.tag-blue{background:rgba(96,165,250,0.08);color:var(--blue);border:1px solid rgba(96,165,250,0.2);}
.tag-yellow{background:rgba(251,191,36,0.08);color:var(--yellow);border:1px solid rgba(251,191,36,0.2);}

.section-hdr{display:flex;align-items:center;gap:0.7rem;padding:1rem 0 0.5rem;border-top:1px solid var(--surface);margin-top:0.4rem;}
.section-hdr-label{font-family:'IBM Plex Mono',monospace;font-size:0.5rem;text-transform:uppercase;letter-spacing:0.2em;color:var(--dim);}
.row-item{display:flex;align-items:center;justify-content:space-between;padding:0.45rem 0;border-bottom:1px solid var(--surface);font-size:0.8rem;}
.row-item:last-child{border-bottom:none;}
.divider{border:none;border-top:1px solid var(--border);margin:1.2rem 0;}

.chat-user{background:rgba(74,222,128,0.05);border:1px solid rgba(74,222,128,0.15);border-radius:12px 12px 2px 12px;padding:0.75rem 1rem;margin:0.4rem 0;font-size:0.82rem;color:var(--text);line-height:1.6;max-width:85%;margin-left:auto;}
.chat-ai{background:var(--bg2);border:1px solid var(--border);border-radius:2px 12px 12px 12px;padding:0.75rem 1rem;margin:0.4rem 0;font-size:0.82rem;color:var(--muted);line-height:1.6;max-width:92%;}
.chat-ai strong{color:var(--text);}
.chat-ai code{background:rgba(0,0,0,0.4);border:1px solid var(--border);border-radius:3px;padding:1px 4px;font-family:'IBM Plex Mono',monospace;font-size:0.77rem;color:var(--green);}

.ticker-outer{width:100%;overflow:hidden;background:var(--bg2);border:1px solid var(--border);border-radius:6px;height:34px;display:flex;align-items:center;margin-bottom:1.5rem;position:relative;}
.ticker-outer::before,.ticker-outer::after{content:'';position:absolute;top:0;bottom:0;width:60px;z-index:2;pointer-events:none;}
.ticker-outer::before{left:0;background:linear-gradient(90deg,var(--bg2),transparent);}
.ticker-outer::after{right:0;background:linear-gradient(-90deg,var(--bg2),transparent);}
.ticker-track{display:flex;white-space:nowrap;animation:ticker 40s linear infinite;}
.ticker-item{display:inline-flex;align-items:center;gap:7px;padding:0 20px;border-right:1px solid var(--border);font-family:'IBM Plex Mono',monospace;font-size:0.67rem;flex-shrink:0;}
.t-sym{color:var(--text2);font-weight:600;}
.t-up{color:var(--green);}
.t-dn{color:var(--red);}

.stat-strip{display:flex;background:var(--bg2);border:1px solid var(--border);border-radius:10px;overflow:hidden;margin-bottom:1.2rem;}
.stat-cell{flex:1;padding:0.85rem 1.1rem;border-right:1px solid var(--border);}
.stat-cell:last-child{border-right:none;}
.stat-val{font-family:'IBM Plex Mono',monospace;font-size:1.25rem;font-weight:700;line-height:1;}
.stat-val.pos{color:var(--green);text-shadow:0 0 15px rgba(74,222,128,0.25);}
.stat-val.neg{color:var(--red);text-shadow:0 0 15px rgba(248,113,113,0.25);}
.stat-val.neu{color:var(--text);}
.stat-lbl{font-family:'IBM Plex Mono',monospace;font-size:0.48rem;text-transform:uppercase;letter-spacing:0.18em;color:var(--dim);margin-top:0.25rem;}

[data-testid="stTextInput"] > div > div > input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] > div > div{background:var(--bg2)!important;border:1px solid var(--border)!important;color:var(--text)!important;border-radius:8px!important;font-family:'IBM Plex Mono',monospace!important;font-size:0.8rem!important;}
[data-testid="stTextInput"] > div > div > input:focus,
[data-testid="stNumberInput"] input:focus{border-color:var(--green)!important;box-shadow:0 0 0 2px rgba(74,222,128,0.1)!important;}
[data-testid="stButton"] > button{font-family:'IBM Plex Mono',monospace!important;font-size:0.68rem!important;font-weight:600!important;text-transform:uppercase!important;letter-spacing:0.1em!important;border-radius:8px!important;border:1px solid var(--border)!important;background:transparent!important;color:var(--muted)!important;transition:all 0.15s!important;padding:0.48rem 1rem!important;}
[data-testid="stButton"] > button:hover{border-color:var(--green)!important;color:var(--green)!important;background:rgba(74,222,128,0.05)!important;box-shadow:0 0 15px rgba(74,222,128,0.1)!important;}
div[data-testid="stButton"] > button[kind="primary"]{background:var(--green)!important;border-color:transparent!important;color:#030804!important;font-weight:700!important;}
div[data-testid="stButton"] > button[kind="primary"]:hover{background:#6ee7a0!important;box-shadow:0 0 20px rgba(74,222,128,0.3)!important;}
[data-testid="stTabs"] [role="tablist"]{gap:0;border-bottom:1px solid var(--border)!important;background:transparent;}
[data-testid="stTabs"] [role="tab"]{font-family:'IBM Plex Mono',monospace!important;font-size:0.56rem!important;font-weight:600!important;text-transform:uppercase!important;letter-spacing:0.14em!important;color:var(--dim)!important;border:none!important;border-bottom:2px solid transparent!important;background:transparent!important;padding:0.55rem 1.1rem!important;border-radius:0!important;transition:color 0.15s!important;}
[data-testid="stTabs"] [role="tab"][aria-selected="true"]{color:var(--green)!important;border-bottom-color:var(--green)!important;background:rgba(74,222,128,0.03)!important;}
[data-testid="stExpander"]{background:var(--bg2)!important;border:1px solid var(--border)!important;border-radius:8px!important;}
[data-testid="stExpander"] summary{font-family:'IBM Plex Mono',monospace!important;font-size:0.66rem!important;font-weight:600!important;text-transform:uppercase!important;letter-spacing:0.14em!important;color:var(--muted)!important;}
[data-testid="stSlider"] > div > div > div{background:var(--green)!important;}
[data-testid="stCheckbox"] label{font-size:0.8rem!important;color:var(--muted)!important;}
div[data-baseweb="select"] > div{background:var(--bg2)!important;border-color:var(--border)!important;}
[data-testid="stRadio"] label{font-size:0.8rem!important;color:var(--muted)!important;}
[data-testid="stTextArea"] textarea{background:var(--bg2)!important;border:1px solid var(--border)!important;color:var(--text)!important;border-radius:8px!important;font-family:'IBM Plex Mono',monospace!important;font-size:0.78rem!important;}
[data-testid="stDateInput"] input{background:var(--bg2)!important;border:1px solid var(--border)!important;color:var(--text)!important;border-radius:8px!important;font-family:'IBM Plex Mono',monospace!important;}
[data-testid="stProgress"] > div > div{background:var(--green)!important;}
[data-testid="stMultiSelect"] > div > div{background:var(--bg2)!important;border:1px solid var(--border)!important;border-radius:8px!important;}

.page-header{margin-bottom:1.8rem;animation:fadeUp 0.35s ease both;}
.page-header-eyebrow{font-family:'IBM Plex Mono',monospace;font-size:0.5rem;text-transform:uppercase;letter-spacing:0.3em;color:var(--green);opacity:0.7;margin-bottom:0.35rem;}
.page-header h1{font-family:'Bebas Neue',sans-serif;font-size:2.8rem;letter-spacing:0.04em;line-height:1;color:var(--text);margin:0 0 0.35rem 0;}
.page-header p{font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:var(--muted);line-height:1.8;max-width:580px;}
</style>
"""

# ── Animated particle background + global same-tab nav fix ──────────────────
ANIMATED_BG = """
<canvas id="ep-bg-canvas" style="position:fixed;top:0;left:0;width:100vw;height:100vh;
pointer-events:none;z-index:0;opacity:0.18"></canvas>
<script>
(function(){
  /* Particle background */
  var c=document.getElementById('ep-bg-canvas');
  if(c){
    var ctx=c.getContext('2d');
    function resize(){c.width=window.innerWidth;c.height=window.innerHeight;}
    resize();
    window.addEventListener('resize',resize);
    var pts=[];
    for(var i=0;i<60;i++) pts.push({
      x:Math.random()*c.width,y:Math.random()*c.height,
      vx:(Math.random()-0.5)*0.3,vy:(Math.random()-0.5)*0.3,
      r:Math.random()*1.1+0.3,
      col:Math.random()>0.5?'rgba(74,222,128,':'rgba(248,113,113,'
    });
    function draw(){
      ctx.clearRect(0,0,c.width,c.height);
      pts.forEach(function(p,i){
        p.x+=p.vx;p.y+=p.vy;
        if(p.x<0||p.x>c.width)p.vx*=-1;
        if(p.y<0||p.y>c.height)p.vy*=-1;
        ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
        ctx.fillStyle=p.col+'0.8)';ctx.fill();
        pts.slice(i+1).forEach(function(q){
          var dx=p.x-q.x,dy=p.y-q.y,d=Math.sqrt(dx*dx+dy*dy);
          if(d<100){
            ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(q.x,q.y);
            ctx.strokeStyle=p.col+(0.08*(1-d/100))+')';
            ctx.lineWidth=0.4;ctx.stroke();
          }
        });
      });
      requestAnimationFrame(draw);
    }
    draw();
  }

  /* Global same-tab navigation fix */
  document.addEventListener('click',function(e){
    var a=e.target.closest('a[href]');
    if(!a)return;
    var href=a.getAttribute('href');
    if(!href||href.startsWith('http')||href.startsWith('mailto')||href.startsWith('#'))return;
    e.preventDefault();
    try{window.top.location.href=href;}
    catch(err){window.location.href=href;}
  },true);
})();
</script>
"""

def inject_bg():
    """Call at the top of every page after navbar() to add the animated background."""
    import streamlit as st
    st.markdown(ANIMATED_BG, unsafe_allow_html=True)
