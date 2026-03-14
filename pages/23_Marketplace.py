import streamlit as st, sys, os
from datetime import datetime, date
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS, inject_bg
from utils.nav import navbar
from utils.session_persist import restore_session
from utils import db

st.set_page_config(page_title="Marketplace | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
st.markdown("""<style>
html,body,[data-testid="stAppViewContainer"]{background:#13161a!important}
[data-testid="stSidebar"],[data-testid="stSidebarNav"],[data-testid="collapsedControl"],
section[data-testid="stSidebar"]{display:none!important;width:0!important;max-width:0!important;opacity:0!important}
.post-card{background:#1c1f23;border:1px solid #2d333b;border-radius:12px;padding:1.4rem 1.6rem;margin-bottom:0.8rem;transition:border-color 0.2s,transform 0.15s;position:relative;overflow:hidden}
.post-card:hover{border-color:#373d47;transform:translateY(-2px)}
.post-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,var(--acc,#4ade80),transparent)}
.post-title{font-family:'Bebas Neue',sans-serif;font-size:1.4rem;letter-spacing:0.04em;color:#e6eaf0;margin-bottom:0.2rem}
.post-thesis{font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#9ca3af;line-height:1.75;margin-top:0.5rem}
.post-meta{display:flex;align-items:center;gap:0.8rem;flex-wrap:wrap;margin-top:0.7rem;font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#6b7280}
.dir-bull{background:rgba(74,222,128,0.1);color:#4ade80;border:1px solid rgba(74,222,128,0.25);border-radius:3px;padding:2px 8px;font-size:0.46rem;text-transform:uppercase;letter-spacing:0.12em}
.dir-bear{background:rgba(248,113,113,0.1);color:#f87171;border:1px solid rgba(248,113,113,0.25);border-radius:3px;padding:2px 8px;font-size:0.46rem;text-transform:uppercase;letter-spacing:0.12em}
.dir-neut{background:rgba(251,191,36,0.1);color:#fbbf24;border:1px solid rgba(251,191,36,0.25);border-radius:3px;padding:2px 8px;font-size:0.46rem;text-transform:uppercase;letter-spacing:0.12em}
.targets-row{display:grid;grid-template-columns:repeat(3,1fr);gap:0.5rem;margin-top:0.8rem}
.target-cell{background:#13161a;border:1px solid #2d333b;border-radius:7px;padding:0.6rem;text-align:center}
.target-n{font-family:'IBM Plex Mono',monospace;font-size:0.82rem;font-weight:600;line-height:1}
.target-l{font-family:'IBM Plex Mono',monospace;font-size:0.44rem;text-transform:uppercase;letter-spacing:0.16em;color:#3d4450;margin-top:0.15rem}
.beta-banner{background:rgba(251,191,36,0.06);border:1px solid rgba(251,191,36,0.2);border-radius:10px;padding:0.9rem 1.3rem;margin-bottom:1.2rem;display:flex;align-items:center;gap:0.8rem;font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#fbbf24}
</style>""", unsafe_allow_html=True)

restore_session()
navbar()

# ── Same-tab nav hook ─────────────────────────────────────────────────────────
import streamlit.components.v1 as _nav_cv1
_nav_cv1.html("""<script>
(function(){
  window.parent.document.addEventListener('click',function(e){
    var a=e.target.closest('a[href]');
    if(!a)return;
    var href=a.getAttribute('href');
    if(!href||href.startsWith('http')||href.startsWith('mailto')||href.startsWith('#'))return;
    e.preventDefault();e.stopPropagation();
    window.top.location.href=href;
  },true);
})();
</script>""", height=0)

inject_bg()

is_logged = bool(st.session_state.get("user"))
uid   = getattr(st.session_state.get("user"),"id","") or "" if is_logged else ""
uname = (st.session_state.get("user_email","").split("@")[0].replace("."," ").replace("_"," ").title()) if is_logged else ""

# Page header
st.markdown("""
<div style="background:#1c1f23;border:1px solid #2d333b;border-radius:12px;padding:2rem 2.5rem;margin-bottom:1.2rem;position:relative;overflow:hidden">
    <div style="position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,#a78bfa,transparent)"></div>
    <div style="display:flex;align-items:center;gap:1rem;margin-bottom:0.4rem">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:2.8rem;letter-spacing:0.04em;line-height:1">Strategy <span style="color:#a78bfa">Marketplace</span></div>
        <span style="background:rgba(251,191,36,0.1);color:#fbbf24;border:1px solid rgba(251,191,36,0.25);font-family:'IBM Plex Mono',monospace;font-size:0.5rem;text-transform:uppercase;letter-spacing:0.14em;padding:3px 10px;border-radius:4px">BETA</span>
    </div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:#6b7280;max-width:600px;line-height:1.8">
        Share your market views and trading setups. See what other traders are watching. 
        This is not financial advice — it's a space to share ideas and learn from each other.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="beta-banner">This is a beta feature. Posts are moderated. Sharing market insights here does not constitute financial advice and should not be acted upon without your own due diligence.</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Browse Ideas", "Share Your View"])

# ── TAB 1: Browse ─────────────────────────────────────────────────────────────
with tab1:
    # Filters
    f1, f2, f3, _ = st.columns([1,1,1,3])
    with f1: filter_dir = st.selectbox("Direction", ["All","Bullish","Bearish","Neutral"])
    with f2: filter_tf  = st.selectbox("Timeframe", ["All","Scalp","Intraday","Swing","Position"])
    with f3: filter_sort= st.selectbox("Sort", ["Newest","Oldest"])

    # Load posts
    posts = []
    try:
        sb = db._sb()
        if sb:
            q = sb.table("market_posts").select("*").eq("approved",True)
            if filter_dir != "All": q = q.eq("direction", filter_dir)
            q = q.order("created_at", desc=(filter_sort=="Newest"))
            res = q.execute()
            posts = res.data or []
    except: pass

    if not posts:
        # Demo posts
        posts = [
            {"id":"d1","username":"TraderX","title":"AAPL Breakout Setup","ticker":"AAPL","timeframe":"Swing","direction":"Bullish","thesis":"AAPL has been consolidating at the 200-day EMA for 3 weeks with decreasing volume. Classic accumulation pattern. Watching for a breakout above $185 on strong volume. The broader market is turning and tech is leading.","entry":183.50,"stop":178.00,"target":196.00,"strategy":"EMA + RSI Filter","created_at":"2026-03-12T10:00:00"},
            {"id":"d2","username":"MacroMind","title":"SPY Distribution Top","ticker":"SPY","timeframe":"Position","direction":"Bearish","thesis":"SPY showing classic distribution pattern after 15% run from October lows. Smart money has been selling into retail strength. Watch the 530 level — break below that with volume is the signal. Fed staying higher for longer is the macro catalyst.","entry":535.00,"stop":542.00,"target":510.00,"strategy":"Custom","created_at":"2026-03-11T14:30:00"},
            {"id":"d3","username":"MomentumKing","title":"BTC Pre-Halving Accumulation","ticker":"BTC-USD","timeframe":"Swing","direction":"Bullish","thesis":"Historical pattern: BTC consolidates 60-90 days before halving then runs. We are in that window. Retail is bearish which is exactly when to be accumulating. RSI on weekly is at 45 — not overbought at all.","entry":65000,"stop":58000,"target":85000,"strategy":"Hull MA Cross","created_at":"2026-03-10T08:00:00"},
        ]
        st.markdown('<div class="info-box" style="margin-bottom:1rem">Showing example posts. Connect Supabase to see live community ideas.</div>', unsafe_allow_html=True)

    for p in posts:
        dir_badge = {"Bullish":'<span class="dir-bull">Bullish</span>',"Bearish":'<span class="dir-bear">Bearish</span>'}.get(p.get("direction","Neutral"),'<span class="dir-neut">Neutral</span>')
        accent = {"Bullish":"#4ade80","Bearish":"#f87171"}.get(p.get("direction",""),"#fbbf24")
        entry  = p.get("entry"); stop = p.get("stop"); target = p.get("target")
        rr_str = f"{abs(target-entry)/abs(entry-stop):.1f}R" if entry and stop and target and abs(entry-stop)>0 else "—"
        date_str = p.get("created_at","")[:10] if p.get("created_at") else "—"

        st.markdown(f"""
        <div class="post-card" style="--acc:{accent}">
            <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:1rem">
                <div style="flex:1">
                    <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.2rem">
                        {dir_badge}
                        <div class="post-title">{p["title"]}</div>
                    </div>
                    <div class="post-thesis">{p["thesis"]}</div>
                    <div class="post-meta">
                        <span><strong style="color:#e6eaf0">{p.get("ticker","")}</strong></span>
                        <span>{p.get("timeframe","")}</span>
                        <span>{p.get("strategy","")}</span>
                        <span style="margin-left:auto">by <strong style="color:#9ca3af">{p.get("username","")}</strong> · {date_str}</span>
                    </div>
                </div>
                {f'''<div style="min-width:180px">
                    <div class="targets-row">
                        <div class="target-cell"><div class="target-n" style="color:#9ca3af">${entry:,.2f}</div><div class="target-l">Entry</div></div>
                        <div class="target-cell"><div class="target-n" style="color:#f87171">${stop:,.2f}</div><div class="target-l">Stop</div></div>
                        <div class="target-cell"><div class="target-n" style="color:#4ade80">${target:,.2f}</div><div class="target-l">Target</div></div>
                    </div>
                    <div style="text-align:center;margin-top:0.4rem;font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:#fbbf24">R/R: {rr_str}</div>
                </div>''' if entry else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── TAB 2: Share ──────────────────────────────────────────────────────────────
with tab2:
    if not is_logged:
        st.markdown('<div class="warn-box">Sign in to share your market views.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:#6b7280;margin-bottom:1.2rem;line-height:1.9">Share your market analysis. Be specific and show your work. Low-quality posts will not be approved.</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            p_title  = st.text_input("Title", placeholder="e.g. AAPL Breakout Setup — Q1 2026")
            p_ticker = st.text_input("Ticker", placeholder="AAPL, BTC-USD, SPY").upper().strip()
            p_dir    = st.selectbox("Your View", ["Bullish","Bearish","Neutral"])
            p_tf     = st.selectbox("Timeframe", ["Scalp","Intraday","Swing","Position"])
            p_strat  = st.text_input("Strategy / Method", placeholder="e.g. EMA Crossover + RSI confirmation")
        with c2:
            p_entry  = st.number_input("Entry Price ($)", value=0.0, format="%.2f")
            p_stop   = st.number_input("Stop Loss ($)",   value=0.0, format="%.2f")
            p_target = st.number_input("Target Price ($)",value=0.0, format="%.2f")

        p_thesis = st.text_area("Your Thesis — explain the setup and why you think it works", height=140,
                                placeholder="Be specific. What pattern are you seeing? What's the catalyst? Why here, why now?")

        if st.button("Submit for Review", type="primary"):
            if not p_title or not p_ticker or not p_thesis:
                st.error("Title, ticker, and thesis are required.")
            elif len(p_thesis) < 80:
                st.error("Thesis is too short. Be more specific about your setup (at least 80 characters).")
            else:
                try:
                    payload = {
                        "user_id": uid, "username": uname,
                        "title": p_title, "ticker": p_ticker,
                        "timeframe": p_tf, "direction": p_dir,
                        "thesis": p_thesis, "strategy": p_strat,
                        "entry": float(p_entry) if p_entry else None,
                        "stop":  float(p_stop)  if p_stop  else None,
                        "target":float(p_target) if p_target else None,
                        "approved": False, "status": "open",
                    }
                    sb4 = db._sb()
                    if sb4:
                        sb4.table("market_posts").insert(payload).execute()
                        st.success("Post submitted for review. It will appear once approved.")
                    else:
                        st.info("Post saved (no DB connection). In production this will be submitted for review.")
                except Exception as e:
                    st.error(f"Error: {e}")
