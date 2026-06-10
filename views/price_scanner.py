import streamlit as st
import plotly.graph_objects as go
from data.products import PRODUCTS, get_all_products_with_analysis, get_live_prices, SEASONAL_DEMAND
from datetime import datetime

def show():
    st.title("🔍 Competitor Price Scanner")
    st.caption("Live Amazon prices vs your store — 10 real pool supply SKUs")

    rapidapi_key = st.session_state.get("rapidapi_key_global", "")
    live_data = {}
    if rapidapi_key:
        live_data = get_live_prices(rapidapi_key)

    st.markdown("---")

    product_names = [p["name"] for p in PRODUCTS]
    selected_name = st.selectbox("Select product:", product_names)
    selected = next(p for p in PRODUCTS if p["name"] == selected_name)

    our       = selected["our_price"]
    asin      = selected["asin"]
    live      = live_data.get(asin, {})
    amz_price = live.get("amazon_price")
    current_month = datetime.now().month
    season    = SEASONAL_DEMAND.get(selected["category"], {}).get(current_month, 1.0)

    st.markdown(
        f"**Category:** {selected['category']} &nbsp;|&nbsp; "
        f"**ASIN:** `{asin}` &nbsp;|&nbsp; "
        f"**Our Price:** `${our}` &nbsp;|&nbsp; "
        f"**Season Index:** `{season}x`"
    )
    st.markdown(f"[🛍️ View on Amazon]({selected['amazon_url']})")

    st.markdown("---")

    if amz_price:
        gap     = round(our - amz_price, 2)
        gap_pct = round((our - amz_price) / amz_price * 100, 1)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Our Price",         f"${our:,.2f}")
        c2.metric("Amazon Buy Box",    f"${amz_price:,.2f}", delta=f"${gap:+.2f} vs us")
        c3.metric("Price Gap",         f"{gap_pct:+.1f}%")
        c4.metric("Seasonal Demand",   f"{season}x", delta="Peak 🔥" if season >= 1.5 else "Normal")

        st.markdown("---")
        st.subheader("📊 Price Comparison")
        fig = go.Figure()
        bars = [("Our Store", our, "#3b82f6"),
                ("Amazon Buy Box", amz_price, "#ef4444" if amz_price < our else "#22c55e")]
        fig.add_trace(go.Bar(
            x=[b[0] for b in bars],
            y=[b[1] for b in bars],
            marker_color=[b[2] for b in bars],
            text=[f"${b[1]:,.2f}" for b in bars],
            textposition="outside",
            width=0.4,
        ))
        fig.update_layout(
            height=320, yaxis_title="Price ($)", showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=20, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("🎯 Pricing Recommendation")
        if gap_pct > 8:
            st.error(
                f"🔴 **We are {gap_pct:.1f}% MORE expensive than Amazon.** "
                f"At risk of losing Buy Box. Consider lowering to **${amz_price * 0.99:,.2f}** "
                f"to match, or bundle to justify the premium."
            )
        elif gap_pct < -5:
            st.success(
                f"🟢 **We are {abs(gap_pct):.1f}% CHEAPER than Amazon.** "
                f"Opportunity to raise to **${amz_price * 0.97:,.2f}** and improve margin."
            )
            if season >= 1.5:
                st.info(f"📈 Peak season bonus: demand index {season}x — can push price higher during summer.")
        else:
            st.info(f"🟡 **Competitively priced** (within {abs(gap_pct):.1f}% of Amazon). Hold and monitor weekly.")

        if live.get("rating"):
            st.markdown(f"**Amazon Rating:** ⭐ {live['rating']}  |  **Reviews:** {live.get('reviews', 'N/A')}")
    else:
        st.warning("⚠️ No live Amazon price for this product. Add your RapidAPI key in the sidebar.")
        st.info(f"**Our Price:** ${our:,.2f}  |  **ASIN:** `{asin}`")

    st.markdown("---")
    st.subheader("📋 All 10 Products — Action Board")
    bulk_df = get_all_products_with_analysis(live_data).sort_values("Gap (%)", ascending=False)

    def color_action(val):
        if "Lower" in str(val): return "background-color:#ffe0e0;color:#900"
        if "Raise" in str(val): return "background-color:#e0ffe0;color:#060"
        return "background-color:#fffbe0;color:#660"

    st.dataframe(
        bulk_df.style.map(color_action, subset=["Action"]),
        use_container_width=True, hide_index=True
    )
