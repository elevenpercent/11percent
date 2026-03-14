import streamlit as st, sys, os, pandas as pd
import plotly.graph_objects as go
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS, inject_bg, PLOTLY_THEME; from utils.nav import navbar
from utils import db

st.set_page_config(page_title="Trade Journal | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
st.markdown("""<style>
.jh{background:linear-gradient(135deg,#0c1018,#0d1420);border:1px solid #1a2235;border-radius:16px;padding:2.5rem 3rem;margin-bottom:2rem;position:relative;overflow:hidden}
.jh::before{content:'';position:absolute;bottom:-40px;right:-40px;width:180px;height:180px;background:radial-gradient(circle,rgba(255,209,102,0.05),transparent 70%);pointer-events:none}
.jh-ey{font-family:'IBM Plex Mono',monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.3em;color:#3a4a5e;margin-bottom:0.5rem}
.jh h1{font-family:'Bebas Neue',sans-serif;font-size:3.5rem;letter-spacing:0.05em;line-height:1;margin:0 0 0.5rem 0}
.jh p{font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8896ab;line-height:1.8;margin:0}
.bm{background:#0c1018;border:1px solid #1a2235;border-radius:12px;padding:1.5rem 1.8rem;transition:border-color 0.2s}
.bm:hover{border-color:#2a3550}
.bm-v{font-family:'Bebas Neue',sans-serif;font-size:2.4rem;letter-spacing:0.04em;line-height:1}
.bm-l{font-family:'IBM Plex Mono',monospace;font-size:0.5rem;text-transform:uppercase;letter-spacing:0.22em;color:#3a4a5e;margin-top:0.35rem}
.sec-t{font-family:'IBM Plex Mono',monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.25em;color:#3a4a5e;padding:1.5rem 0 0.8rem;border-top:1px solid #0d1117}
.entry-card{background:#0c1018;border:1px solid #1a2235;border-radius:12px;padding:1.5rem;margin-bottom:0.75rem;transition:border-color 0.2s}
.entry-card:hover{border-color:#2a3550}
.entry-sym{font-family:'Bebas Neue',sans-serif;font-size:1.8rem;letter-spacing:0.06em}
.entry-meta{font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#8896ab}
.entry-pnl-pos{color:#00e676;font-family:'IBM Plex Mono',monospace;font-size:0.9rem;font-weight:700}
.entry-pnl-neg{color:#ff3d57;font-family:'IBM Plex Mono',monospace;font-size:0.9rem;font-weight:700}
.emotion-calm{color:#00e676}.emotion-fomo{color:#ff3d57}.emotion-hesitant{color:#ffd166}
.emotion-revenge{color:#ff3d57}.emotion-bored{color:#8896ab}
</style>""", unsafe_allow_html=True)
navbar()
inject_bg()

st.markdown("""<div class="jh"><div class="jh-ey">Psychology & Discipline</div><h1>Trade Journal</h1><p>Log trades with emotional state, setup notes, and mistakes. The most successful traders know their patterns — both technical and psychological. This page finds yours.</p></div>""", unsafe_allow_html=True)

if "journal" not in st.session_state:
    db.load_into_session("journal", "journal", [])

tab1, tab2, tab3 = st.tabs(["Log Trade", "Analytics", "All Entries"])

with tab1:
    st.markdown('<div class="sec-t">New Trade Entry</div>', unsafe_allow_html=True)
    ja,jb,jc,jd = st.columns(4)
    with ja: j_date  = st.date_input("Date", value=date.today())
    with jb: j_sym   = st.text_input("Ticker", placeholder="AAPL").upper()
    with jc: j_dir   = st.selectbox("Direction", ["Long","Short"])
    with jd: j_out   = st.selectbox("Outcome", ["Win","Loss","Breakeven"])

    je,jf,jg,jh = st.columns(4)
    with je: j_entry = st.number_input("Entry ($)", value=100.00, format="%.2f")
    with jf: j_exit  = st.number_input("Exit ($)",  value=105.00, format="%.2f")
    with jg: j_qty   = st.number_input("Shares", value=100, min_value=1)
    with jh: j_strat = st.selectbox("Strategy", ["SMA Cross","EMA Cross","RSI","MACD","Bollinger Bands","SuperTrend","Custom","Discretionary","Other"])

    pnl_preview = (j_exit - j_entry) * j_qty if j_dir == "Long" else (j_entry - j_exit) * j_qty
    pnl_color = "#00e676" if pnl_preview >= 0 else "#ff3d57"
    st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.78rem;padding:0.7rem 1rem;background:#0c1018;border:1px solid #1a2235;border-radius:8px;margin:0.5rem 0;">P&L Preview: <strong style="color:{pnl_color}">${pnl_preview:+,.2f}</strong></div>', unsafe_allow_html=True)

    j_setup   = st.text_area("Setup & Thesis — why did you enter?", height=80, placeholder="e.g. EMA20 crossed above EMA50, MACD bullish divergence, above VWAP, institutional level respected...")
    j_emotion = st.selectbox("Emotional state when entering", ["Calm / Focused","Excited / FOMO","Uncertain / Hesitant","Revenge Trading","Bored","Overconfident","Other"])
    j_mistakes = st.multiselect("Mistakes made (if any)", ["Sized too large","Moved stop to breakeven too early","Chased entry","Ignored stop loss","Took profit too early","Added to a loser","Traded off-plan","Over-traded","None"])
    j_lesson  = st.text_area("Lesson — what would you do differently?", height=70, placeholder="e.g. Wait for RSI confirmation before entering momentum setups...")
    j_rating  = st.slider("Trade quality (1 = terrible execution, 10 = perfect)", 1, 10, 7)

    if st.button("Save Trade Entry", type="primary"):
        pnl = (j_exit - j_entry) * j_qty if j_dir == "Long" else (j_entry - j_exit) * j_qty
        st.session_state["journal"].append({
            "date":str(j_date),"sym":j_sym,"dir":j_dir,"out":j_out,
            "entry":j_entry,"exit":j_exit,"qty":j_qty,"pnl":round(pnl,2),
            "strat":j_strat,"emotion":j_emotion,
            "mistakes":"; ".join(j_mistakes) if j_mistakes else "None",
            "lesson":j_lesson,"rating":j_rating,"setup":j_setup
        })
        st.success(f"Entry saved. P&L: ${pnl:+,.2f}")
        db.sync("journal")
        st.rerun()

with tab2:
    if not st.session_state["journal"]:
        st.markdown('<div style="text-align:center;padding:4rem;color:#3a4a5e;font-family:IBM Plex Mono,monospace;font-size:0.75rem;border:1px dashed #1a2235;border-radius:12px;margin-top:1rem;">Log some trades first to see your analytics.</div>', unsafe_allow_html=True)
    else:
        df = pd.DataFrame(st.session_state["journal"])
        wins = (df["out"]=="Win").sum(); total = len(df)
        wr = wins/total*100; avg_pnl = df["pnl"].mean(); total_pnl = df["pnl"].sum()
        avg_win  = df[df["pnl"]>0]["pnl"].mean() if len(df[df["pnl"]>0]) else 0
        avg_loss = df[df["pnl"]<0]["pnl"].mean() if len(df[df["pnl"]<0]) else 0
        profit_factor = abs(df[df["pnl"]>0]["pnl"].sum() / df[df["pnl"]<0]["pnl"].sum()) if len(df[df["pnl"]<0]) > 0 else 999

        st.markdown('<div class="sec-t">Overall Performance</div>', unsafe_allow_html=True)
        m1,m2,m3,m4,m5,m6 = st.columns(6)
        for col,(v,l,c) in zip([m1,m2,m3,m4,m5,m6],[
            (f"{wr:.0f}%","Win Rate","#00e676" if wr>=50 else "#ff3d57"),
            (f"${total_pnl:+,.0f}","Total P&L","#00e676" if total_pnl>=0 else "#ff3d57"),
            (f"${avg_pnl:+.0f}","Avg P&L","#00e676" if avg_pnl>=0 else "#ff3d57"),
            (f"${avg_win:+.0f}","Avg Win","#00e676"),
            (f"${avg_loss:+.0f}","Avg Loss","#ff3d57"),
            (f"{profit_factor:.2f}","Profit Factor","#ffd166"),
        ]):
            col.markdown(f'<div class="bm"><div class="bm-v" style="color:{c}">{v}</div><div class="bm-l">{l}</div></div>', unsafe_allow_html=True)

        # Equity curve
        st.markdown('<div class="sec-t">Equity Curve</div>', unsafe_allow_html=True)
        df_sorted = df.sort_values("date")
        cumulative = df_sorted["pnl"].cumsum()
        fig_eq = go.Figure()
        fig_eq.add_scatter(x=list(range(1,len(df_sorted)+1)), y=cumulative,
                           fill="tozeroy", fillcolor="rgba(0,230,118,0.06)",
                           line=dict(color="#00e676", width=2), name="Cumulative P&L")
        fig_eq.update_layout(**PLOTLY_THEME, height=280, title="Cumulative P&L Over Trades",
                             xaxis_title="Trade #", yaxis_title="Cumulative P&L ($)")
        st.plotly_chart(fig_eq, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="sec-t">Performance by Emotion</div>', unsafe_allow_html=True)
            em_stats = df.groupby("emotion")["pnl"].agg(["mean","sum","count"]).reset_index()
            em_stats.columns = ["Emotion","Avg P&L ($)","Total P&L ($)","Trades"]
            em_stats = em_stats.sort_values("Total P&L ($)", ascending=False)
            fig_em = go.Figure(go.Bar(
                x=em_stats["Emotion"], y=em_stats["Total P&L ($)"],
                marker_color=["#00e676" if v>=0 else "#ff3d57" for v in em_stats["Total P&L ($)"]],
                text=[f"${v:+,.0f}" for v in em_stats["Total P&L ($)"]], textposition="outside",
                textfont=dict(family="IBM Plex Mono", size=10)
            ))
            fig_em.update_layout(**PLOTLY_THEME, height=280, showlegend=False, title="P&L by Emotional State")
            st.plotly_chart(fig_em, use_container_width=True)

        with c2:
            st.markdown('<div class="sec-t">Performance by Strategy</div>', unsafe_allow_html=True)
            st_stats = df.groupby("strat")["pnl"].agg(["mean","sum","count"]).reset_index()
            st_stats.columns = ["Strategy","Avg P&L ($)","Total P&L ($)","Trades"]
            st_stats = st_stats.sort_values("Total P&L ($)", ascending=False)
            fig_st = go.Figure(go.Bar(
                x=st_stats["Strategy"], y=st_stats["Total P&L ($)"],
                marker_color=["#00e676" if v>=0 else "#ff3d57" for v in st_stats["Total P&L ($)"]],
                text=[f"${v:+,.0f}" for v in st_stats["Total P&L ($)"]], textposition="outside",
                textfont=dict(family="IBM Plex Mono", size=10)
            ))
            fig_st.update_layout(**PLOTLY_THEME, height=280, showlegend=False, title="P&L by Strategy")
            st.plotly_chart(fig_st, use_container_width=True)

        # Mistakes
        all_mistakes = [m for row in df["mistakes"] for m in row.split("; ") if m != "None"]
        if all_mistakes:
            st.markdown('<div class="sec-t">Most Common Mistakes</div>', unsafe_allow_html=True)
            mk_df = pd.Series(all_mistakes).value_counts().reset_index()
            mk_df.columns = ["Mistake","Count"]
            fig_mk = go.Figure(go.Bar(
                y=mk_df["Mistake"], x=mk_df["Count"], orientation="h",
                marker_color="#ff3d57",
                text=mk_df["Count"], textposition="outside",
                textfont=dict(family="IBM Plex Mono", size=11)
            ))
            fig_mk.update_layout(**PLOTLY_THEME, height=max(200, len(mk_df)*50),
                                 showlegend=False, title="Mistake Frequency")
            st.plotly_chart(fig_mk, use_container_width=True)

with tab3:
    if not st.session_state["journal"]:
        st.markdown('<div style="text-align:center;padding:4rem;color:#3a4a5e;font-family:IBM Plex Mono,monospace;font-size:0.75rem;border:1px dashed #1a2235;border-radius:12px;margin-top:1rem;">No entries yet.</div>', unsafe_allow_html=True)
    else:
        df2 = pd.DataFrame(st.session_state["journal"])
        st.dataframe(df2[["date","sym","dir","out","entry","exit","pnl","strat","emotion","rating","mistakes"]],
                     use_container_width=True, hide_index=True)
        ca, cb = st.columns(2)
        with ca:
            st.download_button("Download Journal CSV", df2.to_csv(index=False),
                              file_name="trade_journal.csv", mime="text/csv", use_container_width=True)
        with cb:
            if st.button("Clear All Entries", use_container_width=True):
                st.session_state["journal"] = []; db.sync("journal"); st.rerun()
