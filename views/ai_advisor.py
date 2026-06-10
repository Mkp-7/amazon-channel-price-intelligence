import streamlit as st
from agents.groq_agent import get_pricing_advice, chat_with_agent, analyze_listing
from data.products import PRODUCTS, SEASONAL_DEMAND, get_listing_scores, get_live_prices
from datetime import datetime

def show():
    st.title("🤖 AI Pricing Advisor")
    st.caption("Powered by Groq (Llama 3) — Free, fast, no credit card required")

    api_key      = st.session_state.get("groq_key_global", "")
    rapidapi_key = st.session_state.get("rapidapi_key_global", "")

    if not api_key:
        st.warning("⚠️ Enter your **Groq API key** in the sidebar (🔑 API Keys) to activate the AI advisor.")
        st.info(
            "**How to get a free Groq key (30 seconds):**\n"
            "1. Go to [console.groq.com](https://console.groq.com)\n"
            "2. Sign up with email — **no credit card needed**\n"
            "3. Click **API Keys → Create API Key**\n"
            "4. Paste it in the sidebar under 🔑 API Keys\n\n"
            "Free tier: **14,400 requests/day** — more than enough!"
        )
        return

    tab1, tab2, tab3 = st.tabs(["💬 Chat Advisor", "📦 Product Analysis", "📋 Listing AI Review"])

    # ── TAB 1: Chat ──────────────────────────────────────────────
    with tab1:
        st.subheader("💬 Ask the AI Pricing Advisor")
        st.caption("Ask anything about Amazon pricing, seasonal strategy, or competitor tactics.")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if not st.session_state.chat_history:
            st.markdown("**Try asking:**")
            examples = [
                "What's the best pricing strategy for chlorine tablets in peak summer?",
                "How do I win the Amazon Buy Box for pool chemicals?",
                "Should we lower prices during pool closing season?",
                "What makes a good Amazon listing for pool equipment?",
            ]
            cols = st.columns(2)
            for i, ex in enumerate(examples):
                if cols[i % 2].button(ex, key=f"ex_{i}"):
                    st.session_state.chat_history.append({"role": "user", "content": ex})
                    with st.spinner("Thinking..."):
                        reply = chat_with_agent([], ex, api_key)
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})
                    st.rerun()

        user_input = st.chat_input("Ask about pricing strategy, Amazon tactics, seasonality...")
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.spinner("AI is analyzing..."):
                reply = chat_with_agent(st.session_state.chat_history[:-1], user_input, api_key)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.rerun()

        if st.session_state.chat_history:
            if st.button("🗑️ Clear chat"):
                st.session_state.chat_history = []
                st.rerun()

    # ── TAB 2: Product Analysis ──────────────────────────────────
    with tab2:
        st.subheader("📦 AI Product Pricing Analysis")
        st.caption("Select any product and get a data-driven pricing recommendation from the AI.")

        product_names = [p["name"] for p in PRODUCTS]
        selected_name = st.selectbox("Choose a product:", product_names, key="ai_product")
        selected      = next(p for p in PRODUCTS if p["name"] == selected_name)

        current_month = datetime.now().month
        season_demand = SEASONAL_DEMAND.get(selected["category"], {}).get(current_month, 1.0)

        # Use live price if available, else estimate
        live_data = get_live_prices(rapidapi_key) if rapidapi_key else {}
        live      = live_data.get(selected["asin"], {})
        amz_price = live.get("amazon_price")

        c1, c2, c3 = st.columns(3)
        c1.metric("Our Price", f"${selected['our_price']}")
        if amz_price:
            c2.metric("Amazon Price", f"${amz_price:,.2f}", delta="live ✅")
        else:
            c2.metric("Amazon Price", "N/A — add RapidAPI key")
        c3.metric("Seasonal Demand", f"{season_demand}x",
                  delta="peak" if season_demand >= 1.5 else "normal")

        comp_dict = {"Amazon": amz_price or selected["our_price"] * 0.97}

        if st.button("🤖 Get AI Recommendation", type="primary"):
            with st.spinner("AI is analyzing pricing data..."):
                advice = get_pricing_advice(
                    product_name=selected["name"],
                    our_price=selected["our_price"],
                    competitor_data=comp_dict,
                    season_demand=season_demand,
                    api_key=api_key,
                )
            st.markdown("---")
            st.subheader("🎯 AI Recommendation")
            st.markdown(advice)

    # ── TAB 3: Listing AI Review ─────────────────────────────────
    with tab3:
        st.subheader("📋 AI Listing Improvement Advisor")
        st.caption("Get AI-powered advice on how to improve low-scoring Amazon listings.")

        listings_df   = get_listing_scores()
        poor_listings = listings_df[listings_df["Health"] != "🟢 Good"]

        if poor_listings.empty:
            st.success("All listings are in good shape!")
            return

        listing_choice = st.selectbox(
            "Select a listing to improve:",
            poor_listings["Product"].tolist(),
            key="ai_listing",
        )
        row       = listings_df[listings_df["Product"] == listing_choice].iloc[0]
        score_val = int(row["Score"].split("/")[0])

        issues = []
        if row["Bullet Points"]    == "❌": issues.append("missing bullet points")
        if row["5+ Images"]        == "❌": issues.append("fewer than 5 images")
        if row["A+ Content"]       == "❌": issues.append("no A+ content")
        if row["100+ Reviews"]     == "❌": issues.append("under 100 reviews")
        if row["Rating ≥4.2"]      == "❌": issues.append(f"low rating ({row['Rating']})")
        if row["Prime"]            == "❌": issues.append("not Prime eligible")
        if row["Keyword in Title"] == "❌": issues.append("missing keywords in title")

        c1, c2 = st.columns(2)
        c1.metric("Listing Score", row["Score"])
        c2.metric("Health Status", row["Health"])

        if issues:
            st.warning("**Issues found:** " + ", ".join(issues))

        if st.button("🤖 Get AI Fix Plan", type="primary"):
            with st.spinner("AI is reviewing this listing..."):
                advice = analyze_listing(listing_choice, score_val, issues, api_key)
            st.markdown("---")
            st.subheader("🎯 AI Improvement Plan")
            st.markdown(advice)
