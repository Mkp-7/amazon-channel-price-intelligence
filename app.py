import streamlit as st

st.set_page_config(
    page_title="PoolPrice AI Agent",
    page_icon="🏊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.image("https://img.icons8.com/fluency/96/swimming-pool.png", width=80)
st.sidebar.title("PoolPrice AI")
st.sidebar.caption("Amazon channel intelligence\nfor pool supply retailers")

# ── Global API Keys ───────────────────────────────────────────────
with st.sidebar.expander("🔑 API Keys", expanded=True):
    st.text_input(
        "RapidAPI Key (live Amazon prices)",
        type="password",
        key="rapidapi_key_global",
        placeholder="Paste key here...",
    )
    st.caption("[Get RapidAPI key →](https://rapidapi.com/letscrape-6bRBa3QguO5/api/real-time-amazon-data)")

    st.text_input(
        "Groq API Key (AI Advisor)",
        type="password",
        key="groq_key_global",
        placeholder="Paste key here...",
    )
    st.caption("[Get Groq key →](https://console.groq.com)")

    rapidapi_key = st.session_state.get("rapidapi_key_global", "")
    groq_key     = st.session_state.get("groq_key_global", "")
    if rapidapi_key and groq_key:
        st.success("✅ Both keys active")
    elif rapidapi_key:
        st.info("🟢 Live prices active · Add Groq for AI Advisor")
    elif groq_key:
        st.info("🤖 AI active · Add RapidAPI for live prices")
    else:
        st.warning("Add keys above to unlock all features")

# ── Navigation ────────────────────────────────────────────────────
page = st.sidebar.radio(
    "Navigate",
    ["🏠 Dashboard", "🔍 Price Scanner", "📊 Seasonal Planner",
     "✅ Listing Checker", "🤖 AI Advisor"],
)

st.sidebar.markdown("---")

# ── Route to views (not pages/ — avoids Streamlit auto-nav) ──────
if page == "🏠 Dashboard":
    from views import dashboard;        dashboard.show()
elif page == "🔍 Price Scanner":
    from views import price_scanner;    price_scanner.show()
elif page == "📊 Seasonal Planner":
    from views import seasonal_planner; seasonal_planner.show()
elif page == "✅ Listing Checker":
    from views import listing_checker;  listing_checker.show()
elif page == "🤖 AI Advisor":
    from views import ai_advisor;       ai_advisor.show()
