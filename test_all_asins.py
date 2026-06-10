"""
Run from project root:
    python test_all_asins.py YOUR_RAPIDAPI_KEY

Tests all 10 product ASINs one by one.
Paste the output back to Claude to fix any that fail.
"""
import sys, re, time, requests

KEY = sys.argv[1].strip() if len(sys.argv) > 1 else ""
if not KEY:
    print("Usage: python test_all_asins.py YOUR_KEY")
    sys.exit(1)

URL     = "https://real-time-amazon-data.p.rapidapi.com/product-details"
HEADERS = {
    "X-RapidAPI-Key":  KEY,
    "X-RapidAPI-Host": "real-time-amazon-data.p.rapidapi.com",
}

# Auto-load from products.py so this always stays in sync
sys.path.insert(0, ".")
from data.products import PRODUCTS

print(f"\n{'ID':<5} {'ASIN':<14} {'STATUS':<10} {'PRICE':<12} {'PRODUCT'}")
print("-" * 85)

working, failed = [], []

for p in PRODUCTS:
    pid, asin, name, our = p["id"], p["asin"], p["name"], p["our_price"]
    try:
        r = requests.get(URL, headers=HEADERS,
                         params={"asin": asin, "country": "US"}, timeout=20)
        if r.status_code == 200:
            d = r.json().get("data") or r.json().get("product") or r.json()
            raw = (d.get("product_price") or d.get("price") or
                   d.get("buybox_price")  or d.get("current_price") or "")
            price = None
            if raw:
                m = re.search(r"\d+\.?\d*", str(raw).replace(",","").replace("$",""))
                if m: price = float(m.group())
            if price:
                diff = round(our - price, 2)
                flag = "🔴" if diff > our*0.08 else ("🟢" if diff < -our*0.05 else "🟡")
                print(f"{pid:<5} {asin:<14} {'✅ OK':<10} ${price:<11.2f} {flag} {name[:45]}")
                working.append((pid, asin, name, price))
            else:
                fields = list(d.keys()) if isinstance(d, dict) else "?"
                print(f"{pid:<5} {asin:<14} {'⚠️ NO $':<10} {'N/A':<12} {name[:45]}")
                print(f"      fields returned: {fields}")
                failed.append((pid, asin, name, "no price field"))
        elif r.status_code == 403:
            print(f"{pid:<5} {asin:<14} {'❌ 403':<10} {'N/A':<12} Not subscribed to API")
            sys.exit(1)
        elif r.status_code == 429:
            print(f"{pid:<5} {asin:<14} {'⏳ 429':<10} {'N/A':<12} Quota hit — stop")
            sys.exit(1)
        else:
            print(f"{pid:<5} {asin:<14} {f'❌ {r.status_code}':<10} {'N/A':<12} {name[:45]}")
            failed.append((pid, asin, name, f"HTTP {r.status_code}"))
    except Exception as e:
        print(f"{pid:<5} {asin:<14} {'❌ ERR':<10} {'N/A':<12} {e}")
        failed.append((pid, asin, name, str(e)))
    time.sleep(0.5)

print("-" * 85)
print(f"\n✅ Working: {len(working)}/10   ❌ Failed: {len(failed)}/10")
if failed:
    print("\nFailed — share this list with Claude to get replacement ASINs:")
    for pid, asin, name, reason in failed:
        print(f"  {pid}  {asin}  {name}  → {reason}")
if working:
    print("\nWorking — live prices found:")
    for pid, asin, name, price in working:
        print(f"  {pid}  {asin}  ${price}  {name}")
