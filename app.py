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

# ── Groq - loaded silently from Streamlit secrets, never shown to user ──
try:
    st.session_state["groq_key_global"] = st.secrets["GROQ_KEY"]
except Exception:
    st.session_state["groq_key_global"] = ""

# ── RapidAPI - user enters this in the sidebar ──────────────────
with st.sidebar.expander("🔑 Enter API Key", expanded=True):
    st.text_input(
        "RapidAPI Key (live Amazon prices)",
        type="password",
        key="rapidapi_key_global",
        placeholder="Paste your RapidAPI key here...",
    )
    st.caption("[Get key →](https://rapidapi.com/letscrape-6bRBa3QguO5/api/real-time-amazon-data)")

    if st.session_state.get("rapidapi_key_global"):
        st.success("✅ Live Amazon prices active")
    else:
        st.warning("Add key above for live Amazon prices")

# ── Navigation ────────────────────────────────────────────────────
page = st.sidebar.radio(
    "Navigate",
    ["🏠 Dashboard", "🔍 Price Scanner", "📊 Seasonal Planner",
     "✅ Listing Checker", "🤖 AI Advisor"],
)

st.sidebar.markdown("---")

# ── Route to views (not pages/ - avoids Streamlit auto-nav) ──────
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
