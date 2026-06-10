import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data.products import get_seasonal_data, SEASONAL_DEMAND
from datetime import datetime

def show():
    st.title("📊 Seasonal Demand Planner")
    st.caption("Plan pricing strategy around Pool Supply Store's seasonal business cycles")

    current_month = datetime.now().month
    month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    current_month_name = month_names[current_month - 1]

    st.info(f"📅 **Current Month: {current_month_name}** — Use this planner to set pricing strategy for upcoming months.")

    st.markdown("---")

    # Category selector
    categories = list(SEASONAL_DEMAND.keys())
    selected_cats = st.multiselect(
        "Select categories to view:",
        categories,
        default=["Chemicals", "Covers", "Equipment"],
    )

    df = get_seasonal_data()
    filtered = df[df["Category"].isin(selected_cats)] if selected_cats else df

    # Line chart
    st.subheader("📈 Demand Index by Month")
    fig = px.line(
        filtered,
        x="Month",
        y="Demand Index",
        color="Category",
        markers=True,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )

    # Add vertical line for current month using numeric index (0-based for categorical axis)
    month_index = month_names.index(current_month_name)
    fig.add_shape(
        type="line",
        x0=month_index, x1=month_index,
        y0=0, y1=1,
        xref="x", yref="paper",
        line=dict(color="red", width=2, dash="dot"),
    )
    fig.add_annotation(
        x=month_index, y=1.05,
        xref="x", yref="paper",
        text="▼ Today",
        showarrow=False,
        font=dict(color="red", size=11),
    )

    # Add shaded peak zone (May=4, Aug=7 in 0-based index)
    fig.add_shape(type="rect", x0=4, x1=7, y0=0, y1=1,
                  xref="x", yref="paper",
                  fillcolor="rgba(255,200,0,0.10)", line_width=0)
    fig.add_annotation(x=5.5, y=0.97, xref="x", yref="paper",
                       text="Peak Season", showarrow=False,
                       font=dict(color="#92400e", size=10))

    # Closing season (Sep=8, Oct=9)
    fig.add_shape(type="rect", x0=8, x1=10, y0=0, y1=1,
                  xref="x", yref="paper",
                  fillcolor="rgba(100,150,255,0.08)", line_width=0)
    fig.add_annotation(x=9, y=0.97, xref="x", yref="paper",
                       text="Closing Season", showarrow=False,
                       font=dict(color="#1e40af", size=10))

    fig.update_layout(
        height=380,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis_title="Demand Index (1.0 = baseline)",
        legend_title="Category",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Pricing strategy table
    st.subheader("💰 Recommended Pricing Strategy by Month")

    strategy_rows = []
    for month_num, month in enumerate(month_names, 1):
        strategies = []
        for cat in (selected_cats or categories):
            idx = SEASONAL_DEMAND[cat][month_num]
            if idx >= 1.5:
                strategies.append(f"📈 {cat}: Raise 5–10%")
            elif idx >= 0.8:
                strategies.append(f"➡️ {cat}: Hold")
            else:
                strategies.append(f"📉 {cat}: Bundle/Clear")

        strategy_rows.append({
            "Month": month,
            "Is Current": "👈 NOW" if month_num == current_month else "",
            "Pricing Actions": " · ".join(strategies),
        })

    strat_df = pd.DataFrame(strategy_rows)

    def highlight_current(row):
        if row["Is Current"]:
            return ["background-color: #fef9c3; font-weight: bold"] * len(row)
        return [""] * len(row)

    styled_strat = strat_df.style.apply(highlight_current, axis=1)
    st.dataframe(styled_strat, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Heatmap
    st.subheader("🔥 Demand Heatmap")
    heat_data = pd.DataFrame(
        {cat: [SEASONAL_DEMAND[cat][m] for m in range(1, 13)] for cat in categories},
        index=month_names,
    )

    fig2 = go.Figure(data=go.Heatmap(
        z=heat_data.values,
        x=heat_data.columns,
        y=heat_data.index,
        colorscale="RdYlGn",
        text=heat_data.values.round(1),
        texttemplate="%{text}",
        colorbar_title="Demand",
    ))
    fig2.update_layout(
        height=380,
        margin=dict(l=0, r=0, t=20, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.caption("🔑 Demand Index: 2.0 = double baseline sales. Use this to justify price increases during peak and bundle deals in off-season.")
