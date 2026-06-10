import pandas as pd
import random
import json
import os
import re
import time
from datetime import datetime

# ─────────────────────────────────────────────────────────────────
# 10 real Rx Clear products:
#  - our_price  = verified from poolsupplies.com (Google snippets)
#  - asin       = verified live on amazon.com/dp
# ─────────────────────────────────────────────────────────────────
PRODUCTS = [
    {
        "id": "P001",
        "name": "Rx Clear 3\" Chlorine Tablets 50 lbs",
        "category": "Chemicals",
        "our_price": 239.99,
        "asin": "B00IGETSNC",
        "amazon_url": "https://www.amazon.com/dp/B00IGETSNC",
    },
    {
        "id": "P002",
        "name": "Rx Clear Granular Pool Chlorine 50 lbs",
        "category": "Chemicals",
        "our_price": 129.99,
        "asin": "B00OM8E7NC",
        "amazon_url": "https://www.amazon.com/dp/B00OM8E7NC",
    },
    {
        "id": "P003",
        "name": "Rx Clear 1\" Chlorine Tablets 25 lbs",
        "category": "Chemicals",
        "our_price": 149.99,
        "asin": "B00OJG2838",
        "amazon_url": "https://www.amazon.com/dp/B00OJG2838",
    },
    {
        "id": "P004",
        "name": "Rx Clear 3\" No-Grab Chlorine Tablets 22 lbs",
        "category": "Chemicals",
        "our_price": 109.99,
        "asin": "B07JNKLY5P",
        "amazon_url": "https://www.amazon.com/dp/B07JNKLY5P",
    },
    {
        "id": "P005",
        "name": "Rx Clear Spring Opening Kit (up to 7,500 gal)",
        "category": "Chemicals",
        "our_price": 24.99,
        "asin": "B00Y2ZX6XW",
        "amazon_url": "https://www.amazon.com/dp/B00Y2ZX6XW",
    },
    {
        "id": "P006",
        "name": "Rx Clear Spring Opening Kit (up to 15,000 gal)",
        "category": "Chemicals",
        "our_price": 34.99,
        "asin": "B00Y2ZX71S",
        "amazon_url": "https://www.amazon.com/dp/B00Y2ZX71S",
    },
    {
        "id": "P007",
        "name": "Rx Clear Spring Opening Kit (up to 30,000 gal)",
        "category": "Chemicals",
        "our_price": 49.99,
        "asin": "B00Y2ZX72C",
        "amazon_url": "https://www.amazon.com/dp/B00Y2ZX72C",
    },
    {
        "id": "P008",
        "name": "Rx Clear Deluxe Opening Kit (up to 7,500 gal)",
        "category": "Chemicals",
        "our_price": 79.99,
        "asin": "B00SLGWOSG",
        "amazon_url": "https://www.amazon.com/dp/B00SLGWOSG",
    },
    {
        "id": "P009",
        "name": "Rx Clear Deluxe Opening Kit (up to 15,000 gal)",
        "category": "Chemicals",
        "our_price": 99.99,
        "asin": "B00SLGWOUY",
        "amazon_url": "https://www.amazon.com/dp/B00SLGWOUY",
    },
    {
        "id": "P010",
        "name": "Rx Clear Deluxe Opening Kit (up to 30,000 gal)",
        "category": "Chemicals",
        "our_price": 149.99,
        "asin": "B00SLGWOWC",
        "amazon_url": "https://www.amazon.com/dp/B00SLGWOWC",
    },
]

CACHE_FILE = "data/price_cache.json"

SEASONAL_DEMAND = {
    "Chemicals": {1:0.2,2:0.3,3:0.7,4:1.0,5:1.5,6:2.0,7:1.8,8:1.4,9:1.0,10:0.8,11:0.3,12:0.2},
    "Covers":    {1:0.3,2:0.3,3:0.5,4:0.8,5:1.0,6:1.5,7:1.2,8:1.0,9:1.8,10:2.0,11:0.8,12:0.4},
    "Equipment": {1:0.2,2:0.3,3:0.8,4:1.2,5:1.5,6:1.8,7:1.5,8:1.2,9:0.8,10:0.5,11:0.3,12:0.2},
    "Cleaning":  {1:0.2,2:0.2,3:0.6,4:1.0,5:1.4,6:1.8,7:1.8,8:1.4,9:0.8,10:0.5,11:0.2,12:0.2},
}

# ── Cache ─────────────────────────────────────────────────────────
def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE) as f: return json.load(f)
        except: return {}
    return {}

def save_cache(cache):
    os.makedirs("data", exist_ok=True)
    with open(CACHE_FILE, "w") as f: json.dump(cache, f, indent=2)

def cache_is_fresh(entry, max_age_hours=6):
    if not entry or "fetched_at" not in entry: return False
    age = (datetime.now() - datetime.fromisoformat(entry["fetched_at"])).total_seconds()
    return age < max_age_hours * 3600

# ── Live fetch ────────────────────────────────────────────────────
def fetch_live_amazon_price(asin: str, rapidapi_key: str) -> tuple[dict, str | None]:
    import requests as req
    url = "https://real-time-amazon-data.p.rapidapi.com/product-details"
    headers = {
        "X-RapidAPI-Key":  rapidapi_key.strip(),
        "X-RapidAPI-Host": "real-time-amazon-data.p.rapidapi.com",
    }
    try:
        r = req.get(url, headers=headers, params={"asin": asin, "country": "US"}, timeout=20)
        if r.status_code == 401: return {}, "❌ 401 Invalid API key"
        if r.status_code == 403: return {}, "❌ 403 Not subscribed to this API"
        if r.status_code == 429: return {}, "⏳ 429 Free quota (50 req/month) exhausted"
        if r.status_code != 200: return {}, f"❌ HTTP {r.status_code}: {r.text[:200]}"

        body = r.json()
        d = body.get("data") or body.get("product") or body
        price_str = (d.get("product_price") or d.get("price") or
                     d.get("buybox_price") or d.get("current_price") or
                     d.get("product_original_price") or "")
        price = None
        if price_str:
            m = re.search(r"\d+\.?\d*", str(price_str).replace(",","").replace("$",""))
            if m: price = float(m.group())

        if price is None:
            fields = list(d.keys()) if isinstance(d, dict) else str(d)[:200]
            return {"asin": asin, "amazon_price": None,
                    "raw_fields": fields, "fetched_at": datetime.now().isoformat()}, \
                   f"⚠️ Price field missing. Fields returned: {fields}"

        return {
            "asin": asin, "amazon_price": price,
            "title": d.get("product_title") or d.get("title", ""),
            "rating": d.get("product_star_rating") or d.get("rating"),
            "reviews": d.get("product_num_ratings") or d.get("reviews_count"),
            "fetched_at": datetime.now().isoformat(),
        }, None

    except req.exceptions.Timeout:
        return {}, "⏱️ Timed out (20s)"
    except Exception as e:
        return {}, f"❌ {type(e).__name__}: {e}"


def test_api_key(rapidapi_key: str) -> dict:
    import requests as req
    url = "https://real-time-amazon-data.p.rapidapi.com/product-details"
    headers = {"X-RapidAPI-Key": rapidapi_key.strip(),
               "X-RapidAPI-Host": "real-time-amazon-data.p.rapidapi.com"}
    try:
        r = req.get(url, headers=headers, params={"asin": "B00IGETSNC", "country": "US"}, timeout=20)
        body = r.json() if "application/json" in r.headers.get("content-type","") else {}
        d = body.get("data") or body.get("product") or body
        price_str = (d.get("product_price") or d.get("price") or
                     d.get("buybox_price") or d.get("current_price") or "")
        return {
            "ok": r.status_code == 200,
            "status_code": r.status_code,
            "price_raw": price_str,
            "top_keys": list(body.keys()) if isinstance(body, dict) else [],
            "data_keys": list(d.keys()) if isinstance(d, dict) else [],
            "error": None if r.status_code == 200 else r.text[:300],
        }
    except Exception as e:
        return {"ok": False, "status_code": None, "error": str(e), "top_keys": [], "data_keys": []}


def get_live_prices(rapidapi_key: str, force_refresh=False) -> dict:
    cache, results, errors = load_cache(), {}, {}
    for p in PRODUCTS:
        asin = p["asin"]
        if not force_refresh and cache_is_fresh(cache.get(asin)):
            results[asin] = cache[asin]
        else:
            data, err = fetch_live_amazon_price(asin, rapidapi_key)
            if err:
                errors[asin] = err
                if asin in cache: results[asin] = cache[asin]
            else:
                cache[asin] = data
                results[asin] = data
            time.sleep(0.3)
    if any(results.values()): save_cache(cache)
    results["__errors__"] = errors
    return results


def action_label(gap_pct):
    if gap_pct > 8:  return "🔴 Lower Price"
    if gap_pct < -5: return "🟢 Raise Price"
    return "🟡 Hold"


def get_all_products_with_analysis(live_data=None):
    rows = []
    for p in PRODUCTS:
        our  = p["our_price"]
        live = (live_data or {}).get(p["asin"], {})
        amz  = live.get("amazon_price") if live else None
        if amz:
            gap_pct = round((our - amz) / amz * 100, 1)
            amz_label, src = f"${amz:,.2f} ✅", "🟢 Live"
        else:
            random.seed(hash(p["id"]) + 42)
            amz = round(our * random.uniform(0.85, 1.15), 2)
            gap_pct = round((our - amz) / amz * 100, 1)
            amz_label, src = f"${amz:,.2f} ⚠️", "⚠️ Est."
        rows.append({
            "SKU": p["id"], "Product": p["name"], "Category": p["category"],
            "Our Price": f"${our:,.2f}", "Amazon Price": amz_label,
            "Gap (%)": gap_pct, "Action": action_label(gap_pct), "Source": src,
        })
    return pd.DataFrame(rows)


def get_seasonal_data():
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    rows = []
    for cat, monthly in SEASONAL_DEMAND.items():
        for i, m in enumerate(months, 1):
            idx = monthly[i]
            rows.append({
                "Month": m, "Month_Num": i, "Category": cat, "Demand Index": idx,
                "Recommended Strategy": (
                    "Raise prices 5-10%" if idx >= 1.5 else
                    "Hold pricing" if idx >= 0.8 else "Clearance / bundle deals"
                ),
            })
    return pd.DataFrame(rows)


LISTING_CHECKLIST_PRODUCTS = [
    {"Product":'Rx Clear 3" Chlorine Tablets 50 lbs', "Bullet Points":True, "Images_5plus":True,  "APlus":True,  "Reviews":847,  "Rating":4.6,"Prime":True, "Keyword_Title":True},
    {"Product":"Rx Clear Granular Chlorine 50 lbs",    "Bullet Points":True, "Images_5plus":True,  "APlus":False, "Reviews":312,  "Rating":4.3,"Prime":True, "Keyword_Title":True},
    {"Product":'Rx Clear 1" Chlorine Tablets 25 lbs',  "Bullet Points":True, "Images_5plus":False, "APlus":False, "Reviews":198,  "Rating":4.1,"Prime":True, "Keyword_Title":False},
    {"Product":"Rx Clear No-Grab Tablets 22 lbs",      "Bullet Points":False,"Images_5plus":True,  "APlus":False, "Reviews":74,   "Rating":3.9,"Prime":True, "Keyword_Title":True},
    {"Product":"Spring Opening Kit 7,500 gal",         "Bullet Points":True, "Images_5plus":True,  "APlus":True,  "Reviews":521,  "Rating":4.4,"Prime":True, "Keyword_Title":True},
    {"Product":"Spring Opening Kit 15,000 gal",        "Bullet Points":True, "Images_5plus":False, "APlus":False, "Reviews":289,  "Rating":4.2,"Prime":True, "Keyword_Title":True},
    {"Product":"Spring Opening Kit 30,000 gal",        "Bullet Points":True, "Images_5plus":True,  "APlus":False, "Reviews":156,  "Rating":4.0,"Prime":True, "Keyword_Title":False},
    {"Product":"Deluxe Opening Kit 7,500 gal",         "Bullet Points":False,"Images_5plus":False, "APlus":False, "Reviews":43,   "Rating":3.7,"Prime":True, "Keyword_Title":False},
    {"Product":"Deluxe Opening Kit 15,000 gal",        "Bullet Points":True, "Images_5plus":True,  "APlus":True,  "Reviews":677,  "Rating":4.5,"Prime":True, "Keyword_Title":True},
    {"Product":"Deluxe Opening Kit 30,000 gal",        "Bullet Points":True, "Images_5plus":True,  "APlus":False, "Reviews":1204, "Rating":4.7,"Prime":True, "Keyword_Title":True},
]

def get_listing_scores():
    rows = []
    for p in LISTING_CHECKLIST_PRODUCTS:
        checks = [p["Bullet Points"],p["Images_5plus"],p["APlus"],
                  p["Reviews"]>=100,p["Rating"]>=4.2,p["Prime"],p["Keyword_Title"]]
        score = sum(checks)
        rows.append({
            "Product":p["Product"],
            "Bullet Points":"✅" if p["Bullet Points"] else "❌",
            "5+ Images":"✅" if p["Images_5plus"] else "❌",
            "A+ Content":"✅" if p["APlus"] else "❌",
            "100+ Reviews":"✅" if p["Reviews"]>=100 else "❌",
            "Rating ≥4.2":"✅" if p["Rating"]>=4.2 else "❌",
            "Prime":"✅" if p["Prime"] else "❌",
            "Keyword in Title":"✅" if p["Keyword_Title"] else "❌",
            "Score":f"{score}/7",
            "Health":"🟢 Good" if score>=6 else ("🟡 Needs Work" if score>=4 else "🔴 Poor"),
            "Reviews":p["Reviews"],"Rating":p["Rating"],
        })
    return pd.DataFrame(rows)
