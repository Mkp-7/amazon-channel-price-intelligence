"""
Run this from the project root in VS Code terminal:
    python test_api.py

Tests your RapidAPI key and shows exactly what the API returns.
"""

import sys
import os
import re
import requests

# ── Paste your key here OR pass as argument ───────────────────────
RAPIDAPI_KEY = ""   # <-- paste your key between the quotes

# Also accepts key as command-line arg:  python test_api.py YOUR_KEY_HERE
if len(sys.argv) > 1:
    RAPIDAPI_KEY = sys.argv[1].strip()

# ─────────────────────────────────────────────────────────────────
TEST_ASIN = "B00IGETSNC"   # Rx Clear Chlorine Tablets — real product
URL       = "https://real-time-amazon-data.p.rapidapi.com/product-details"

def print_section(title):
    print(f"\n{'='*55}")
    print(f"  {title}")
    print('='*55)

def run_test(key, asin=TEST_ASIN):
    print_section(f"Testing ASIN: {asin}")

    if not key:
        print("❌ No API key provided.")
        print("   Either paste it into RAPIDAPI_KEY in this file,")
        print("   or run:  python test_api.py YOUR_KEY_HERE")
        return

    print(f"   Key: {key[:8]}...{key[-4:]}  ({len(key)} chars)")

    headers = {
        "X-RapidAPI-Key":  key.strip(),
        "X-RapidAPI-Host": "real-time-amazon-data.p.rapidapi.com",
    }
    params = {"asin": asin, "country": "US"}

    print(f"\n📡 Calling: {URL}")
    print(f"   Params:  {params}")

    try:
        r = requests.get(URL, headers=headers, params=params, timeout=20)
    except requests.exceptions.Timeout:
        print("❌ Request timed out (20s). Check your internet connection.")
        return
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        return
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return

    print(f"\n📬 HTTP Status: {r.status_code}")

    # ── Status-specific guidance ──────────────────────────────────
    if r.status_code == 401:
        print("❌ 401 Unauthorized — key is invalid or copied wrong.")
        print("   Fix: go to rapidapi.com → your app → Security → copy key again.")
        return

    if r.status_code == 403:
        print("❌ 403 Forbidden — key works but not subscribed to this API.")
        print("   Fix:")
        print("   1. Go to https://rapidapi.com/letscrape-6bRBa3QguO5/api/real-time-amazon-data")
        print("   2. Click 'Subscribe to Test' (blue button)")
        print("   3. Select Basic / Free plan (50 req/month, no card)")
        print("   4. Run this test again.")
        return

    if r.status_code == 429:
        print("⏳ 429 Too Many Requests — free quota (50/month) exhausted.")
        print("   Resets on your RapidAPI billing date.")
        return

    if r.status_code != 200:
        print(f"❌ Unexpected status {r.status_code}")
        print(f"   Response: {r.text[:400]}")
        return

    # ── Parse response ────────────────────────────────────────────
    try:
        body = r.json()
    except Exception:
        print(f"❌ Response is not JSON:\n{r.text[:400]}")
        return

    print("✅ Got valid JSON response")
    print(f"\n📦 Top-level keys: {list(body.keys())}")

    # Navigate to data object
    d = body.get("data") or body.get("product") or body
    if isinstance(d, dict):
        print(f"📦 Data-level keys: {list(d.keys())}")
    else:
        print(f"⚠️  Data is not a dict: {type(d)} — value: {str(d)[:200]}")
        return

    # Try all known price field names
    price_fields = ["product_price","price","buybox_price","current_price","product_original_price"]
    print("\n💰 Checking price fields:")
    found_price = None
    for field in price_fields:
        val = d.get(field)
        status = f"  → {val}" if val else "  (empty)"
        print(f"   {field:35s} {status}")
        if val and not found_price:
            found_price = val

    if found_price:
        cleaned = str(found_price).replace(",","").replace("$","").strip()
        m = re.search(r"\d+\.?\d*", cleaned)
        parsed = float(m.group()) if m else None
        print(f"\n✅ Price parsed: ${parsed}")
    else:
        print("\n⚠️  No price found in any known field.")
        print("   The API may use a different field name.")
        print("   Check 'Data-level keys' above and look for a price-related field.")

    # Show other useful fields
    print("\n📋 Other useful fields:")
    useful = ["product_title","title","product_star_rating","rating",
              "product_num_ratings","reviews_count","product_availability"]
    for field in useful:
        val = d.get(field)
        if val:
            print(f"   {field}: {str(val)[:60]}")

    print_section("SUMMARY")
    if found_price:
        print(f"✅ API key works!")
        print(f"   Product : {d.get('product_title','N/A')[:50]}")
        print(f"   Price   : ${parsed}")
        print(f"   Rating  : {d.get('product_star_rating','N/A')}")
        print(f"   Reviews : {d.get('product_num_ratings','N/A')}")
        print("\n👉 Go back to Streamlit and click '🔄 Refresh Live Prices'")
    else:
        print("⚠️  Connected but price not parsed — check fields above.")

    print()


if __name__ == "__main__":
    run_test(RAPIDAPI_KEY)
