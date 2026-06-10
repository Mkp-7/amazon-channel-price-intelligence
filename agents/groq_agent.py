import os
import json
import requests
from typing import Optional

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.1-8b-instant"  # Free, fast (llama3-8b-8192 was deprecated Aug 2025)

SYSTEM_PROMPT = """You are an expert Amazon ecommerce pricing analyst for Pool Supply Store, 
a pool supply retailer based in . You help the team make smart, 
data-driven pricing decisions for their Amazon channel.

Your expertise includes:
- Amazon marketplace dynamics and Buy Box optimization
- Seasonal pricing for pool supplies (peak: May-August, closing: Sept-Oct)
- Competitive pricing strategy against In The Swim, Leslie's Pool, Walmart, HTH Pools
- Pool supply product knowledge (chemicals, covers, equipment, liners, accessories)

Always provide:
1. A clear recommendation (Raise / Lower / Hold price)
2. Specific reasoning based on the data
3. A concrete suggested price or price range
4. One risk to watch out for

Keep responses concise, practical, and actionable. Use plain language."""


def call_groq(messages: list, api_key: str) -> Optional[str]:
    """Call Groq API with a list of messages."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 600,
        "temperature": 0.4,
    }
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as e:
        try:
            err_body = response.json()
            err_msg = err_body.get("error", {}).get("message", str(e))
        except Exception:
            err_msg = str(e)
        if response.status_code == 401:
            return "❌ Invalid API key. Please check your Groq API key at console.groq.com."
        elif response.status_code == 429:
            return "⏳ Rate limit hit. Wait 60 seconds and try again (free tier: 30 req/min)."
        elif response.status_code == 404:
            return f"❌ Model not found. The model '{MODEL}' may not be available. Error: {err_msg}"
        else:
            return f"❌ API error {response.status_code}: {err_msg}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


def get_pricing_advice(
    product_name: str,
    our_price: float,
    competitor_data: dict,
    season_demand: float,
    api_key: str,
) -> str:
    """Get AI pricing advice for a specific product."""
    comp_summary = "\n".join(
        [f"  - {k}: ${v}" for k, v in competitor_data.items()]
    )
    lowest = min(competitor_data.values())
    highest = max(competitor_data.values())

    user_msg = f"""Analyze this Amazon pricing situation for Pool Supply Store:

Product: {product_name}
Our Current Price: ${our_price}
Competitor Prices:
{comp_summary}
Lowest Competitor: ${lowest}
Highest Competitor: ${highest}
Current Seasonal Demand Index: {season_demand} (1.0 = average, 2.0 = peak summer)

Should we adjust our price? Give a specific recommendation."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]
    return call_groq(messages, api_key)


def chat_with_agent(conversation_history: list, user_message: str, api_key: str) -> str:
    """Multi-turn chat with the pricing agent."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_message})
    return call_groq(messages, api_key)


def analyze_listing(product_name: str, score: int, issues: list, api_key: str) -> str:
    """Get AI advice on improving an Amazon listing."""
    issues_str = ", ".join(issues) if issues else "none identified"
    user_msg = f"""Amazon listing audit for Pool Supply Store:

Product: {product_name}
Overall Listing Score: {score}/7
Issues Found: {issues_str}

What are the top 2-3 actions to improve this listing's performance on Amazon? 
Focus on what will most impact sales rank and Buy Box eligibility."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]
    return call_groq(messages, api_key)
