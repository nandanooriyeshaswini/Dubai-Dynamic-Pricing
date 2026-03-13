"""
Dubai Dynamic Restaurant Pricing — EDA Dashboard
==================================================
Streamlit app: 10 insight categories, drill-downs, Sankey to App Adoption.
Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from itertools import combinations
import os

# =============================================================================
# CONFIG
# =============================================================================

st.set_page_config(
    page_title="DinePrice Dubai — EDA Dashboard",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .block-container {padding-top: 1rem; padding-bottom: 1rem;}
    h1 {font-size: 1.8rem !important;}
    h2 {font-size: 1.4rem !important; border-bottom: 2px solid #FF6B35; padding-bottom: 0.3rem;}
    h3 {font-size: 1.1rem !important;}
    div[data-testid="stMetric"] {background: #f8f9fa; padding: 10px; border-radius: 8px; border-left: 4px solid #FF6B35;}
</style>
""", unsafe_allow_html=True)

PALETTE = ["#FF6B35", "#004E89", "#1A936F", "#F4A261", "#E76F51",
           "#264653", "#2A9D8F", "#E9C46A", "#606C38", "#BC6C25"]

# =============================================================================
# DATA
# =============================================================================

@st.cache_data
def load_data():
    # Try multiple paths for flexibility
    for path in ["data/data_clean.csv", "data_clean.csv",
                  "dubai-pricing-dashboard/data/data_clean.csv"]:
        if os.path.exists(path):
            return pd.read_csv(path)
    st.error("data_clean.csv not found. Place it in data/ folder.")
    st.stop()

df = load_data()

# Helper: explode multi-select columns
def explode_col(df, col):
    return df[col].dropna().str.split(", ").explode().str.strip()

# =============================================================================
# SIDEBAR
# =============================================================================

st.sidebar.image("https://img.icons8.com/fluency/96/restaurant.png", width=60)
st.sidebar.title("🍽️ DinePrice Dubai")
st.sidebar.markdown("*Dynamic Pricing EDA Dashboard*")
st.sidebar.divider()

sections = [
    "📊 Overview & KPIs",
    "1️⃣ Customer Profile & Segmentation",
    "2️⃣ Dining Behaviour Patterns",
    "3️⃣ Price Sensitivity & Appetite",
    "4️⃣ Dynamic Pricing System",
    "5️⃣ Location & Cuisine Intelligence",
    "6️⃣ Delivery vs Dine-in",
    "7️⃣ Correlation Analysis",
    "8️⃣ Challenges & Features (ARM Preview)",
    "9️⃣ App Adoption Deep Dive",
    "🔟 Seasonality",
    "🔀 Sankey: Path to Adoption",
]

section = st.sidebar.radio("Navigate", sections, index=0)

st.sidebar.divider()
st.sidebar.caption(f"Dataset: {len(df):,} clean records | 35 variables")
st.sidebar.caption("North Star: App Adoption (Yes/No)")

# =============================================================================
# 0. OVERVIEW & KPIs
# =============================================================================

if section == "📊 Overview & KPIs":
    st.title("🍽️ DinePrice Dubai — Dynamic Restaurant Pricing")
    st.markdown("**North Star Metric:** App Adoption Rate — *What drives customers to say Yes?*")

    adopt_rate = (df["App_Adoption"] == "Yes").mean() * 100
    avg_spend = df["Avg_Spend_AED"].mean()
    avg_surge = df["Surge_Multiplier"].mean()
    delivery_pct = (df["Order_Channel"] == "Delivery App").mean() * 100

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Responses", f"{len(df):,}")
    c2.metric("Adoption Rate", f"{adopt_rate:.1f}%")
    c3.metric("Avg Spend", f"{avg_spend:.0f} AED")
    c4.metric("Avg Surge", f"{avg_surge:.2f}x")
    c5.metric("Delivery Share", f"{delivery_pct:.1f}%")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        fig = px.pie(df, names="App_Adoption", title="App Adoption Split",
                     color_discrete_sequence=[PALETTE[0], PALETTE[1]],
                     hole=0.45)
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.histogram(df, x="Avg_Spend_AED", nbins=40,
                           color="App_Adoption", barmode="overlay",
                           title="Spend Distribution by Adoption",
                           color_discrete_sequence=[PALETTE[0], PALETTE[1]])
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    # Quick dataset preview
    with st.expander("📋 Dataset Preview"):
        st.dataframe(df.head(20), use_container_width=True)

# =============================================================================
# 1. CUSTOMER PROFILE & SEGMENTATION
# =============================================================================

elif section == "1️⃣ Customer Profile & Segmentation":
    st.title("1️⃣ Customer Profile & Segmentation")

    col1, col2 = st.columns(2)

    with col1:
        age_order = ["18-24", "25-34", "35-44", "45-54", "55+"]
        fig = px.histogram(df, x="Age", color="App_Adoption",
                           category_orders={"Age": age_order},
                           title="Age Distribution by Adoption",
                           color_discrete_sequence=PALETTE, barmode="group")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        inc_order = ["<5000", "5000-10000", "10001-20000", "20001-35000", ">35000"]
        fig = px.histogram(df, x="Monthly_Income", color="App_Adoption",
                           category_orders={"Monthly_Income": inc_order},
                           title="Income Distribution by Adoption",
                           color_discrete_sequence=PALETTE, barmode="group")
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        fig = px.histogram(df, x="Customer_Type", color="Nationality_Cluster",
                           title="Customer Type by Nationality",
                           color_discrete_sequence=PALETTE, barmode="stack")
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        fig = px.histogram(df, x="Loyalty_Status", color="Customer_Type",
                           title="Loyalty Status by Customer Type",
                           color_discrete_sequence=PALETTE, barmode="stack")
        st.plotly_chart(fig, use_container_width=True)

    # Drill-down: Age × Income heatmap
    st.subheader("🔍 Drill-down: Age × Income Heatmap")
    ct = pd.crosstab(df["Age"], df["Monthly_Income"])
    ct = ct.reindex(index=age_order, columns=inc_order)
    fig = px.imshow(ct, text_auto=True, color_continuous_scale="Oranges",
                    title="Respondent Count: Age vs Income",
                    labels=dict(x="Monthly Income", y="Age Group", color="Count"))
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Drill-down: Nationality breakdown
    st.subheader("🔍 Drill-down: Nationality Cluster")
    fig = px.sunburst(df, path=["Nationality_Cluster", "Customer_Type", "App_Adoption"],
                      title="Nationality → Customer Type → Adoption",
                      color_discrete_sequence=PALETTE)
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# 2. DINING BEHAVIOUR PATTERNS
# =============================================================================

elif section == "2️⃣ Dining Behaviour Patterns":
    st.title("2️⃣ Dining Behaviour Patterns")

    col1, col2 = st.columns(2)

    with col1:
        time_order = ["Breakfast", "Lunch", "Dinner", "Late Night"]
        ct = pd.crosstab(df["Age"], df["Order_Time"])
        ct = ct.reindex(index=["18-24", "25-34", "35-44", "45-54", "55+"],
                        columns=time_order)
        fig = px.imshow(ct, text_auto=True, color_continuous_scale="YlOrRd",
                        title="Order Time by Age Group")
        fig.update_layout(height=380)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.histogram(df, x="Order_Channel", color="Age",
                           category_orders={"Age": ["18-24", "25-34", "35-44", "45-54", "55+"]},
                           title="Channel Preference by Age",
                           color_discrete_sequence=PALETTE, barmode="stack")
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        freq_order = ["Multiple/week", "Once/week", "2-3/month", "Once/month", "Rarely"]
        inc_order = ["<5000", "5000-10000", "10001-20000", "20001-35000", ">35000"]
        ct2 = pd.crosstab(df["Monthly_Income"], df["Dining_Frequency"])
        ct2 = ct2.reindex(index=inc_order, columns=freq_order)
        fig = px.imshow(ct2, text_auto=True, color_continuous_scale="Tealgrn",
                        title="Dining Frequency by Income")
        fig.update_layout(height=380)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        fig = px.histogram(df, x="Group_Size", color="Customer_Type",
                           title="Group Size by Customer Type",
                           color_discrete_sequence=PALETTE, barmode="group")
        st.plotly_chart(fig, use_container_width=True)

    # Drill-down: Day preference
    st.subheader("🔍 Drill-down: Day × Time × Channel")
    fig = px.sunburst(df, path=["Day_Preference", "Order_Time", "Order_Channel"],
                      title="Day → Time → Channel Flow",
                      color_discrete_sequence=PALETTE)
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

    # Drill-down: Frequency vs Spend
    st.subheader("🔍 Drill-down: Dining Frequency vs Average Spend")
    fig = px.box(df, x="Dining_Frequency", y="Avg_Spend_AED", color="Dining_Frequency",
                 category_orders={"Dining_Frequency": freq_order},
                 title="Spend Distribution by Dining Frequency",
                 color_discrete_sequence=PALETTE)
    fig.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# 3. PRICE SENSITIVITY & DYNAMIC PRICING APPETITE
# =============================================================================

elif section == "3️⃣ Price Sensitivity & Appetite":
    st.title("3️⃣ Price Sensitivity & Dynamic Pricing Appetite")

    col1, col2 = st.columns(2)

    with col1:
        sens_order = ["Very sensitive", "Moderately sensitive", "Slightly sensitive", "Not sensitive"]
        inc_order = ["<5000", "5000-10000", "10001-20000", "20001-35000", ">35000"]
        ct = pd.crosstab(df["Monthly_Income"], df["Price_Sensitivity"])
        ct = ct.reindex(index=inc_order, columns=sens_order)
        fig = px.imshow(ct, text_auto=True, color_continuous_scale="RdYlGn_r",
                        title="Price Sensitivity by Income")
        fig.update_layout(height=380)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        disc_order = ["5%", "10%", "15%", "20%", ">20%"]
        ct2 = pd.crosstab(df["Price_Sensitivity"], df["Discount_Motivation"])
        ct2 = ct2.reindex(index=sens_order, columns=disc_order)
        fig = px.imshow(ct2, text_auto=True, color_continuous_scale="Oranges",
                        title="Discount Motivation by Sensitivity")
        fig.update_layout(height=380)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        fig = px.histogram(df, x="Offpeak_Willingness", color="Price_Sensitivity",
                           title="Off-Peak Willingness by Sensitivity",
                           color_discrete_sequence=PALETTE, barmode="stack",
                           category_orders={"Offpeak_Willingness": [
                               "Definitely yes", "Probably yes", "Maybe",
                               "Probably not", "Definitely not"]})
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        fair_order = ["Very fair", "Somewhat fair", "Neutral", "Unfair", "Very unfair"]
        fig = px.histogram(df, x="Fairness_Perception", color="Age",
                           title="Fairness Perception by Age",
                           color_discrete_sequence=PALETTE, barmode="stack",
                           category_orders={
                               "Fairness_Perception": fair_order,
                               "Age": ["18-24", "25-34", "35-44", "45-54", "55+"]
                           })
        st.plotly_chart(fig, use_container_width=True)

    # Drill-down: Sensitivity → Adoption
    st.subheader("🔍 Drill-down: Price Sensitivity → Adoption Rate")
    adopt_by_sens = df.groupby("Price_Sensitivity")["App_Adoption"].apply(
        lambda x: (x == "Yes").mean() * 100).reindex(sens_order).reset_index()
    adopt_by_sens.columns = ["Price_Sensitivity", "Adoption_Rate"]
    fig = px.bar(adopt_by_sens, x="Price_Sensitivity", y="Adoption_Rate",
                 title="Adoption Rate by Price Sensitivity",
                 color="Adoption_Rate", color_continuous_scale="RdYlGn",
                 text="Adoption_Rate")
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Drill-down: Discount Importance × Fairness
    st.subheader("🔍 Drill-down: Discount Importance vs Fairness Perception")
    ct3 = pd.crosstab(df["Discount_Importance"], df["Fairness_Perception"])
    di_order = ["Extremely important", "Very important", "Moderately important",
                "Slightly important", "Not important"]
    ct3 = ct3.reindex(index=di_order, columns=fair_order)
    fig = px.imshow(ct3, text_auto=True, color_continuous_scale="Purples",
                    title="Discount Importance vs Fairness Perception")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# 4. DYNAMIC PRICING SYSTEM VARIABLES
# =============================================================================

elif section == "4️⃣ Dynamic Pricing System":
    st.title("4️⃣ Dynamic Pricing System Variables")

    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Surge", f"{df['Surge_Multiplier'].mean():.2f}x")
    col2.metric("Avg Discount %", f"{df['Discount_Percentage'].mean():.1f}%")
    occ_mean = df["Table_Occupancy_Pct"].dropna().mean()
    col3.metric("Avg Occupancy", f"{occ_mean:.1f}%")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.histogram(df, x="Demand_Level", color="Demand_Level",
                           title="Demand Level Distribution",
                           color_discrete_sequence=PALETTE)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.histogram(df, x="Surge_Multiplier", nbins=30, color="Demand_Level",
                           title="Surge Multiplier Distribution by Demand",
                           color_discrete_sequence=PALETTE)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        fig = px.box(df, x="Demand_Level", y="Table_Occupancy_Pct",
                     color="Demand_Level", title="Table Occupancy by Demand Level",
                     color_discrete_sequence=PALETTE,
                     category_orders={"Demand_Level": ["Low", "Medium", "High"]})
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        fig = px.scatter(df, x="Base_Order_Value", y="Final_Order_Value",
                         color="Demand_Level", opacity=0.5,
                         title="Base vs Final Order Value (Surge Impact)",
                         color_discrete_sequence=PALETTE)
        # Add y=x reference line
        fig.add_shape(type="line", x0=0, y0=0, x1=800, y1=800,
                      line=dict(dash="dash", color="gray"))
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    # Drill-down: Surge vs Adoption
    st.subheader("🔍 Drill-down: Surge Multiplier vs App Adoption")
    df["Surge_Bin"] = pd.cut(df["Surge_Multiplier"],
                              bins=[0.7, 0.85, 0.95, 1.05, 1.15, 1.25, 1.45],
                              labels=["0.75-0.85", "0.85-0.95", "0.95-1.05",
                                      "1.05-1.15", "1.15-1.25", "1.25-1.40"])
    surge_adopt = df.groupby("Surge_Bin")["App_Adoption"].apply(
        lambda x: (x == "Yes").mean() * 100).reset_index()
    surge_adopt.columns = ["Surge_Bin", "Adoption_Rate"]
    fig = px.bar(surge_adopt, x="Surge_Bin", y="Adoption_Rate",
                 title="Adoption Rate by Surge Level",
                 color="Adoption_Rate", color_continuous_scale="RdYlGn",
                 text="Adoption_Rate")
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Drill-down: Demand × Day × Time
    st.subheader("🔍 Drill-down: Demand Level by Day & Time")
    ct = pd.crosstab([df["Day_Preference"], df["Order_Time"]], df["Demand_Level"])
    ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100
    fig = px.imshow(ct_pct.round(1), text_auto=True, color_continuous_scale="YlOrRd",
                    title="Demand Level % by Day × Time Combination",
                    labels=dict(color="%"))
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)
    df.drop(columns=["Surge_Bin"], inplace=True, errors="ignore")

# =============================================================================
# 5. LOCATION & CUISINE INTELLIGENCE
# =============================================================================

elif section == "5️⃣ Location & Cuisine Intelligence":
    st.title("5️⃣ Location & Cuisine Intelligence")

    col1, col2 = st.columns(2)

    with col1:
        loc_inc = pd.crosstab(df["Restaurant_Location"], df["Monthly_Income"])
        inc_order = ["<5000", "5000-10000", "10001-20000", "20001-35000", ">35000"]
        loc_inc = loc_inc.reindex(columns=inc_order)
        fig = px.imshow(loc_inc, text_auto=True, color_continuous_scale="Blues",
                        title="Restaurant Location by Income")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        cuis_nat = pd.crosstab(df["Nationality_Cluster"], df["Cuisine_Preference"])
        fig = px.imshow(cuis_nat, text_auto=True, color_continuous_scale="Oranges",
                        title="Cuisine Preference by Nationality")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        tier_inc = pd.crosstab(df["Monthly_Income"], df["Restaurant_Tier"])
        tier_inc = tier_inc.reindex(index=inc_order)
        fig = px.imshow(tier_inc, text_auto=True, color_continuous_scale="Tealgrn",
                        title="Restaurant Tier by Income")
        fig.update_layout(height=380)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        spend_loc = df.groupby("Restaurant_Location")["Avg_Spend_AED"].mean().sort_values(ascending=True).reset_index()
        fig = px.bar(spend_loc, x="Avg_Spend_AED", y="Restaurant_Location",
                     orientation="h", title="Average Spend by Location",
                     color="Avg_Spend_AED", color_continuous_scale="Oranges",
                     text="Avg_Spend_AED")
        fig.update_traces(texttemplate='%{text:.0f} AED', textposition='outside')
        fig.update_layout(height=380)
        st.plotly_chart(fig, use_container_width=True)

    # Drill-down: Cuisine spend
    st.subheader("🔍 Drill-down: Spend by Cuisine Type")
    fig = px.box(df, x="Cuisine_Preference", y="Avg_Spend_AED",
                 color="Cuisine_Preference", title="Spend Distribution by Cuisine",
                 color_discrete_sequence=PALETTE)
    fig.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Drill-down: Location × Tier sunburst
    st.subheader("🔍 Drill-down: Location → Tier → Adoption")
    fig = px.sunburst(df, path=["Restaurant_Location", "Restaurant_Tier", "App_Adoption"],
                      title="Location → Tier → Adoption Flow",
                      color_discrete_sequence=PALETTE)
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# 6. DELIVERY VS DINE-IN ANALYSIS
# =============================================================================

elif section == "6️⃣ Delivery vs Dine-in":
    st.title("6️⃣ Delivery vs Dine-in Analysis")

    dinein = df[df["Order_Channel"] == "Dine-in"]
    delivery = df[df["Order_Channel"] == "Delivery App"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Dine-in", f"{len(dinein):,} ({len(dinein)/len(df)*100:.1f}%)")
    c2.metric("Delivery", f"{len(delivery):,} ({len(delivery)/len(df)*100:.1f}%)")
    c3.metric("Dine-in Avg Spend", f"{dinein['Avg_Spend_AED'].mean():.0f} AED")
    c4.metric("Delivery Avg Spend", f"{delivery['Avg_Spend_AED'].mean():.0f} AED")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.pie(df, names="Order_Channel", title="Channel Distribution",
                     color_discrete_sequence=PALETTE, hole=0.4)
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.box(df, x="Order_Channel", y="Avg_Spend_AED", color="Order_Channel",
                     title="Spend by Channel", color_discrete_sequence=PALETTE)
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        fig = px.histogram(df, x="Weather_Behaviour", color="Order_Channel",
                           title="Weather Impact on Channel Choice",
                           color_discrete_sequence=PALETTE, barmode="group")
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        del_data = df[df["Delivery_Distance_km"].notna()]
        fig = px.scatter(del_data, x="Delivery_Distance_km", y="Est_Delivery_Time_min",
                         color="Avg_Spend_AED", opacity=0.6,
                         title="Delivery Distance vs Time (colored by spend)",
                         color_continuous_scale="Oranges")
        st.plotly_chart(fig, use_container_width=True)

    # Drill-down: Distance distribution
    st.subheader("🔍 Drill-down: Delivery Distance Distribution")
    fig = px.histogram(del_data, x="Delivery_Distance_km", nbins=25,
                       color="Distance_Category", title="Delivery Distance Distribution",
                       color_discrete_sequence=PALETTE)
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

    # Drill-down: Channel × Adoption
    st.subheader("🔍 Drill-down: Channel → Adoption Rate")
    ch_adopt = df.groupby("Order_Channel")["App_Adoption"].apply(
        lambda x: (x == "Yes").mean() * 100).reset_index()
    ch_adopt.columns = ["Order_Channel", "Adoption_Rate"]
    fig = px.bar(ch_adopt, x="Order_Channel", y="Adoption_Rate",
                 color="Adoption_Rate", color_continuous_scale="RdYlGn",
                 text="Adoption_Rate", title="Adoption Rate by Channel")
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(height=380)
    st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# 7. CORRELATION ANALYSIS
# =============================================================================

elif section == "7️⃣ Correlation Analysis":
    st.title("7️⃣ Correlation Analysis")

    num_cols = ["Avg_Spend_AED", "Surge_Multiplier", "Final_Order_Value",
                "Discount_Percentage", "Experience_Rating", "Table_Occupancy_Pct",
                "Delivery_Distance_km", "Est_Delivery_Time_min"]

    corr = df[num_cols].corr()
    fig = px.imshow(corr.round(2), text_auto=True, color_continuous_scale="RdBu_r",
                    title="Correlation Matrix — Numeric Variables",
                    zmin=-1, zmax=1)
    fig.update_layout(height=550)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        inc_order = ["<5000", "5000-10000", "10001-20000", "20001-35000", ">35000"]
        fig = px.box(df, x="Monthly_Income", y="Avg_Spend_AED",
                     color="Monthly_Income", title="Income vs Average Spend",
                     category_orders={"Monthly_Income": inc_order},
                     color_discrete_sequence=PALETTE)
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.scatter(df, x="Surge_Multiplier", y="Experience_Rating",
                         color="App_Adoption", opacity=0.4,
                         title="Surge vs Rating (colored by Adoption)",
                         color_discrete_sequence=[PALETTE[0], PALETTE[1]])
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    # Drill-down: Spend vs Final value
    st.subheader("🔍 Drill-down: Base Spend vs Final Value by Tier")
    fig = px.scatter(df, x="Base_Order_Value", y="Final_Order_Value",
                     color="Restaurant_Tier", opacity=0.5,
                     title="Base vs Final Order Value by Restaurant Tier",
                     color_discrete_sequence=PALETTE)
    fig.add_shape(type="line", x0=0, y0=0, x1=800, y1=800,
                  line=dict(dash="dash", color="gray"))
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# 8. CHALLENGES & FEATURES (ASSOCIATION RULE MINING PREVIEW)
# =============================================================================

elif section == "8️⃣ Challenges & Features (ARM Preview)":
    st.title("8️⃣ Challenges & Desired Features")
    st.markdown("*Preview of patterns for Association Rule Mining*")

    col1, col2 = st.columns(2)

    with col1:
        challenges = explode_col(df, "Challenges")
        ch_counts = challenges.value_counts().reset_index()
        ch_counts.columns = ["Challenge", "Count"]
        fig = px.bar(ch_counts, x="Count", y="Challenge", orientation="h",
                     title="Top Challenges Faced", color="Count",
                     color_continuous_scale="Reds", text="Count")
        fig.update_traces(textposition="outside")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        features = explode_col(df, "Desired_Features")
        ft_counts = features.value_counts().reset_index()
        ft_counts.columns = ["Feature", "Count"]
        fig = px.bar(ft_counts, x="Count", y="Feature", orientation="h",
                     title="Most Desired Features", color="Count",
                     color_continuous_scale="Greens", text="Count")
        fig.update_traces(textposition="outside")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    # Co-occurrence matrices
    st.subheader("🔍 Drill-down: Challenge Co-occurrence Matrix")

    ch_exploded = df["Challenges"].dropna().str.split(", ")
    all_ch = sorted(set(c for row in ch_exploded for c in row))
    cooc_ch = pd.DataFrame(0, index=all_ch, columns=all_ch)
    for row in ch_exploded:
        for a, b in combinations(row, 2):
            cooc_ch.loc[a, b] += 1
            cooc_ch.loc[b, a] += 1

    fig = px.imshow(cooc_ch, text_auto=True, color_continuous_scale="Reds",
                    title="Challenge Co-occurrence (pairs selected together)")
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🔍 Drill-down: Feature Co-occurrence Matrix")

    ft_exploded = df["Desired_Features"].dropna().str.split(", ")
    all_ft = sorted(set(f for row in ft_exploded for f in row))
    cooc_ft = pd.DataFrame(0, index=all_ft, columns=all_ft)
    for row in ft_exploded:
        for a, b in combinations(row, 2):
            cooc_ft.loc[a, b] += 1
            cooc_ft.loc[b, a] += 1

    fig = px.imshow(cooc_ft, text_auto=True, color_continuous_scale="Greens",
                    title="Feature Co-occurrence (pairs selected together)")
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

    # Challenge → Feature flow (top combos)
    st.subheader("🔍 Drill-down: Challenge → Feature Association Preview")
    # Build a simple cross-frequency
    ch_ft_pairs = []
    for _, row in df.iterrows():
        if pd.notna(row["Challenges"]) and pd.notna(row["Desired_Features"]):
            for ch in str(row["Challenges"]).split(", "):
                for ft in str(row["Desired_Features"]).split(", "):
                    ch_ft_pairs.append({"Challenge": ch.strip(), "Feature": ft.strip()})
    pairs_df = pd.DataFrame(ch_ft_pairs)
    top_pairs = pairs_df.groupby(["Challenge", "Feature"]).size().reset_index(name="Count")
    top_pairs = top_pairs.nlargest(15, "Count")
    fig = px.bar(top_pairs, x="Count", y="Challenge", color="Feature",
                 orientation="h", title="Top 15 Challenge → Feature Associations",
                 color_discrete_sequence=PALETTE, barmode="stack")
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# 9. APP ADOPTION DEEP DIVE
# =============================================================================

elif section == "9️⃣ App Adoption Deep Dive":
    st.title("9️⃣ App Adoption — Deep Dive")

    adopt_rate = (df["App_Adoption"] == "Yes").mean() * 100
    st.metric("Overall Adoption Rate", f"{adopt_rate:.1f}%")

    # Adoption by multiple dimensions
    dims = ["Age", "Monthly_Income", "Customer_Type", "Price_Sensitivity",
            "Fairness_Perception", "Order_Channel", "Restaurant_Tier",
            "Loyalty_Status", "Day_Preference", "Nationality_Cluster"]

    cols_per_row = 2
    for i in range(0, len(dims), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, dim in enumerate(dims[i:i+cols_per_row]):
            with cols[j]:
                adopt_by = df.groupby(dim)["App_Adoption"].apply(
                    lambda x: (x == "Yes").mean() * 100).sort_values(ascending=True).reset_index()
                adopt_by.columns = [dim, "Adoption_Rate"]
                fig = px.bar(adopt_by, x="Adoption_Rate", y=dim, orientation="h",
                             title=f"Adoption by {dim}", color="Adoption_Rate",
                             color_continuous_scale="RdYlGn", text="Adoption_Rate")
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

    # Drill-down: Multi-factor profile
    st.subheader("🔍 Drill-down: Adoption Rate by Sensitivity × Fairness")
    ct = pd.crosstab(df["Price_Sensitivity"], df["Fairness_Perception"])
    ct_adopt = df.pivot_table(values="App_Adoption",
                               index="Price_Sensitivity",
                               columns="Fairness_Perception",
                               aggfunc=lambda x: (x == "Yes").mean() * 100)
    sens_order = ["Very sensitive", "Moderately sensitive", "Slightly sensitive", "Not sensitive"]
    fair_order = ["Very fair", "Somewhat fair", "Neutral", "Unfair", "Very unfair"]
    ct_adopt = ct_adopt.reindex(index=sens_order, columns=fair_order)
    fig = px.imshow(ct_adopt.round(1), text_auto=True, color_continuous_scale="RdYlGn",
                    title="Adoption Rate %: Sensitivity × Fairness",
                    labels=dict(color="Adoption %"))
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# 10. SEASONALITY
# =============================================================================

elif section == "🔟 Seasonality":
    st.title("🔟 Seasonality Analysis")

    months = explode_col(df, "Peak_Months")
    m_counts = months.value_counts().reindex(["Oct-Dec", "Jan-Mar", "Apr-Jun", "Jul-Sep"]).reset_index()
    m_counts.columns = ["Season", "Selections"]

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(m_counts, x="Season", y="Selections", color="Season",
                     title="Peak Dining Seasons (selection count)",
                     color_discrete_sequence=PALETTE, text="Selections")
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, height=380)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Season by customer type
        df_months = df[["Customer_Type", "Peak_Months"]].dropna()
        df_months = df_months.assign(
            Peak_Months=df_months["Peak_Months"].str.split(", ")).explode("Peak_Months")
        ct = pd.crosstab(df_months["Customer_Type"], df_months["Peak_Months"])
        ct = ct.reindex(columns=["Oct-Dec", "Jan-Mar", "Apr-Jun", "Jul-Sep"])
        fig = px.imshow(ct, text_auto=True, color_continuous_scale="YlOrRd",
                        title="Peak Months by Customer Type")
        fig.update_layout(height=380)
        st.plotly_chart(fig, use_container_width=True)

    # Drill-down: Season × Demand
    st.subheader("🔍 Drill-down: Season & Demand Level")
    df_m2 = df[["Demand_Level", "Peak_Months"]].dropna()
    df_m2 = df_m2.assign(Peak_Months=df_m2["Peak_Months"].str.split(", ")).explode("Peak_Months")
    ct2 = pd.crosstab(df_m2["Peak_Months"], df_m2["Demand_Level"])
    ct2 = ct2.reindex(index=["Oct-Dec", "Jan-Mar", "Apr-Jun", "Jul-Sep"],
                      columns=["Low", "Medium", "High"])
    fig = px.imshow(ct2, text_auto=True, color_continuous_scale="Oranges",
                    title="Demand Level Distribution by Season")
    fig.update_layout(height=380)
    st.plotly_chart(fig, use_container_width=True)

    # Drill-down: Season × Weather
    st.subheader("🔍 Drill-down: Season × Weather Behaviour")
    df_m3 = df[["Weather_Behaviour", "Peak_Months"]].dropna()
    df_m3 = df_m3.assign(Peak_Months=df_m3["Peak_Months"].str.split(", ")).explode("Peak_Months")
    ct3 = pd.crosstab(df_m3["Peak_Months"], df_m3["Weather_Behaviour"])
    ct3 = ct3.reindex(index=["Oct-Dec", "Jan-Mar", "Apr-Jun", "Jul-Sep"])
    fig = px.imshow(ct3, text_auto=True, color_continuous_scale="Tealgrn",
                    title="Weather Behaviour by Season")
    fig.update_layout(height=380)
    st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# SANKEY: PATH TO ADOPTION
# =============================================================================

elif section == "🔀 Sankey: Path to Adoption":
    st.title("🔀 Sankey Diagram — Path to App Adoption")
    st.markdown("*How customer attributes flow through behaviour and attitudes to the North Star metric.*")

    # Build Sankey: Customer_Type → Price_Sensitivity → Fairness → Adoption
    # We aggregate flows between each stage

    def build_sankey_data(df, path_cols):
        """Build Sankey nodes and links from a sequence of columns."""
        all_labels = []
        for col in path_cols:
            for val in df[col].unique():
                label = f"{col}: {val}"
                if label not in all_labels:
                    all_labels.append(label)

        label_idx = {l: i for i, l in enumerate(all_labels)}

        sources, targets, values = [], [], []

        for i in range(len(path_cols) - 1):
            src_col = path_cols[i]
            tgt_col = path_cols[i + 1]
            flow = df.groupby([src_col, tgt_col]).size().reset_index(name="count")
            for _, row in flow.iterrows():
                src_label = f"{src_col}: {row[src_col]}"
                tgt_label = f"{tgt_col}: {row[tgt_col]}"
                sources.append(label_idx[src_label])
                targets.append(label_idx[tgt_label])
                values.append(row["count"])

        return all_labels, sources, targets, values

    path = ["Customer_Type", "Price_Sensitivity", "Fairness_Perception", "App_Adoption"]
    labels, sources, targets, values = build_sankey_data(df, path)

    # Color nodes
    node_colors = []
    for l in labels:
        if "App_Adoption: Yes" in l:
            node_colors.append("#1A936F")
        elif "App_Adoption: No" in l:
            node_colors.append("#E76F51")
        elif "Customer_Type" in l:
            node_colors.append("#004E89")
        elif "Price_Sensitivity" in l:
            node_colors.append("#F4A261")
        elif "Fairness" in l:
            node_colors.append("#2A9D8F")
        else:
            node_colors.append("#999999")

    # Color links based on target
    link_colors = []
    for t in targets:
        if "Yes" in labels[t]:
            link_colors.append("rgba(26,147,111,0.3)")
        elif "No" in labels[t]:
            link_colors.append("rgba(231,111,81,0.3)")
        else:
            link_colors.append("rgba(150,150,150,0.15)")

    # Clean labels for display
    display_labels = [l.split(": ", 1)[1] if ": " in l else l for l in labels]

    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15, thickness=25, line=dict(color="black", width=0.5),
            label=display_labels, color=node_colors
        ),
        link=dict(
            source=sources, target=targets, value=values, color=link_colors
        )
    ))
    fig.update_layout(
        title="Customer Type → Price Sensitivity → Fairness Perception → App Adoption",
        font_size=12, height=600
    )
    st.plotly_chart(fig, use_container_width=True)

    # Second Sankey: Channel → Demand → Surge Bucket → Adoption
    st.subheader("🔀 Channel → Demand → Adoption")

    df_s2 = df.copy()
    df_s2["Surge_Bucket"] = pd.cut(df_s2["Surge_Multiplier"],
                                     bins=[0, 0.95, 1.05, 1.5],
                                     labels=["Discount (<0.95)", "Neutral (0.95-1.05)", "Surge (>1.05)"])

    path2 = ["Order_Channel", "Demand_Level", "Surge_Bucket", "App_Adoption"]
    labels2, sources2, targets2, values2 = build_sankey_data(df_s2.dropna(subset=["Surge_Bucket"]), path2)

    node_colors2 = []
    for l in labels2:
        if "Yes" in l:
            node_colors2.append("#1A936F")
        elif "No" in l:
            node_colors2.append("#E76F51")
        elif "Channel" in l:
            node_colors2.append("#004E89")
        elif "Demand" in l:
            node_colors2.append("#F4A261")
        elif "Surge" in l or "Discount" in l or "Neutral" in l:
            node_colors2.append("#2A9D8F")
        else:
            node_colors2.append("#999999")

    link_colors2 = []
    for t in targets2:
        if "Yes" in labels2[t]:
            link_colors2.append("rgba(26,147,111,0.3)")
        elif "No" in labels2[t]:
            link_colors2.append("rgba(231,111,81,0.3)")
        else:
            link_colors2.append("rgba(150,150,150,0.15)")

    display_labels2 = [l.split(": ", 1)[1] if ": " in l else l for l in labels2]

    fig2 = go.Figure(go.Sankey(
        node=dict(
            pad=15, thickness=25, line=dict(color="black", width=0.5),
            label=display_labels2, color=node_colors2
        ),
        link=dict(
            source=sources2, target=targets2, value=values2, color=link_colors2
        )
    ))
    fig2.update_layout(
        title="Order Channel → Demand Level → Surge Bucket → App Adoption",
        font_size=12, height=600
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Third Sankey: Income → Tier → Location → Adoption
    st.subheader("🔀 Income → Tier → Location → Adoption")
    path3 = ["Monthly_Income", "Restaurant_Tier", "Restaurant_Location", "App_Adoption"]
    labels3, sources3, targets3, values3 = build_sankey_data(df, path3)

    node_colors3 = []
    for l in labels3:
        if "Yes" in l:
            node_colors3.append("#1A936F")
        elif "No" in l:
            node_colors3.append("#E76F51")
        elif "Income" in l:
            node_colors3.append("#004E89")
        elif "Tier" in l:
            node_colors3.append("#F4A261")
        elif "Location" in l:
            node_colors3.append("#2A9D8F")
        else:
            node_colors3.append("#999999")

    link_colors3 = []
    for t in targets3:
        if "Yes" in labels3[t]:
            link_colors3.append("rgba(26,147,111,0.3)")
        elif "No" in labels3[t]:
            link_colors3.append("rgba(231,111,81,0.3)")
        else:
            link_colors3.append("rgba(150,150,150,0.15)")

    display_labels3 = [l.split(": ", 1)[1] if ": " in l else l for l in labels3]

    fig3 = go.Figure(go.Sankey(
        node=dict(
            pad=15, thickness=25, line=dict(color="black", width=0.5),
            label=display_labels3, color=node_colors3
        ),
        link=dict(
            source=sources3, target=targets3, value=values3, color=link_colors3
        )
    ))
    fig3.update_layout(
        title="Income → Restaurant Tier → Location → App Adoption",
        font_size=12, height=600
    )
    st.plotly_chart(fig3, use_container_width=True)
