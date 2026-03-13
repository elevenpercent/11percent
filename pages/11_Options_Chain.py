import streamlit as st, sys, os, math, pandas as pd, numpy as np
import yfinance as yf, plotly.graph_objects as go
from scipy.stats import norm
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import SHARED_CSS, PLOTLY_THEME; from utils.nav import navbar

st.set_page_config(page_title="Options Chain | 11%", layout="wide", initial_sidebar_state="collapsed")
st.markdown(SHARED_CSS, unsafe_allow_html=True)
st.markdown("""<style>
.ph{background:linear-gradient(135deg,#0c1018,#0d1420);border:1px solid #1a2235;border-radius:16px;padding:2.5rem 3rem;margin-bottom:2rem}
.ph h1{font-family:'Bebas Neue',sans-serif;font-size:3.5rem;letter-spacing:0.05em;line-height:1;margin:0 0 0.5rem 0}
.ph p{font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#8896ab;line-height:1.8;margin:0}
.ph-ey{font-family:'IBM Plex Mono',monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.3em;color:#3a4a5e;margin-bottom:0.5rem}
.sec-t{font-family:'IBM Plex Mono',monospace;font-size:0.55rem;text-transform:uppercase;letter-spacing:0.25em;color:#3a4a5e;padding:1.2rem 0 0.8rem;border-top:1px solid #0d1117}
.bm{background:#0c1018;border:1px solid #1a2235;border-radius:12px;padding:1.5rem 1.8rem;transition:border-color 0.2s}
.bm:hover{border-color:#2a3550}
.bm-v{font-family:'Bebas Neue',sans-serif;font-size:2.4rem;letter-spacing:0.04em;line-height:1}
.bm-l{font-family:'IBM Plex Mono',monospace;font-size:0.5rem;text-transform:uppercase;letter-spacing:0.22em;color:#3a4a5e;margin-top:0.35rem}
.bm-s{font-family:'IBM Plex Mono',monospace;font-size:0.62rem;color:#8896ab;margin-top:0.15rem}
.chain-hdr{display:grid;grid-template-columns:80px 70px 70px 80px 70px 70px;gap:8px;padding:0.6rem 1rem;background:#0d1117;font-family:'IBM Plex Mono',monospace;font-size:0.5rem;text-transform:uppercase;letter-spacing:0.15em;color:#3a4a5e;border-radius:6px 6px 0 0}
.chain-row{display:grid;grid-template-columns:80px 70px 70px 80px 70px 70px;gap:8px;padding:0.7rem 1rem;border-bottom:1px solid #0d1117;font-family:'IBM Plex Mono',monospace;font-size:0.72rem;transition:background 0.12s;align-items:center}
.chain-row:hover{background:rgba(255,255,255,0.02)}
.chain-atm{background:rgba(0,230,118,0.04)!important;border-color:rgba(0,230,118,0.15)!important}
.strat-card{background:#0c1018;border:1px solid #1a2235;border-radius:12px;padding:1.4rem 1.6rem;margin-bottom:0.6rem;display:flex;align-items:flex-start;gap:2rem;transition:border-color 0.2s}
.strat-card:hover{border-color:#2a3550}
.strat-name{font-family:'Bebas Neue',sans-serif;font-size:1.5rem;letter-spacing:0.05em;min-width:200px}
.strat-desc{font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:#8896ab;line-height:1.7;flex:1}
.sbadge{font-family:'IBM Plex Mono',monospace;font-size:0.48rem;text-transform:uppercase;letter-spacing:0.12em;padding:3px 10px;border-radius:4px;white-space:nowrap;display:block;margin-bottom:4px}
</style>""", unsafe_allow_html=True)
navbar()

st.markdown("""<div class="ph"><div class="ph-ey">Options Trading</div><h1>Options Chain</h1>
<p>Live options chain with open interest chart, Black-Scholes pricing, full Greeks, and strategy guides. Understand what you are buying before you buy it.</p></div>""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Live Chain", "Black-Scholes Calculator", "Strategy Guide"])

# ─── TAB 1 ────────────────────────────────────────────────────────────────────
with tab1:
    c1, c2 = st.columns([2, 4])
    with c1: ot = st.text_input("Ticker", value="AAPL").upper().strip()
    with c2: st.markdown('<div style="font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:#3a4a5e;padding-top:1.9rem;">Live data from Yahoo Finance. ATM strike highlighted. Sorted by open interest.</div>', unsafe_allow_html=True)

    if st.button("Load Options Chain", type="primary"):
        with st.spinner(f"Loading {ot} options..."):
            try:
                tk = yf.Ticker(ot)
                price = tk.fast_info.last_price or 0
                exps  = tk.options
                if not exps: st.error("No options found."); st.stop()
                chain = tk.option_chain(exps[0])
                st.session_state.update({"opt_calls":chain.calls,"opt_puts":chain.puts,
                                         "opt_price":price,"opt_exp":exps[0],"opt_sym":ot})
            except Exception as e: st.error(f"Error: {e}")

    if "opt_calls" in st.session_state:
        price = st.session_state["opt_price"]
        exp   = st.session_state["opt_exp"]
        calls = st.session_state["opt_calls"]
        puts  = st.session_state["opt_puts"]
        sym   = st.session_state["opt_sym"]

        st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.82rem;color:#00e676;margin:1rem 0 0.5rem;"><strong>{sym}</strong> @ ${price:.2f} &nbsp;·&nbsp; Expiry: {exp}</div>', unsafe_allow_html=True)

        # OI chart
        calls_oi = calls.nlargest(15,"openInterest")[["strike","openInterest"]].sort_values("strike")
        puts_oi  = puts.nlargest(15,"openInterest")[["strike","openInterest"]].sort_values("strike")
        fig_oi = go.Figure()
        fig_oi.add_bar(x=calls_oi["strike"], y=calls_oi["openInterest"],  name="Call OI", marker_color="#00e676", opacity=0.8)
        fig_oi.add_bar(x=puts_oi["strike"],  y=-puts_oi["openInterest"],  name="Put OI",  marker_color="#ff3d57", opacity=0.8)
        fig_oi.add_vline(x=price, line_dash="dash", line_color="#ffd166", annotation_text=f"${price:.2f}")
        fig_oi.update_layout(**PLOTLY_THEME, height=280, title="Open Interest by Strike (Calls up / Puts down)",
                             barmode="overlay", xaxis_title="Strike")
        st.plotly_chart(fig_oi, use_container_width=True)

        cc, cp = st.columns(2)
        for col, df_c, label in [(cc, calls, "CALLS"), (cp, puts, "PUTS")]:
            with col:
                st.markdown(f'<div style="font-family:IBM Plex Mono,monospace;font-size:0.6rem;text-transform:uppercase;letter-spacing:0.2em;color:#3a4a5e;margin-bottom:0.4rem;">{label}</div>', unsafe_allow_html=True)
                st.markdown('<div class="chain-hdr"><span>Strike</span><span>Bid</span><span>Ask</span><span>Last</span><span>OI</span><span>IV</span></div>', unsafe_allow_html=True)
                show = df_c.nlargest(15,"openInterest").sort_values("strike")
                for _, r in show.iterrows():
                    is_atm = abs(r["strike"]-price)/price < 0.02
                    row_cls = "chain-row chain-atm" if is_atm else "chain-row"
                    iv_str = f"{r['impliedVolatility']*100:.0f}%" if pd.notna(r.get("impliedVolatility")) else "—"
                    oi_str = f"{int(r['openInterest']):,}" if pd.notna(r.get("openInterest")) else "—"
                    strike_str = f"${r['strike']:.0f}"
                    bid_str = f"${r['bid']:.2f}"
                    ask_str = f"${r['ask']:.2f}"
                    last_str = f"${r['lastPrice']:.2f}"
                    st.markdown(f'<div class="{row_cls}"><span style="font-weight:700;color:#eef2f7">{strike_str}</span><span style="color:#ff3d57">{bid_str}</span><span style="color:#00e676">{ask_str}</span><span style="color:#8896ab">{last_str}</span><span style="color:#4da6ff">{oi_str}</span><span style="color:#ffd166">{iv_str}</span></div>', unsafe_allow_html=True)

# ─── TAB 2 ────────────────────────────────────────────────────────────────────
with tab2:
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

        r1 = st.columns(3)
        r2 = st.columns(4)
        pcolor = "#00e676" if opt_type=="Call" else "#ff3d57"
        for col,(v,l,s,c) in zip(r1,[
            (f"${price_out:.3f}", f"{opt_type} Fair Value", "Black-Scholes model", pcolor),
            (f"${call_p:.3f}", "Call Price", "theoretical", "#00e676"),
            (f"${put_p:.3f}", "Put Price", "theoretical", "#ff3d57"),
        ]): col.markdown(f'<div class="bm"><div class="bm-v" style="color:{c}">{v}</div><div class="bm-l">{l}</div><div class="bm-s">{s}</div></div>', unsafe_allow_html=True)
        for col,(v,l,s,c) in zip(r2,[
            (f"{delta:.4f}", "Delta", "$ move per $1 stock", "#4da6ff"),
            (f"{gamma:.5f}", "Gamma", "delta change per $1", "#b388ff"),
            (f"${theta:.4f}", "Theta / day", "daily time decay", "#ff3d57"),
            (f"${vega:.4f}", "Vega (1% IV)", "volatility sensitivity", "#ffd166"),
        ]): col.markdown(f'<div class="bm"><div class="bm-v" style="color:{c}">{v}</div><div class="bm-l">{l}</div><div class="bm-s">{s}</div></div>', unsafe_allow_html=True)

        # IV vs Price chart
        iv_range = np.linspace(0.05, 1.0, 60)
        prices_c, prices_p = [], []
        for iv in iv_range:
            d1_ = (math.log(bs_s/bs_k)+(bs_r+0.5*iv**2)*T)/(iv*math.sqrt(T))
            d2_ = d1_ - iv*math.sqrt(T)
            prices_c.append(bs_s*norm.cdf(d1_)-bs_k*math.exp(-bs_r*T)*norm.cdf(d2_))
            prices_p.append(bs_k*math.exp(-bs_r*T)*norm.cdf(-d2_)-bs_s*norm.cdf(-d1_))
        fig_iv = go.Figure()
        fig_iv.add_scatter(x=iv_range*100, y=prices_c, name="Call", line=dict(color="#00e676", width=2))
        fig_iv.add_scatter(x=iv_range*100, y=prices_p, name="Put",  line=dict(color="#ff3d57", width=2))
        fig_iv.add_vline(x=bs_v*100, line_dash="dash", line_color="#ffd166",
                         annotation_text=f"Current IV {bs_v*100:.0f}%")
        fig_iv.update_layout(**PLOTLY_THEME, height=280, title="Option Price vs Implied Volatility",
                             xaxis_title="IV (%)", yaxis_title="Option Price ($)")
        st.plotly_chart(fig_iv, use_container_width=True)

# ─── TAB 3 ────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="sec-t">Common Options Strategies</div>', unsafe_allow_html=True)
    strategies = [
        ("Long Call",        "Bullish",         "Beginner",     "#00e676", "Buy a call option. Max loss = premium paid. Unlimited upside if stock moves strongly higher. Best used when you expect a large directional move within a defined window."),
        ("Long Put",         "Bearish",         "Beginner",     "#ff3d57", "Buy a put option. Profit if stock falls. Used for downside protection or as a pure bearish bet. Defined risk — you can only lose the premium."),
        ("Covered Call",     "Neutral-Bullish", "Beginner",     "#00e676", "Own 100 shares and sell a call. Collect premium income that reduces your cost basis. Caps your upside. Best in flat or slowly rising markets."),
        ("Cash-Secured Put", "Neutral-Bullish", "Intermediate", "#4da6ff", "Sell a put while holding cash to buy stock if assigned. Collect premium. If stock drops to strike you buy at a discount. High probability income trade."),
        ("Bull Call Spread",  "Bullish",         "Intermediate", "#00e676", "Buy lower call and sell higher call. Defined risk and reward. Much cheaper than a naked call. Best when you are moderately bullish with a clear upside target."),
        ("Bear Put Spread",   "Bearish",         "Intermediate", "#ff3d57", "Buy higher put and sell lower put. Defined risk bearish play. Cheaper than a long put. Best for moderate downside expectations."),
        ("Iron Condor",      "Neutral",         "Advanced",     "#b388ff", "Sell a strangle then buy wings for protection. Collect premium. Profit if stock stays in a defined range until expiry. High probability income strategy."),
        ("Long Straddle",    "High Volatility", "Advanced",     "#ffd166", "Buy call and put at the same strike. Profit from a large move in either direction. Expensive. Best before earnings or catalysts when direction is unknown."),
    ]
    for name, bias, level, color, desc in strategies:
        lvl_c = {"Beginner":"#00d68f","Intermediate":"#ffd166","Advanced":"#ff4757"}[level]
        st.markdown(f"""<div class="strat-card">
            <div class="strat-name" style="color:{color}">{name}</div>
            <div class="strat-desc">{desc}</div>
            <div>
                <div class="sbadge" style="background:{color}18;color:{color};border:1px solid {color}30">{bias}</div>
                <div class="sbadge" style="background:{lvl_c}18;color:{lvl_c};border:1px solid {lvl_c}30">{level}</div>
            </div>
        </div>""", unsafe_allow_html=True)
