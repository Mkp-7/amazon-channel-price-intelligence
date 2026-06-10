# 🏊 PoolPrice AI Agent

> An AI-powered Amazon channel intelligence dashboard for pool supply retailers.
> Built as a portfolio project for the **Ecommerce Amazon Channel Specialist** role.

**Stack: Python · Streamlit · Groq (LLM) · RapidAPI · Plotly**

---

## 🎯 What This Does

This tool mirrors the actual daily work of an Amazon Channel Specialist:

| Feature | What it does |
|---|---|
| **Dashboard** | KPI overview of all 10 SKUs with live pricing action signals |
| **Price Scanner** | Compare store prices vs live Amazon Buy Box prices (via RapidAPI) |
| **Seasonal Demand Planner** | Heatmap + month-by-month pricing strategy calendar |
| **Listing Quality Checker** | Audit Amazon listings against 7 best-practice criteria |
| **AI Pricing Advisor** | Chat with an AI agent (Groq / Llama 3.1) for pricing recommendations |

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/amazon-channel-price-intelligence.git
cd poolprice-agent
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run locally
```bash
streamlit run app.py
```

### 4. Get your API keys

**RapidAPI**
1. Go to [rapidapi.com/letscrape-6bRBa3QguO5/api/real-time-amazon-data](https://rapidapi.com/letscrape-6bRBa3QguO5/api/real-time-amazon-data)
2. Copy your key from the code panel on the right
3. Paste it in the app sidebar under **🔑 API Keys**

**Groq**
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up with email → click **API Keys → Create API Key**
3. Paste it in the app sidebar under **🔑 API Keys**

---

## ☁️ Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select your repo → set `app.py` as the main file
4. Click **Deploy** - live in ~2 minutes

---

## 🧠 AI Agent Details

- **Model:** Llama 3.1 8B Instant via Groq
- **No API keys stored** - entered by the user in the sidebar each session

The AI agent is a pool supply pricing analyst. It understands:
- Amazon Buy Box dynamics and eligibility
- Seasonal pool supply demand (peak: May–Aug, closing: Sep–Oct)
- Competitive pricing strategy
- Pool supply product categories and price sensitivity

---

## 📊 Live Pricing Data

- **Store prices:** 10 real Rx Clear products with prices verified from the retailer's website
- **Amazon prices:** Live Buy Box prices fetched via RapidAPI (cached 6 hours to protect monthly quota)
- **Seasonal demand:** Based on real pool industry seasonality patterns

### API quota management
The app caches Amazon prices for 6 hours in `data/price_cache.json`.
With 10 products and a 6-hour cache, 50 requests covers roughly 3 days of refreshes.
Delete `data/price_cache.json` to force a fresh fetch.

---

## 📁 Project Structure

```
poolprice-agent/
├── app.py                   # Main Streamlit app + global sidebar
├── requirements.txt
├── test_api.py              # Standalone API key diagnostic (run in terminal)
├── .streamlit/
│   └── config.toml          # Theme + server config
├── data/
│   └── products.py          # Product catalog, live fetch, cache, seasonal data
├── agents/
│   └── groq_agent.py        # Groq LLM agent (pricing advisor)
└── pages/
    ├── dashboard.py          # KPI overview + full pricing action board
    ├── price_scanner.py      # Live Amazon vs store price comparison
    ├── seasonal_planner.py   # Demand heatmap + strategy calendar
    ├── listing_checker.py    # Amazon listing quality audit
    └── ai_advisor.py         # AI chat + per-product analysis
```

---

## 💡 Why I Built This

Instead of just submitting a resume, I built the tool I would actually use on day one at the job.

This project demonstrates:
- ✅ Understanding of Amazon marketplace operations and Buy Box mechanics
- ✅ Data-driven pricing analysis with live competitor data
- ✅ Knowledge of real pool supply product catalog and seasonal business cycles
- ✅ Ability to build with real APIs (RapidAPI, Groq)
- ✅ Initiative and ownership - built before being asked

---

## 🔧 Production Roadmap

- [ ] Add Walmart price comparison
- [ ] Automated daily price alert emails
- [ ] Buy Box win/loss tracking over time
- [ ] Inventory-aware pricing (lower when overstock)
- [ ] A/B price testing tracker
- [ ] Live data via Amazon SP-API (replace RapidAPI)
