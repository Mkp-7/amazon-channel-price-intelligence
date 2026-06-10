import streamlit as st
from data.products import get_all_products_with_analysis, get_listing_scores, PRODUCTS, get_live_prices

def show():
    st.title("🏊 PoolPrice AI — Amazon Channel Dashboard")
    st.caption("Amazon channel intelligence for a pool supply store · Real products · Live pricing")

    # Keys come from app.py sidebar — just read session state here
    rapidapi_key = st.session_state.get("rapidapi_key_global", "")
    refresh = False

    if rapidapi_key:
        refresh = st.button("🔄 Refresh Live Prices", help="Force fresh fetch from Amazon (uses 1 API request per product)")

    # Load live prices
    live_data = {}
    if rapidapi_key:
        with st.spinner("Loading Amazon prices (cached 6 h to protect free quota)..."):
            live_data = get_live_prices(rapidapi_key, force_refresh=refresh)
        live_count = sum(1 for v in live_data.values() if v.get("amazon_price"))
        if live_count:
            st.success(f"✅ Live Amazon prices loaded for {live_count}/{len(PRODUCTS)} products")
        else:
            st.warning("⚠️ Could not fetch live prices — check your RapidAPI key. Showing estimates.")
    else:
        st.info("💡 Add your **RapidAPI key** in the sidebar to unlock live Amazon prices.")

    st.markdown("---")

    products_df = get_all_products_with_analysis(live_data)
    listings_df = get_listing_scores()

    need_lower    = len(products_df[products_df["Action"] == "🔴 Lower Price"])
    can_raise     = len(products_df[products_df["Action"] == "🟢 Raise Price"])
    poor_listings = len(listings_df[listings_df["Health"] == "🔴 Poor"])
    avg_rating    = round(listings_df["Rating"].mean(), 1)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("SKUs Tracked", len(PRODUCTS))
    c2.metric("🔴 Overpriced", need_lower, delta=f"{need_lower} need action", delta_color="inverse")
    c3.metric("🟢 Can Raise",  can_raise,  delta=f"{can_raise} opportunity")
    c4.metric("🔴 Poor Listings", poor_listings, delta="needs fixing", delta_color="inverse")
    c5.metric("Avg Amazon Rating", avg_rating)

    st.markdown("---")
    st.subheader("📋 Full Pricing Action Board")
    st.caption("🟢 Live = real Amazon price  |  ⚠️ Est. = estimated (add RapidAPI key for live data)")

    def color_action(val):
        if "Lower" in str(val): return "background-color:#ffe0e0;color:#900"
        if "Raise" in str(val): return "background-color:#e0ffe0;color:#060"
        return "background-color:#fffbe0;color:#660"

    def color_gap(val):
        try:
            v = float(val)
            if v > 8:  return "color:#c00;font-weight:bold"
            if v < -5: return "color:#060;font-weight:bold"
        except: pass
        return ""

    styled = (
        products_df.style
        .map(color_action, subset=["Action"])
        .map(color_gap,    subset=["Gap (%)"])
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("💡 Key Insights")
    ca, cb = st.columns(2)
    with ca:
        st.error(f"**{need_lower} products** priced above Amazon — at risk of losing Buy Box.")
        st.success(f"**{can_raise} products** priced below Amazon — margin improvement opportunity.")
    with cb:
        st.warning(f"**{poor_listings} listings** score below 4/7 — suppressing organic rank.")
        st.info("**Peak season (Jun–Aug)** is active — consider 5–10% increases on high-demand SKUs.")
