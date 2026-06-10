import streamlit as st
import pandas as pd
import plotly.express as px
from data.products import get_listing_scores, LISTING_CHECKLIST_PRODUCTS

def show():
    st.title("✅ Amazon Listing Quality Checker")
    st.caption("Audit Pool Supply Store Amazon listings against best practices")

    st.markdown("---")

    df = get_listing_scores()

    # Summary KPIs
    good = len(df[df["Health"] == "🟢 Good"])
    needs_work = len(df[df["Health"] == "🟡 Needs Work"])
    poor = len(df[df["Health"] == "🔴 Poor"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Listings Audited", len(df))
    col2.metric("🟢 Good (6–7/7)", good)
    col3.metric("🟡 Needs Work (4–5/7)", needs_work)
    col4.metric("🔴 Poor (<4/7)", poor)

    st.markdown("---")

    # Full audit table
    st.subheader("📋 Full Listing Audit")

    display_cols = ["Product", "Bullet Points", "5+ Images", "A+ Content",
                    "100+ Reviews", "Rating ≥4.2", "Prime", "Keyword in Title",
                    "Score", "Health"]

    def color_health(val):
        if "Good" in val:
            return "background-color: #d1fae5; color: #065f46"
        elif "Needs" in val:
            return "background-color: #fef9c3; color: #713f12"
        elif "Poor" in val:
            return "background-color: #fee2e2; color: #991b1b"
        return ""

    styled = df[display_cols].style.map(color_health, subset=["Health"])
    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📊 Health Distribution")
        health_counts = df["Health"].value_counts().reset_index()
        health_counts.columns = ["Health", "Count"]
        fig = px.pie(
            health_counts,
            names="Health",
            values="Count",
            color_discrete_map={
                "🟢 Good": "#22c55e",
                "🟡 Needs Work": "#f59e0b",
                "🔴 Poor": "#ef4444",
            },
            hole=0.4,
        )
        fig.update_layout(
            height=280,
            margin=dict(l=0, r=0, t=20, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("📈 Ratings Overview")
        fig2 = px.bar(
            df.sort_values("Rating"),
            x="Reviews",
            y="Product",
            color="Rating",
            color_continuous_scale="RdYlGn",
            orientation="h",
            text="Rating",
        )
        fig2.update_layout(
            height=310,
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
            yaxis=dict(tickfont=dict(size=9)),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # Drill-down
    st.subheader("🔎 Product Deep Dive")
    selected_product = st.selectbox("Select a listing to analyze:", df["Product"].tolist())
    row = df[df["Product"] == selected_product].iloc[0]
    raw = next(p for p in LISTING_CHECKLIST_PRODUCTS if p["Product"] == selected_product)

    col1, col2, col3 = st.columns(3)
    col1.metric("Overall Score", row["Score"])
    col2.metric("Rating", f"⭐ {raw['Rating']}")
    col3.metric("Reviews", f"{'✅' if raw['Reviews'] >= 100 else '❌'} {raw['Reviews']}")

    issues = []
    if not raw["Bullet Points"]:
        issues.append("Missing bullet points — add 5 keyword-rich bullet points")
    if not raw["Images_5plus"]:
        issues.append("Fewer than 5 images — add lifestyle, infographic, and detail shots")
    if not raw["APlus"]:
        issues.append("No A+ Content — create enhanced brand content to boost conversion")
    if raw["Reviews"] < 100:
        issues.append(f"Only {raw['Reviews']} reviews — run a Vine program or request reviews")
    if raw["Rating"] < 4.2:
        issues.append(f"Rating {raw['Rating']} is below 4.2 — investigate negative reviews")
    if not raw["Prime"]:
        issues.append("Not Prime eligible — check FBA enrollment or seller-fulfilled prime")
    if not raw["Keyword_Title"]:
        issues.append("Title missing primary keyword — add 'pool' + product type + size/spec")

    if issues:
        st.subheader("⚠️ Issues to Fix")
        for i, issue in enumerate(issues, 1):
            st.warning(f"**{i}.** {issue}")
    else:
        st.success("🎉 This listing meets all quality benchmarks! Monitor reviews regularly.")

    st.caption("💡 Fixing listing quality directly impacts Amazon search rank, conversion rate, and Buy Box win rate.")
