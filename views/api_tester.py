import streamlit as st
from data.products import test_api_key, fetch_live_amazon_price

def show():
    st.title("🔧 API Key Tester")
    st.caption("Diagnose your RapidAPI key — see exactly what the API returns")

    rapidapi_key = st.session_state.get("rapidapi_key_global", "")

    if not rapidapi_key:
        st.warning("⚠️ No RapidAPI key found. Enter it in the sidebar under **🔑 API Keys**.")
        st.markdown("""
**How to get your free RapidAPI key:**
1. Go to [rapidapi.com](https://rapidapi.com/letscrape-6bRBa3QguO5/api/real-time-amazon-data)
2. Click **Subscribe to Test** → choose **Basic (Free)** — 50 requests/month, no credit card
3. Go to **Endpoints** → click any endpoint → your key appears in the code panel on the right under `X-RapidAPI-Key`
4. Copy and paste it into the sidebar
""")
        return

    st.info(f"🔑 Key loaded: `{rapidapi_key[:8]}...{rapidapi_key[-4:]}` ({len(rapidapi_key)} chars)")

    col1, col2 = st.columns(2)
    run_test = col1.button("🧪 Run Diagnostic Test", type="primary")
    
    # Manual ASIN test
    st.markdown("---")
    st.subheader("🔍 Test a Specific ASIN")
    test_asin = st.text_input("Enter any Amazon ASIN to test:", value="B00IGETSNC",
                               help="B00IGETSNC = Rx Clear Chlorine Tablets (a real product)")
    run_asin = st.button("Fetch This ASIN →")

    if run_test:
        with st.spinner("Testing API key with ASIN B00IGETSNC..."):
            result = test_api_key(rapidapi_key)

        st.markdown("---")
        st.subheader("📋 Diagnostic Result")

        if result["ok"]:
            st.success("✅ API key works! Connection successful.")
        else:
            st.error(f"❌ API call failed — HTTP {result['status_code']}")

        c1, c2, c3 = st.columns(3)
        c1.metric("HTTP Status", result["status_code"] or "N/A")
        c2.metric("Price Found", result.get("price_raw") or "None")
        c3.metric("Key Length",  len(rapidapi_key))

        if result.get("top_keys"):
            st.markdown(f"**Top-level response keys:** `{result['top_keys']}`")
        if result.get("data_keys"):
            st.markdown(f"**Data object keys:** `{result['data_keys']}`")
        if result.get("error"):
            st.code(result["error"], language="text")

        # Specific guidance based on result
        st.markdown("---")
        st.subheader("💡 What to Do Next")
        code = result["status_code"]
        if result["ok"] and result.get("price_raw"):
            st.success("Everything works. Go to Dashboard and click **🔄 Refresh Live Prices**.")
        elif result["ok"] and not result.get("price_raw"):
            st.warning(
                "API connected but price field not found in the response. "
                "The API may have changed its response structure. "
                f"Fields returned: `{result.get('data_keys', [])}`"
            )
        elif code == 403:
            st.error(
                "**403 Forbidden** — Most common cause: you haven't subscribed to this specific API.\n\n"
                "Fix:\n"
                "1. Go to [this exact URL](https://rapidapi.com/letscrape-6bRBa3QguO5/api/real-time-amazon-data)\n"
                "2. Click **Subscribe to Test** (blue button)\n"
                "3. Select **Basic / Free** plan\n"
                "4. Confirm subscription\n"
                "5. Come back here and test again"
            )
        elif code == 401:
            st.error(
                "**401 Unauthorized** — Key is invalid or copied incorrectly.\n\n"
                "Fix:\n"
                "1. Go to [rapidapi.com/developer/apps](https://rapidapi.com/developer/apps)\n"
                "2. Click your app → **Security** → copy the key again\n"
                "3. Make sure there are no spaces before/after the key"
            )
        elif code == 429:
            st.warning("**429 Too Many Requests** — You've used all 50 free requests this month. Resets on your billing date.")
        else:
            st.info("Check the error details above. If stuck, try regenerating your key at rapidapi.com.")

    if run_asin and test_asin.strip():
        with st.spinner(f"Fetching ASIN {test_asin.strip()}..."):
            data, err = fetch_live_amazon_price(test_asin.strip(), rapidapi_key)

        st.markdown("---")
        st.subheader(f"📦 Result for ASIN `{test_asin.strip()}`")
        if err:
            st.error(f"Error: {err}")
        else:
            st.success("✅ Fetch successful!")
            c1, c2, c3 = st.columns(3)
            c1.metric("Price",   f"${data['amazon_price']}" if data.get("amazon_price") else "Not found")
            c2.metric("Rating",  data.get("rating") or "N/A")
            c3.metric("Reviews", data.get("reviews") or "N/A")
            if data.get("title"):
                st.markdown(f"**Title:** {data['title']}")
            if data.get("raw_fields"):
                st.warning(f"Price not parsed. Raw fields: `{data['raw_fields']}`")
