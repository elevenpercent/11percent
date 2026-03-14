import streamlit as st, sys, os, math, pandas as pd, numpy as np
import yfinance as yf, plotly.graph_objects as go
from scipy.stats import norm
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS, PLOTLY_THEME; from utils.nav import navbarimport streamlit as st, sys, os, math, pandas as pd, numpy as np
import yfinance as yf, plotly.graph_objects as go
from scipy.stats import norm
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS, inject_bg, PLOTLY_THEME; from utils.nav import navbar

st.set_page_config(page_title="Options Chain | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
st.markdown("""<style>
.ph{background:linear-gradient(135deg,#141a1f,#111820);border:1px solid #243040;border-radius:16px;padding:2.5rem 3rem;margin-bottom:2rem;position:relative;overflow:hidden}
.ph::before{content:'';position:absolute;top:-40px;right:-40px;width:160px;height:160px;background:radial-gradient(circle,rgba(167,139,250,0.07),transparent 70%);pointer-events:none}
.ph h1{font-family:'Bebas Neue',sans-serif;font-size:3.2rem;letter-spacing:0.05em;line-height:1;margin:0 0 0.5rem 0}
.ph p{font-family:'IBM Plex Mono',monospace;font-size:0.72rem;color:#8896ab;line-height:1.8;margin:0}
.ph-ey{font-family:'IBM Plex Mono',monospace;font-size:0.52rem;text-transform:uppercase;letter-spacing:0.3em;color:#3d5068;margin-bottom:0.5rem}
.sec-t{font-family:'IBM Plex Mono',monospace;font-size:0.52rem;text-transform:uppercase;letter-spacing:0.25em;color:#3d5068;padding:1.2rem 0 0.7rem;border-top:1px solid #1e2830}
.bm{background:#141a1f;border:1px solid #243040;border-radius:12px;padding:1.4rem 1.6rem;transition:border-color 0.2s}
.bm:hover{border-color:#2e3d50}
.bm-v{font-family:'Bebas Neue',sans-serif;font-size:2.2rem;letter-spacing:0.04em;line-height:1}
.bm-l{font-family:'IBM Plex Mono',monospace;font-size:0.5rem;text-transform:uppercase;letter-spacing:0.2em;color:#3d5068;margin-top:0.35rem}
.bm-s{font-family:'IBM Plex Mono',monospace;font-size:0.62rem;color:#8896ab;margin-top:0.15rem}
.chain-hdr{display:grid;grid-template-columns:80px 70px 70px 80px 70px 70px;gap:8px;padding:0.6rem 1rem;background:#1a2230;font-family:'IBM Plex Mono',monospace;font-size:0.5rem;text-transform:uppercase;letter-spacing:0.15em;color:#3d5068;border-radius:6px 6px 0 0}
.chain-row{display:grid;grid-template-columns:80px 70px 70px 80px 70px 70px;gap:8px;padding:0.7rem 1rem;border-bottom:1px solid #141a1f;font-family:'IBM Plex Mono',monospace;font-size:0.72rem;transition:background 0.12s;align-items:center}
.chain-row:hover{background:rgba(255,255,255,0.02)}
.chain-atm{background:rgba(38,217,127,0.04)!important}
.strat-card{background:#141a1f;border:1px solid #243040;border-radius:12px;padding:1.4rem 1.6rem;margin-bottom:0.6rem;display:flex;align-items:flex-start;gap:2rem;transition:border-color 0.2s,transform 0.15s}
.strat-card:hover{border-color:#2e3d50;transform:translateX(4px)}
.strat-name{font-family:'Bebas Neue',sans-serif;font-size:1.4rem;letter-spacing:0.05em;min-width:200px}
.strat-desc{font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:#8896ab;line-height:1.7;flex:1}
.sbadge{font-family:'IBM Plex Mono',monospace;font-size:0.48rem;text-transform:uppercase;letter-spacing:0.12em;padding:3px 10px;border-radius:4px;white-space:nowrap;display:block;margin-bottom:4px}
/* Play advisor */
.advisor-card{background:linear-gradient(135deg,#141a1f,#111820);border:1px solid #243040;border-radius:16px;padding:1.8rem 2rem;margin-bottom:1rem;position:relative;overflow:hidden;animation:fadeUp 0.4s ease both}
.advisor-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,var(--accent,#26d97f),transparent)}
.advisor-title{font-family:'Bebas Neue',sans-serif;font-size:1.8rem;letter-spacing:0.05em;margin-bottom:0.3rem}
.advisor-sub{font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:#8896ab;line-height:1.7;margin-bottom:1rem}
.greek-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:0.8rem;margin:1rem 0}
.greek-cell{background:#0f1318;border:1px solid #1e2830;border-radius:8px;padding:0.9rem;text-align:center}
.greek-val{font-family:'Bebas Neue',sans-serif;font-size:1.6rem;letter-spacing:0.03em}
.greek-lbl{font-family:'IBM Plex Mono',monospace;font-size:0.48rem;text-transform:uppercase;letter-spacing:0.15em;color:#3d5068;margin-top:0.2rem}
.play-row{display:flex;align-items:flex-start;gap:1.2rem;padding:0.9rem 1rem;border:1px solid #243040;border-radius:10px;margin-bottom:0.6rem;cursor:pointer;transition:background 0.15s,border-color 0.15s}
.play-row:hover{background:rgba(255,255,255,0.02);border-color:#2e3d50}
.play-rank{font-family:'Bebas Neue',sans-serif;font-size:2rem;color:#3d5068;min-width:36px}
.play-name{font-family:'Bebas Neue',sans-serif;font-size:1.3rem;letter-spacing:0.04em;margin-bottom:0.2rem}
.play-why{font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#8896ab;line-height:1.6}
.play-score{font-family:'Bebas Neue',sans-serif;font-size:1.4rem;min-width:60px;text-align:right}
.score-bar{height:4px;border-radius:2px;margin-top:0.4rem}
</style>""", unsafe_allow_html=True)
navbar()
inject_bg()

st.markdown("""<div class="ph"><div class="ph-ey">Options Trading</div><h1>Options Chain</h1>
<p>Live chain with OI chart, full Greeks, Black-Scholes pricer, and an AI-style Play Advisor that tells you which options strategy fits the current setup.</p></div>""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["Live Chain", "Play Advisor", "Black-Scholes", "Strategy Guide"])

# ─── TAB 1: LIVE CHAIN ────────────────────────────────────────────────────────
with tab1:
    c1, c2 = st.columns([2, 4])
    with c1: ot = st.text_input("Ticker", value="AAPL", placeholder="AAPL, TSLA, SPY").upper().strip()
    with c2:
        st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.68rem;color:#3d5068;padding-top:1.9rem;">Live data from Yahoo Finance. Green = ATM strike. Sorted by open interest.</div>', unsafe_allow_html=True)

    exp_sel = None
    if st.button("Load Options Chain", type="primary"):
        with st.spinner(f"Loading {ot}..."):
            try:
                tk    = yf.Ticker(ot)
                price = tk.fast_info.last_price or 0
                exps  = tk.options
                if not exps: st.error("No options found."); st.stop()
                st.session_state.update({"opt_sym":ot,"opt_price":price,"opt_exps":list(exps),"opt_exp":exps[0]})
                chain = tk.option_chain(exps[0])
                st.session_state.update({"opt_calls":chain.calls,"opt_puts":chain.puts})
            except Exception as e: st.error(f"Error: {e}")

    if "opt_exps" in st.session_state:
        ec1, ec2 = st.columns([3,5])
        with ec1:
            new_exp = st.selectbox("Expiry date", st.session_state["opt_exps"],
                                    index=st.session_state["opt_exps"].index(st.session_state["opt_exp"]))
        if new_exp != st.session_state["opt_exp"]:
            with st.spinner("Loading..."):
                try:
                    chain = yf.Ticker(st.session_state["opt_sym"]).option_chain(new_exp)
                    st.session_state.update({"opt_exp":new_exp,"opt_calls":chain.calls,"opt_puts":chain.puts})
                    st.rerun()
                except: pass

    if "opt_calls" in st.session_state:
        price = st.session_state["opt_price"]
        calls = st.session_state["opt_calls"]
        puts  = st.session_state["opt_puts"]
        sym   = st.session_state["opt_sym"]
        exp   = st.session_state["opt_exp"]

        st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.8rem;color:#26d97f;margin:1rem 0 0.5rem;"><strong>{sym}</strong> @ ${price:.2f} &nbsp;·&nbsp; Expiry: {exp}</div>', unsafe_allow_html=True)

        # OI chart
        calls_oi = calls.nlargest(15,"openInterest")[["strike","openInterest"]].sort_values("strike")
        puts_oi  = puts.nlargest(15,"openInterest")[["strike","openInterest"]].sort_values("strike")
        fig_oi = go.Figure()
        fig_oi.add_bar(x=calls_oi["strike"], y=calls_oi["openInterest"],  name="Call OI", marker_color="#26d97f", opacity=0.8)
        fig_oi.add_bar(x=puts_oi["strike"],  y=-puts_oi["openInterest"],  name="Put OI",  marker_color="#e84040", opacity=0.8)
        fig_oi.add_vline(x=price, line_dash="dash", line_color="#f0c040", annotation_text=f"${price:.2f}")
        t = {**PLOTLY_THEME, "margin": dict(l=40,r=20,t=40,b=40)}
        fig_oi.update_layout(**t, height=260, title="Open Interest (Calls up / Puts down)", barmode="overlay")
        st.plotly_chart(fig_oi, use_container_width=True)

        cc, cp = st.columns(2)
        for col, df_c, label in [(cc,calls,"CALLS"),(cp,puts,"PUTS")]:
            with col:
                st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;text-transform:uppercase;letter-spacing:0.2em;color:#3d5068;margin-bottom:0.4rem;">{label}</div>', unsafe_allow_html=True)
                st.markdown('<div class="chain-hdr"><span>Strike</span><span>Bid</span><span>Ask</span><span>Last</span><span>OI</span><span>IV</span></div>', unsafe_allow_html=True)
                show = df_c.nlargest(15,"openInterest").sort_values("strike")
                for _, r in show.iterrows():
                    atm = abs(r["strike"]-price)/price < 0.02
                    cls = "chain-row chain-atm" if atm else "chain-row"
                    iv_str = f"{r['impliedVolatility']*100:.0f}%" if pd.notna(r.get("impliedVolatility")) else "—"
                    oi_str = f"{int(r['openInterest']):,}" if pd.notna(r.get("openInterest")) else "—"
                    st.markdown(f'<div class="{cls}"><span style="font-weight:700;color:#e8edf2">${r["strike"]:.0f}</span><span style="color:#e84040">${r["bid"]:.2f}</span><span style="color:#26d97f">${r["ask"]:.2f}</span><span style="color:#8896ab">${r["lastPrice"]:.2f}</span><span style="color:#4da6ff">{oi_str}</span><span style="color:#f0c040">{iv_str}</span></div>', unsafe_allow_html=True)

# ─── TAB 2: PLAY ADVISOR ─────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="sec-t">Options Play Advisor — Find Your Best Setup</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:#8896ab;margin-bottom:1.2rem;line-height:1.8;">Enter your view on the stock and current market conditions. The advisor scores every major strategy and tells you which play fits best, what to buy/sell, and why.</div>', unsafe_allow_html=True)

    pa1, pa2 = st.columns(2)
    with pa1:
        pa_ticker  = st.text_input("Ticker", value="AAPL", key="pa_tick").upper().strip()
        pa_view    = st.selectbox("Your directional view", ["Strongly Bullish","Mildly Bullish","Neutral / Range-bound","Mildly Bearish","Strongly Bearish"])
        pa_horizon = st.selectbox("Time horizon", ["1–2 weeks","1 month","2–3 months","6+ months"])
        pa_iv_view = st.selectbox("IV expectation (will volatility expand or contract?)", ["IV will expand (earnings/catalyst coming)","IV will stay flat","IV will contract (after catalyst)"])
    with pa2:
        pa_capital = st.number_input("Max capital to risk ($)", value=1000, min_value=50, step=100)
        pa_risk    = st.selectbox("Risk tolerance", ["Conservative — defined risk only","Moderate — willing to sell premium","Aggressive — naked strategies OK"])
        pa_reason  = st.text_area("Why are you interested in this trade? (optional)", height=80,
                                   placeholder="e.g. Earnings in 2 weeks, broken out of resistance, sector rotation...")

    analyze_btn = st.button("Analyze and Find Best Play", type="primary")

    if analyze_btn and pa_ticker:
        with st.spinner(f"Analyzing {pa_ticker}..."):
            try:
                tk    = yf.Ticker(pa_ticker)
                price = tk.fast_info.last_price or 0
                exps  = tk.options
                chain = tk.option_chain(exps[0]) if exps else None
                hist  = tk.history(period="3mo")
                if isinstance(hist.columns, pd.MultiIndex): hist.columns = hist.columns.get_level_values(0)

                # Compute realized vol
                closes = hist["Close"].to_numpy(dtype=float)
                log_r  = np.diff(np.log(closes))
                realized_vol = float(np.std(log_r) * np.sqrt(252) * 100)

                # Get ATM IV from chain
                atm_iv = 30.0
                if chain is not None:
                    atm_calls = chain.calls[abs(chain.calls["strike"] - price) < price * 0.05]
                    if not atm_calls.empty and "impliedVolatility" in atm_calls.columns:
                        atm_iv = float(atm_calls["impliedVolatility"].mean() * 100)

                iv_rank = "HIGH" if atm_iv > realized_vol * 1.2 else ("LOW" if atm_iv < realized_vol * 0.8 else "FAIR")

                # Score strategies based on inputs
                bull = pa_view in ["Strongly Bullish","Mildly Bullish"]
                bear = pa_view in ["Strongly Bearish","Mildly Bearish"]
                strong = pa_view in ["Strongly Bullish","Strongly Bearish"]
                neutral = pa_view == "Neutral / Range-bound"
                iv_up   = "expand" in pa_iv_view
                iv_down = "contract" in pa_iv_view
                short_term = "week" in pa_horizon
                conservative = "Conservative" in pa_risk

                def score_play(name):
                    s = 50
                    if name == "Long Call":
                        if bull: s += 20
                        if strong: s += 15
                        if iv_up: s += 10
                        if iv_down: s -= 20
                        if short_term: s -= 10
                        if conservative: s -= 15
                    elif name == "Bull Call Spread":
                        if bull: s += 25
                        if iv_up: s -= 5
                        if iv_down: s += 10
                        if conservative: s += 15
                    elif name == "Long Put":
                        if bear: s += 20
                        if strong: s += 15
                        if iv_up: s += 10
                        if iv_down: s -= 20
                        if conservative: s -= 15
                    elif name == "Bear Put Spread":
                        if bear: s += 25
                        if conservative: s += 15
                        if iv_down: s += 10
                    elif name == "Covered Call":
                        if bull: s += 5
                        if iv_down: s += 15
                        if iv_rank == "HIGH": s += 20
                        if conservative: s += 20
                    elif name == "Cash-Secured Put":
                        if bull: s += 10
                        if iv_rank == "HIGH": s += 20
                        if iv_down: s += 10
                        if conservative: s += 15
                    elif name == "Iron Condor":
                        if neutral: s += 30
                        if iv_rank == "HIGH": s += 20
                        if iv_down: s += 15
                        if conservative: s += 10
                    elif name == "Long Straddle":
                        if iv_up: s += 30
                        if strong: s += 10
                        if iv_rank == "LOW": s += 15
                        if iv_down: s -= 30
                        if iv_rank == "HIGH": s -= 20
                    elif name == "Long Strangle":
                        if iv_up: s += 25
                        if neutral: s += 10
                        if iv_rank == "LOW": s += 10
                        if iv_down: s -= 25
                    elif name == "PMCC (Poor Man's Covered Call)":
                        if bull: s += 15
                        if not short_term: s += 15
                        if conservative: s += 10
                    return min(max(s, 0), 100)

                PLAYS = [
                    ("Long Call", "#26d97f",
                     "Buy an OTM or ATM call. Best when you expect a strong directional move. Risk = premium paid only. Choose strike 5-10% OTM for leverage, ATM for higher delta."),
                    ("Bull Call Spread", "#26d97f",
                     "Buy lower call + sell higher call. Cuts cost vs naked call. Caps upside but also caps risk. Best for moderate bullish moves with defined target."),
                    ("Long Put", "#e84040",
                     "Buy an OTM put. Best for bearish bets or portfolio hedging. Risk = premium only. Profits accelerate if stock falls sharply."),
                    ("Bear Put Spread", "#e84040",
                     "Buy higher put + sell lower put. Cheaper than naked put. Best for moderate bearish moves with a clear downside target."),
                    ("Covered Call", "#f0c040",
                     "Own stock + sell OTM call. Collect premium income. Caps upside. Best when IV is high and you want to reduce cost basis on a stock you already own."),
                    ("Cash-Secured Put", "#4da6ff",
                     "Sell put with cash reserved to buy stock. Collect premium. If stock falls to strike you buy it at a discount. Best when IV is elevated and you want to enter a long position cheaper."),
                    ("Iron Condor", "#a78bfa",
                     "Sell OTM strangle + buy wings. Collect premium if stock stays in range. Best in high-IV, low-movement environments. Profit zone = between your short strikes."),
                    ("Long Straddle", "#f0c040",
                     "Buy ATM call + ATM put. Profit from a large move in either direction. Needs a BIG move to be profitable. Best before earnings when IV is low but a move is expected."),
                    ("Long Strangle", "#f0c040",
                     "Buy OTM call + OTM put. Cheaper than straddle. Needs even bigger move to profit. Good before major catalysts."),
                    ("PMCC (Poor Man's Covered Call)", "#4da6ff",
                     "Buy deep ITM LEAPS call + sell near-term OTM call. Acts like a covered call but uses far less capital. Best for long-term bullish plays with income overlay."),
                ]

                scored = sorted([(name, color, desc, score_play(name)) for name,color,desc in PLAYS],
                                key=lambda x: x[3], reverse=True)
                st.session_state["pa_results"] = scored
                st.session_state["pa_price"]   = price
                st.session_state["pa_iv"]       = atm_iv
                st.session_state["pa_rvol"]     = realized_vol
                st.session_state["pa_iv_rank"]  = iv_rank
                st.session_state["pa_ticker"]   = pa_ticker
            except Exception as e:
                st.error(f"Error: {e}")

    if "pa_results" in st.session_state:
        price     = st.session_state["pa_price"]
        atm_iv    = st.session_state["pa_iv"]
        rv        = st.session_state["pa_rvol"]
        iv_rank   = st.session_state["pa_iv_rank"]
        sym       = st.session_state["pa_ticker"]
        results   = st.session_state["pa_results"]

        # Situation summary
        iv_color = {"HIGH":"#e84040","LOW":"#26d97f","FAIR":"#f0c040"}[iv_rank]
        st.markdown(f"""
        <div class="advisor-card" style="--accent:{iv_color}">
            <div class="advisor-title" style="color:{iv_color}">{sym} — IV is {iv_rank}</div>
            <div class="advisor-sub">
                Current price: <strong style="color:#e8edf2">${price:.2f}</strong> &nbsp;·&nbsp;
                ATM IV: <strong style="color:{iv_color}">{atm_iv:.0f}%</strong> &nbsp;·&nbsp;
                Realized Vol (90d): <strong style="color:#8896ab">{rv:.0f}%</strong><br>
                {
                "HIGH IV means options are expensive — favour SELLING premium (iron condor, covered call, CSP). Buying options is costly." if iv_rank=="HIGH"
                else "LOW IV means options are cheap — favour BUYING options (long call, long put, straddle). Great time to be long premium before a catalyst."
                if iv_rank=="LOW"
                else "IV is roughly fair value — focus on direction rather than IV edge."
                }
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sec-t">Strategy Rankings for Your Setup</div>', unsafe_allow_html=True)
        for rank, (name, color, desc, score) in enumerate(results, 1):
            bar_color = "#26d97f" if score >= 70 else "#f0c040" if score >= 50 else "#3d5068"
            st.markdown(f"""
            <div class="play-row">
                <div class="play-rank">#{rank}</div>
                <div style="flex:1">
                    <div class="play-name" style="color:{color}">{name}</div>
                    <div class="play-why">{desc}</div>
                    <div class="score-bar" style="width:{score}%;background:{bar_color};margin-top:0.5rem"></div>
                </div>
                <div class="play-score" style="color:{bar_color}">{score}</div>
            </div>
            """, unsafe_allow_html=True)

# ─── TAB 3: BLACK-SCHOLES ────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="sec-t">Black-Scholes Pricer + Full Greeks</div>', unsafe_allow_html=True)
    ba, bb = st.columns(2)
    with ba:
        bs_s = st.number_input("Stock Price ($)", value=150.00, format="%.2f")
        bs_k = st.number_input("Strike Price ($)", value=155.00, format="%.2f")
        bs_t = st.number_input("Days to Expiry", value=30, min_value=1)
    with bb:
        bs_v = st.slider("Implied Volatility (%)", 5, 200, 25) / 100
        bs_r = st.slider("Risk-Free Rate (%)", 0.0, 10.0, 5.0, 0.1) / 100
        opt_type = st.radio("Option Type", ["Call","Put"], horizontal=True)

    T = bs_t / 365
    if T > 0 and bs_v > 0 and bs_s > 0 and bs_k > 0:
        d1 = (math.log(bs_s/bs_k) + (bs_r + 0.5*bs_v**2)*T) / (bs_v*math.sqrt(T))
        d2 = d1 - bs_v*math.sqrt(T)
        call_p = bs_s*norm.cdf(d1) - bs_k*math.exp(-bs_r*T)*norm.cdf(d2)
        put_p  = bs_k*math.exp(-bs_r*T)*norm.cdf(-d2) - bs_s*norm.cdf(-d1)
        price_out = call_p if opt_type=="Call" else put_p
        delta = norm.cdf(d1) if opt_type=="Call" else norm.cdf(d1)-1
        gamma = norm.pdf(d1)/(bs_s*bs_v*math.sqrt(T))
        theta = (-(bs_s*norm.pdf(d1)*bs_v/(2*math.sqrt(T))) - bs_r*bs_k*math.exp(-bs_r*T)*(norm.cdf(d2) if opt_type=="Call" else norm.cdf(-d2)))/365
        vega  = bs_s*norm.pdf(d1)*math.sqrt(T)/100

        st.markdown(f"""<div class="greek-grid">
            <div class="greek-cell"><div class="greek-val" style="color:{'#26d97f' if opt_type=='Call' else '#e84040'}">${price_out:.3f}</div><div class="greek-lbl">{opt_type} Price</div></div>
            <div class="greek-cell"><div class="greek-val" style="color:#4da6ff">{delta:.4f}</div><div class="greek-lbl">Delta</div></div>
            <div class="greek-cell"><div class="greek-val" style="color:#a78bfa">{gamma:.5f}</div><div class="greek-lbl">Gamma</div></div>
            <div class="greek-cell"><div class="greek-val" style="color:#e84040">${theta:.4f}</div><div class="greek-lbl">Theta/day</div></div>
            <div class="greek-cell"><div class="greek-val" style="color:#f0c040">${vega:.4f}</div><div class="greek-lbl">Vega/1%IV</div></div>
        </div>""", unsafe_allow_html=True)

        iv_range = np.linspace(0.05, 1.0, 60)
        prices_c, prices_p = [], []
        for iv in iv_range:
            d1_ = (math.log(bs_s/bs_k)+(bs_r+0.5*iv**2)*T)/(iv*math.sqrt(T))
            d2_ = d1_ - iv*math.sqrt(T)
            prices_c.append(bs_s*norm.cdf(d1_)-bs_k*math.exp(-bs_r*T)*norm.cdf(d2_))
            prices_p.append(bs_k*math.exp(-bs_r*T)*norm.cdf(-d2_)-bs_s*norm.cdf(-d1_))
        fig_iv = go.Figure()
        fig_iv.add_scatter(x=iv_range*100, y=prices_c, name="Call", line=dict(color="#26d97f",width=2))
        fig_iv.add_scatter(x=iv_range*100, y=prices_p, name="Put",  line=dict(color="#e84040",width=2))
        fig_iv.add_vline(x=bs_v*100, line_dash="dash", line_color="#f0c040",
                         annotation_text=f"Current IV {bs_v*100:.0f}%")
        t2 = {**PLOTLY_THEME, "margin": dict(l=48,r=16,t=40,b=40)}
        fig_iv.update_layout(**t2, height=260, title="Option Price vs IV",
                             xaxis_title="IV (%)", yaxis_title="Price ($)")
        st.plotly_chart(fig_iv, use_container_width=True)

# ─── TAB 4: STRATEGY GUIDE ────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="sec-t">Options Strategy Reference</div>', unsafe_allow_html=True)
    strategies = [
        ("Long Call",         "Bullish",         "Beginner",    "#26d97f", "Buy a call. Max loss = premium. Profit if stock moves strongly higher. Pick ATM for high delta, OTM for leverage."),
        ("Long Put",          "Bearish",         "Beginner",    "#e84040", "Buy a put. Profit if stock falls. Defined risk. Useful for hedging a long portfolio or a pure directional bearish bet."),
        ("Covered Call",      "Neutral-Bullish", "Beginner",    "#26d97f", "Own stock + sell OTM call. Collect premium. Caps upside. Best when IV is high and you want income from a position you hold."),
        ("Cash-Secured Put",  "Neutral-Bullish", "Intermediate","#4da6ff", "Sell put with cash reserve. Collect premium. If assigned you buy stock at strike (which you wanted anyway). Best when IV is elevated."),
        ("Bull Call Spread",  "Bullish",         "Intermediate","#26d97f", "Buy lower call + sell higher call. Defined risk and reward. Cheaper than naked call. Best with a clear upside target."),
        ("Bear Put Spread",   "Bearish",         "Intermediate","#e84040", "Buy higher put + sell lower put. Defined risk bearish play. Cheaper than long put. Best with a clear downside target."),
        ("Iron Condor",       "Neutral",         "Advanced",    "#a78bfa", "Sell OTM strangle + buy wings. Profit if stock stays in range. Best in high-IV environments where you expect little movement."),
        ("Long Straddle",     "High Volatility", "Advanced",    "#f0c040", "Buy ATM call + put. Profit from a large move in either direction. Needs a BIG move. Best before low-IV earnings."),
        ("Long Strangle",     "High Volatility", "Advanced",    "#f0c040", "Buy OTM call + OTM put. Cheaper than straddle but needs even bigger move. Good before major catalysts."),
        ("PMCC",              "Bullish",         "Advanced",    "#4da6ff", "Buy deep ITM LEAPS + sell near-term OTM call. Acts like covered call with much less capital. Best for long-term bulls who want income."),
    ]
    for name, bias, level, color, desc in strategies:
        lvl_c = {"Beginner":"#26d97f","Intermediate":"#f0c040","Advanced":"#e84040"}[level]
        st.markdown(f"""<div class="strat-card">
            <div class="strat-name" style="color:{color}">{name}</div>
            <div class="strat-desc">{desc}</div>
            <div>
                <div class="sbadge" style="background:{color}15;color:{color};border:1px solid {color}30">{bias}</div>
                <div class="sbadge" style="background:{lvl_c}15;color:{lvl_c};border:1px solid {lvl_c}30">{level}</div>
            </div>
        </div>""", unsafe_allow_html=True)

st.set_page_config(page_title="Options Chain | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
st.markdown("""<style>
.ph{background:linear-gradient(135deg,#141a1f,#111820);border:1px solid #243040;border-radius:16px;padding:2.5rem 3rem;margin-bottom:2rem;position:relative;overflow:hidden}
.ph::before{content:'';position:absolute;top:-40px;right:-40px;width:160px;height:160px;background:radial-gradient(circle,rgba(167,139,250,0.07),transparent 70%);pointer-events:none}
.ph h1{font-family:'Bebas Neue',sans-serif;font-size:3.2rem;letter-spacing:0.05em;line-height:1;margin:0 0 0.5rem 0}
.ph p{font-family:'IBM Plex Mono',monospace;font-size:0.72rem;color:#8896ab;line-height:1.8;margin:0}
.ph-ey{font-family:'IBM Plex Mono',monospace;font-size:0.52rem;text-transform:uppercase;letter-spacing:0.3em;color:#3d5068;margin-bottom:0.5rem}
.sec-t{font-family:'IBM Plex Mono',monospace;font-size:0.52rem;text-transform:uppercase;letter-spacing:0.25em;color:#3d5068;padding:1.2rem 0 0.7rem;border-top:1px solid #1e2830}
.bm{background:#141a1f;border:1px solid #243040;border-radius:12px;padding:1.4rem 1.6rem;transition:border-color 0.2s}
.bm:hover{border-color:#2e3d50}
.bm-v{font-family:'Bebas Neue',sans-serif;font-size:2.2rem;letter-spacing:0.04em;line-height:1}
.bm-l{font-family:'IBM Plex Mono',monospace;font-size:0.5rem;text-transform:uppercase;letter-spacing:0.2em;color:#3d5068;margin-top:0.35rem}
.bm-s{font-family:'IBM Plex Mono',monospace;font-size:0.62rem;color:#8896ab;margin-top:0.15rem}
.chain-hdr{display:grid;grid-template-columns:80px 70px 70px 80px 70px 70px;gap:8px;padding:0.6rem 1rem;background:#1a2230;font-family:'IBM Plex Mono',monospace;font-size:0.5rem;text-transform:uppercase;letter-spacing:0.15em;color:#3d5068;border-radius:6px 6px 0 0}
.chain-row{display:grid;grid-template-columns:80px 70px 70px 80px 70px 70px;gap:8px;padding:0.7rem 1rem;border-bottom:1px solid #141a1f;font-family:'IBM Plex Mono',monospace;font-size:0.72rem;transition:background 0.12s;align-items:center}
.chain-row:hover{background:rgba(255,255,255,0.02)}
.chain-atm{background:rgba(38,217,127,0.04)!important}
.strat-card{background:#141a1f;border:1px solid #243040;border-radius:12px;padding:1.4rem 1.6rem;margin-bottom:0.6rem;display:flex;align-items:flex-start;gap:2rem;transition:border-color 0.2s,transform 0.15s}
.strat-card:hover{border-color:#2e3d50;transform:translateX(4px)}
.strat-name{font-family:'Bebas Neue',sans-serif;font-size:1.4rem;letter-spacing:0.05em;min-width:200px}
.strat-desc{font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:#8896ab;line-height:1.7;flex:1}
.sbadge{font-family:'IBM Plex Mono',monospace;font-size:0.48rem;text-transform:uppercase;letter-spacing:0.12em;padding:3px 10px;border-radius:4px;white-space:nowrap;display:block;margin-bottom:4px}
/* Play advisor */
.advisor-card{background:linear-gradient(135deg,#141a1f,#111820);border:1px solid #243040;border-radius:16px;padding:1.8rem 2rem;margin-bottom:1rem;position:relative;overflow:hidden;animation:fadeUp 0.4s ease both}
.advisor-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,var(--accent,#26d97f),transparent)}
.advisor-title{font-family:'Bebas Neue',sans-serif;font-size:1.8rem;letter-spacing:0.05em;margin-bottom:0.3rem}
.advisor-sub{font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:#8896ab;line-height:1.7;margin-bottom:1rem}
.greek-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:0.8rem;margin:1rem 0}
.greek-cell{background:#0f1318;border:1px solid #1e2830;border-radius:8px;padding:0.9rem;text-align:center}
.greek-val{font-family:'Bebas Neue',sans-serif;font-size:1.6rem;letter-spacing:0.03em}
.greek-lbl{font-family:'IBM Plex Mono',monospace;font-size:0.48rem;text-transform:uppercase;letter-spacing:0.15em;color:#3d5068;margin-top:0.2rem}
.play-row{display:flex;align-items:flex-start;gap:1.2rem;padding:0.9rem 1rem;border:1px solid #243040;border-radius:10px;margin-bottom:0.6rem;cursor:pointer;transition:background 0.15s,border-color 0.15s}
.play-row:hover{background:rgba(255,255,255,0.02);border-color:#2e3d50}
.play-rank{font-family:'Bebas Neue',sans-serif;font-size:2rem;color:#3d5068;min-width:36px}
.play-name{font-family:'Bebas Neue',sans-serif;font-size:1.3rem;letter-spacing:0.04em;margin-bottom:0.2rem}
.play-why{font-family:'IBM Plex Mono',monospace;font-size:0.65rem;color:#8896ab;line-height:1.6}
.play-score{font-family:'Bebas Neue',sans-serif;font-size:1.4rem;min-width:60px;text-align:right}
.score-bar{height:4px;border-radius:2px;margin-top:0.4rem}
</style>""", unsafe_allow_html=True)
navbar()

st.markdown("""<div class="ph"><div class="ph-ey">Options Trading</div><h1>Options Chain</h1>
<p>Live chain with OI chart, full Greeks, Black-Scholes pricer, and an AI-style Play Advisor that tells you which options strategy fits the current setup.</p></div>""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["Live Chain", "Play Advisor", "Black-Scholes", "Strategy Guide"])

# ─── TAB 1: LIVE CHAIN ────────────────────────────────────────────────────────
with tab1:
    c1, c2 = st.columns([2, 4])
    with c1: ot = st.text_input("Ticker", value="AAPL", placeholder="AAPL, TSLA, SPY").upper().strip()
    with c2:
        st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.68rem;color:#3d5068;padding-top:1.9rem;">Live data from Yahoo Finance. Green = ATM strike. Sorted by open interest.</div>', unsafe_allow_html=True)

    exp_sel = None
    if st.button("Load Options Chain", type="primary"):
        with st.spinner(f"Loading {ot}..."):
            try:
                tk    = yf.Ticker(ot)
                price = tk.fast_info.last_price or 0
                exps  = tk.options
                if not exps: st.error("No options found."); st.stop()
                st.session_state.update({"opt_sym":ot,"opt_price":price,"opt_exps":list(exps),"opt_exp":exps[0]})
                chain = tk.option_chain(exps[0])
                st.session_state.update({"opt_calls":chain.calls,"opt_puts":chain.puts})
            except Exception as e: st.error(f"Error: {e}")

    if "opt_exps" in st.session_state:
        ec1, ec2 = st.columns([3,5])
        with ec1:
            new_exp = st.selectbox("Expiry date", st.session_state["opt_exps"],
                                    index=st.session_state["opt_exps"].index(st.session_state["opt_exp"]))
        if new_exp != st.session_state["opt_exp"]:
            with st.spinner("Loading..."):
                try:
                    chain = yf.Ticker(st.session_state["opt_sym"]).option_chain(new_exp)
                    st.session_state.update({"opt_exp":new_exp,"opt_calls":chain.calls,"opt_puts":chain.puts})
                    st.rerun()
                except: pass

    if "opt_calls" in st.session_state:
        price = st.session_state["opt_price"]
        calls = st.session_state["opt_calls"]
        puts  = st.session_state["opt_puts"]
        sym   = st.session_state["opt_sym"]
        exp   = st.session_state["opt_exp"]

        st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.8rem;color:#26d97f;margin:1rem 0 0.5rem;"><strong>{sym}</strong> @ ${price:.2f} &nbsp;·&nbsp; Expiry: {exp}</div>', unsafe_allow_html=True)

        # OI chart
        calls_oi = calls.nlargest(15,"openInterest")[["strike","openInterest"]].sort_values("strike")
        puts_oi  = puts.nlargest(15,"openInterest")[["strike","openInterest"]].sort_values("strike")
        fig_oi = go.Figure()
        fig_oi.add_bar(x=calls_oi["strike"], y=calls_oi["openInterest"],  name="Call OI", marker_color="#26d97f", opacity=0.8)
        fig_oi.add_bar(x=puts_oi["strike"],  y=-puts_oi["openInterest"],  name="Put OI",  marker_color="#e84040", opacity=0.8)
        fig_oi.add_vline(x=price, line_dash="dash", line_color="#f0c040", annotation_text=f"${price:.2f}")
        t = {**PLOTLY_THEME, "margin": dict(l=40,r=20,t=40,b=40)}
        fig_oi.update_layout(**t, height=260, title="Open Interest (Calls up / Puts down)", barmode="overlay")
        st.plotly_chart(fig_oi, use_container_width=True)

        cc, cp = st.columns(2)
        for col, df_c, label in [(cc,calls,"CALLS"),(cp,puts,"PUTS")]:
            with col:
                st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.58rem;text-transform:uppercase;letter-spacing:0.2em;color:#3d5068;margin-bottom:0.4rem;">{label}</div>', unsafe_allow_html=True)
                st.markdown('<div class="chain-hdr"><span>Strike</span><span>Bid</span><span>Ask</span><span>Last</span><span>OI</span><span>IV</span></div>', unsafe_allow_html=True)
                show = df_c.nlargest(15,"openInterest").sort_values("strike")
                for _, r in show.iterrows():
                    atm = abs(r["strike"]-price)/price < 0.02
                    cls = "chain-row chain-atm" if atm else "chain-row"
                    iv_str = f"{r['impliedVolatility']*100:.0f}%" if pd.notna(r.get("impliedVolatility")) else "—"
                    oi_str = f"{int(r['openInterest']):,}" if pd.notna(r.get("openInterest")) else "—"
                    st.markdown(f'<div class="{cls}"><span style="font-weight:700;color:#e8edf2">${r["strike"]:.0f}</span><span style="color:#e84040">${r["bid"]:.2f}</span><span style="color:#26d97f">${r["ask"]:.2f}</span><span style="color:#8896ab">${r["lastPrice"]:.2f}</span><span style="color:#4da6ff">{oi_str}</span><span style="color:#f0c040">{iv_str}</span></div>', unsafe_allow_html=True)

# ─── TAB 2: PLAY ADVISOR ─────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="sec-t">Options Play Advisor — Find Your Best Setup</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.72rem;color:#8896ab;margin-bottom:1.2rem;line-height:1.8;">Enter your view on the stock and current market conditions. The advisor scores every major strategy and tells you which play fits best, what to buy/sell, and why.</div>', unsafe_allow_html=True)

    pa1, pa2 = st.columns(2)
    with pa1:
        pa_ticker  = st.text_input("Ticker", value="AAPL", key="pa_tick").upper().strip()
        pa_view    = st.selectbox("Your directional view", ["Strongly Bullish","Mildly Bullish","Neutral / Range-bound","Mildly Bearish","Strongly Bearish"])
        pa_horizon = st.selectbox("Time horizon", ["1–2 weeks","1 month","2–3 months","6+ months"])
        pa_iv_view = st.selectbox("IV expectation (will volatility expand or contract?)", ["IV will expand (earnings/catalyst coming)","IV will stay flat","IV will contract (after catalyst)"])
    with pa2:
        pa_capital = st.number_input("Max capital to risk ($)", value=1000, min_value=50, step=100)
        pa_risk    = st.selectbox("Risk tolerance", ["Conservative — defined risk only","Moderate — willing to sell premium","Aggressive — naked strategies OK"])
        pa_reason  = st.text_area("Why are you interested in this trade? (optional)", height=80,
                                   placeholder="e.g. Earnings in 2 weeks, broken out of resistance, sector rotation...")

    analyze_btn = st.button("Analyze and Find Best Play", type="primary")

    if analyze_btn and pa_ticker:
        with st.spinner(f"Analyzing {pa_ticker}..."):
            try:
                tk    = yf.Ticker(pa_ticker)
                price = tk.fast_info.last_price or 0
                exps  = tk.options
                chain = tk.option_chain(exps[0]) if exps else None
                hist  = tk.history(period="3mo")
                if isinstance(hist.columns, pd.MultiIndex): hist.columns = hist.columns.get_level_values(0)

                # Compute realized vol
                closes = hist["Close"].to_numpy(dtype=float)
                log_r  = np.diff(np.log(closes))
                realized_vol = float(np.std(log_r) * np.sqrt(252) * 100)

                # Get ATM IV from chain
                atm_iv = 30.0
                if chain is not None:
                    atm_calls = chain.calls[abs(chain.calls["strike"] - price) < price * 0.05]
                    if not atm_calls.empty and "impliedVolatility" in atm_calls.columns:
                        atm_iv = float(atm_calls["impliedVolatility"].mean() * 100)

                iv_rank = "HIGH" if atm_iv > realized_vol * 1.2 else ("LOW" if atm_iv < realized_vol * 0.8 else "FAIR")

                # Score strategies based on inputs
                bull = pa_view in ["Strongly Bullish","Mildly Bullish"]
                bear = pa_view in ["Strongly Bearish","Mildly Bearish"]
                strong = pa_view in ["Strongly Bullish","Strongly Bearish"]
                neutral = pa_view == "Neutral / Range-bound"
                iv_up   = "expand" in pa_iv_view
                iv_down = "contract" in pa_iv_view
                short_term = "week" in pa_horizon
                conservative = "Conservative" in pa_risk

                def score_play(name):
                    s = 50
                    if name == "Long Call":
                        if bull: s += 20
                        if strong: s += 15
                        if iv_up: s += 10
                        if iv_down: s -= 20
                        if short_term: s -= 10
                        if conservative: s -= 15
                    elif name == "Bull Call Spread":
                        if bull: s += 25
                        if iv_up: s -= 5
                        if iv_down: s += 10
                        if conservative: s += 15
                    elif name == "Long Put":
                        if bear: s += 20
                        if strong: s += 15
                        if iv_up: s += 10
                        if iv_down: s -= 20
                        if conservative: s -= 15
                    elif name == "Bear Put Spread":
                        if bear: s += 25
                        if conservative: s += 15
                        if iv_down: s += 10
                    elif name == "Covered Call":
                        if bull: s += 5
                        if iv_down: s += 15
                        if iv_rank == "HIGH": s += 20
                        if conservative: s += 20
                    elif name == "Cash-Secured Put":
                        if bull: s += 10
                        if iv_rank == "HIGH": s += 20
                        if iv_down: s += 10
                        if conservative: s += 15
                    elif name == "Iron Condor":
                        if neutral: s += 30
                        if iv_rank == "HIGH": s += 20
                        if iv_down: s += 15
                        if conservative: s += 10
                    elif name == "Long Straddle":
                        if iv_up: s += 30
                        if strong: s += 10
                        if iv_rank == "LOW": s += 15
                        if iv_down: s -= 30
                        if iv_rank == "HIGH": s -= 20
                    elif name == "Long Strangle":
                        if iv_up: s += 25
                        if neutral: s += 10
                        if iv_rank == "LOW": s += 10
                        if iv_down: s -= 25
                    elif name == "PMCC (Poor Man's Covered Call)":
                        if bull: s += 15
                        if not short_term: s += 15
                        if conservative: s += 10
                    return min(max(s, 0), 100)

                PLAYS = [
                    ("Long Call", "#26d97f",
                     "Buy an OTM or ATM call. Best when you expect a strong directional move. Risk = premium paid only. Choose strike 5-10% OTM for leverage, ATM for higher delta."),
                    ("Bull Call Spread", "#26d97f",
                     "Buy lower call + sell higher call. Cuts cost vs naked call. Caps upside but also caps risk. Best for moderate bullish moves with defined target."),
                    ("Long Put", "#e84040",
                     "Buy an OTM put. Best for bearish bets or portfolio hedging. Risk = premium only. Profits accelerate if stock falls sharply."),
                    ("Bear Put Spread", "#e84040",
                     "Buy higher put + sell lower put. Cheaper than naked put. Best for moderate bearish moves with a clear downside target."),
                    ("Covered Call", "#f0c040",
                     "Own stock + sell OTM call. Collect premium income. Caps upside. Best when IV is high and you want to reduce cost basis on a stock you already own."),
                    ("Cash-Secured Put", "#4da6ff",
                     "Sell put with cash reserved to buy stock. Collect premium. If stock falls to strike you buy it at a discount. Best when IV is elevated and you want to enter a long position cheaper."),
                    ("Iron Condor", "#a78bfa",
                     "Sell OTM strangle + buy wings. Collect premium if stock stays in range. Best in high-IV, low-movement environments. Profit zone = between your short strikes."),
                    ("Long Straddle", "#f0c040",
                     "Buy ATM call + ATM put. Profit from a large move in either direction. Needs a BIG move to be profitable. Best before earnings when IV is low but a move is expected."),
                    ("Long Strangle", "#f0c040",
                     "Buy OTM call + OTM put. Cheaper than straddle. Needs even bigger move to profit. Good before major catalysts."),
                    ("PMCC (Poor Man's Covered Call)", "#4da6ff",
                     "Buy deep ITM LEAPS call + sell near-term OTM call. Acts like a covered call but uses far less capital. Best for long-term bullish plays with income overlay."),
                ]

                scored = sorted([(name, color, desc, score_play(name)) for name,color,desc in PLAYS],
                                key=lambda x: x[3], reverse=True)
                st.session_state["pa_results"] = scored
                st.session_state["pa_price"]   = price
                st.session_state["pa_iv"]       = atm_iv
                st.session_state["pa_rvol"]     = realized_vol
                st.session_state["pa_iv_rank"]  = iv_rank
                st.session_state["pa_ticker"]   = pa_ticker
            except Exception as e:
                st.error(f"Error: {e}")

    if "pa_results" in st.session_state:
        price     = st.session_state["pa_price"]
        atm_iv    = st.session_state["pa_iv"]
        rv        = st.session_state["pa_rvol"]
        iv_rank   = st.session_state["pa_iv_rank"]
        sym       = st.session_state["pa_ticker"]
        results   = st.session_state["pa_results"]

        # Situation summary
        iv_color = {"HIGH":"#e84040","LOW":"#26d97f","FAIR":"#f0c040"}[iv_rank]
        st.markdown(f"""
        <div class="advisor-card" style="--accent:{iv_color}">
            <div class="advisor-title" style="color:{iv_color}">{sym} — IV is {iv_rank}</div>
            <div class="advisor-sub">
                Current price: <strong style="color:#e8edf2">${price:.2f}</strong> &nbsp;·&nbsp;
                ATM IV: <strong style="color:{iv_color}">{atm_iv:.0f}%</strong> &nbsp;·&nbsp;
                Realized Vol (90d): <strong style="color:#8896ab">{rv:.0f}%</strong><br>
                {
                "HIGH IV means options are expensive — favour SELLING premium (iron condor, covered call, CSP). Buying options is costly." if iv_rank=="HIGH"
                else "LOW IV means options are cheap — favour BUYING options (long call, long put, straddle). Great time to be long premium before a catalyst."
                if iv_rank=="LOW"
                else "IV is roughly fair value — focus on direction rather than IV edge."
                }
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sec-t">Strategy Rankings for Your Setup</div>', unsafe_allow_html=True)
        for rank, (name, color, desc, score) in enumerate(results, 1):
            bar_color = "#26d97f" if score >= 70 else "#f0c040" if score >= 50 else "#3d5068"
            st.markdown(f"""
            <div class="play-row">
                <div class="play-rank">#{rank}</div>
                <div style="flex:1">
                    <div class="play-name" style="color:{color}">{name}</div>
                    <div class="play-why">{desc}</div>
                    <div class="score-bar" style="width:{score}%;background:{bar_color};margin-top:0.5rem"></div>
                </div>
                <div class="play-score" style="color:{bar_color}">{score}</div>
            </div>
            """, unsafe_allow_html=True)

# ─── TAB 3: BLACK-SCHOLES ────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="sec-t">Black-Scholes Pricer + Full Greeks</div>', unsafe_allow_html=True)
    ba, bb = st.columns(2)
    with ba:
        bs_s = st.number_input("Stock Price ($)", value=150.00, format="%.2f")
        bs_k = st.number_input("Strike Price ($)", value=155.00, format="%.2f")
        bs_t = st.number_input("Days to Expiry", value=30, min_value=1)
    with bb:
        bs_v = st.slider("Implied Volatility (%)", 5, 200, 25) / 100
        bs_r = st.slider("Risk-Free Rate (%)", 0.0, 10.0, 5.0, 0.1) / 100
        opt_type = st.radio("Option Type", ["Call","Put"], horizontal=True)

    T = bs_t / 365
    if T > 0 and bs_v > 0 and bs_s > 0 and bs_k > 0:
        d1 = (math.log(bs_s/bs_k) + (bs_r + 0.5*bs_v**2)*T) / (bs_v*math.sqrt(T))
        d2 = d1 - bs_v*math.sqrt(T)
        call_p = bs_s*norm.cdf(d1) - bs_k*math.exp(-bs_r*T)*norm.cdf(d2)
        put_p  = bs_k*math.exp(-bs_r*T)*norm.cdf(-d2) - bs_s*norm.cdf(-d1)
        price_out = call_p if opt_type=="Call" else put_p
        delta = norm.cdf(d1) if opt_type=="Call" else norm.cdf(d1)-1
        gamma = norm.pdf(d1)/(bs_s*bs_v*math.sqrt(T))
        theta = (-(bs_s*norm.pdf(d1)*bs_v/(2*math.sqrt(T))) - bs_r*bs_k*math.exp(-bs_r*T)*(norm.cdf(d2) if opt_type=="Call" else norm.cdf(-d2)))/365
        vega  = bs_s*norm.pdf(d1)*math.sqrt(T)/100

        st.markdown(f"""<div class="greek-grid">
            <div class="greek-cell"><div class="greek-val" style="color:{'#26d97f' if opt_type=='Call' else '#e84040'}">${price_out:.3f}</div><div class="greek-lbl">{opt_type} Price</div></div>
            <div class="greek-cell"><div class="greek-val" style="color:#4da6ff">{delta:.4f}</div><div class="greek-lbl">Delta</div></div>
            <div class="greek-cell"><div class="greek-val" style="color:#a78bfa">{gamma:.5f}</div><div class="greek-lbl">Gamma</div></div>
            <div class="greek-cell"><div class="greek-val" style="color:#e84040">${theta:.4f}</div><div class="greek-lbl">Theta/day</div></div>
            <div class="greek-cell"><div class="greek-val" style="color:#f0c040">${vega:.4f}</div><div class="greek-lbl">Vega/1%IV</div></div>
        </div>""", unsafe_allow_html=True)

        iv_range = np.linspace(0.05, 1.0, 60)
        prices_c, prices_p = [], []
        for iv in iv_range:
            d1_ = (math.log(bs_s/bs_k)+(bs_r+0.5*iv**2)*T)/(iv*math.sqrt(T))
            d2_ = d1_ - iv*math.sqrt(T)
            prices_c.append(bs_s*norm.cdf(d1_)-bs_k*math.exp(-bs_r*T)*norm.cdf(d2_))
            prices_p.append(bs_k*math.exp(-bs_r*T)*norm.cdf(-d2_)-bs_s*norm.cdf(-d1_))
        fig_iv = go.Figure()
        fig_iv.add_scatter(x=iv_range*100, y=prices_c, name="Call", line=dict(color="#26d97f",width=2))
        fig_iv.add_scatter(x=iv_range*100, y=prices_p, name="Put",  line=dict(color="#e84040",width=2))
        fig_iv.add_vline(x=bs_v*100, line_dash="dash", line_color="#f0c040",
                         annotation_text=f"Current IV {bs_v*100:.0f}%")
        t2 = {**PLOTLY_THEME, "margin": dict(l=48,r=16,t=40,b=40)}
        fig_iv.update_layout(**t2, height=260, title="Option Price vs IV",
                             xaxis_title="IV (%)", yaxis_title="Price ($)")
        st.plotly_chart(fig_iv, use_container_width=True)

# ─── TAB 4: STRATEGY GUIDE ────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="sec-t">Options Strategy Reference</div>', unsafe_allow_html=True)
    strategies = [
        ("Long Call",         "Bullish",         "Beginner",    "#26d97f", "Buy a call. Max loss = premium. Profit if stock moves strongly higher. Pick ATM for high delta, OTM for leverage."),
        ("Long Put",          "Bearish",         "Beginner",    "#e84040", "Buy a put. Profit if stock falls. Defined risk. Useful for hedging a long portfolio or a pure directional bearish bet."),
        ("Covered Call",      "Neutral-Bullish", "Beginner",    "#26d97f", "Own stock + sell OTM call. Collect premium. Caps upside. Best when IV is high and you want income from a position you hold."),
        ("Cash-Secured Put",  "Neutral-Bullish", "Intermediate","#4da6ff", "Sell put with cash reserve. Collect premium. If assigned you buy stock at strike (which you wanted anyway). Best when IV is elevated."),
        ("Bull Call Spread",  "Bullish",         "Intermediate","#26d97f", "Buy lower call + sell higher call. Defined risk and reward. Cheaper than naked call. Best with a clear upside target."),
        ("Bear Put Spread",   "Bearish",         "Intermediate","#e84040", "Buy higher put + sell lower put. Defined risk bearish play. Cheaper than long put. Best with a clear downside target."),
        ("Iron Condor",       "Neutral",         "Advanced",    "#a78bfa", "Sell OTM strangle + buy wings. Profit if stock stays in range. Best in high-IV environments where you expect little movement."),
        ("Long Straddle",     "High Volatility", "Advanced",    "#f0c040", "Buy ATM call + put. Profit from a large move in either direction. Needs a BIG move. Best before low-IV earnings."),
        ("Long Strangle",     "High Volatility", "Advanced",    "#f0c040", "Buy OTM call + OTM put. Cheaper than straddle but needs even bigger move. Good before major catalysts."),
        ("PMCC",              "Bullish",         "Advanced",    "#4da6ff", "Buy deep ITM LEAPS + sell near-term OTM call. Acts like covered call with much less capital. Best for long-term bulls who want income."),
    ]
    for name, bias, level, color, desc in strategies:
        lvl_c = {"Beginner":"#26d97f","Intermediate":"#f0c040","Advanced":"#e84040"}[level]
        st.markdown(f"""<div class="strat-card">
            <div class="strat-name" style="color:{color}">{name}</div>
            <div class="strat-desc">{desc}</div>
            <div>
                <div class="sbadge" style="background:{color}15;color:{color};border:1px solid {color}30">{bias}</div>
                <div class="sbadge" style="background:{lvl_c}15;color:{lvl_c};border:1px solid {lvl_c}30">{level}</div>
            </div>
        </div>""", unsafe_allow_html=True)
