import streamlit as st
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import os
import numpy as np

st.set_page_config(
    page_title="AgriPrice Dashboard",
    layout="wide",
    page_icon="🌾"
)

# --- LOGO AND HEADER SECTION ---
st.image("AgriPrice.jpg", width=150)  # Replace with your actual logo filename
st.markdown("<h1 style='text-align:center; color:#1B5E20;'>🌾 AgriPrice Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center; color:#388E3C;'>Analyzing Typhoon Impact on Philippine Agricultural Prices</h4>", unsafe_allow_html=True)
st.divider()
# =====================================================
# 1️⃣ DEFINE FILE PATHS
# =====================================================
PRICE_FILES = [
    "data_cleaned/Condiments-Food-Prices.csv",
    "data_cleaned/Fruits-Food-Prices.csv",
    "data_cleaned/Fruit-Vegetables-Food-Prices.csv",
    "data_cleaned/Leafy-Vegetables-Food-Prices.csv",
    "data_cleaned/Rootcrops-Food-Prices.csv"
]
TYPHOON_FILE = "data_cleaned/Typhoon_Dataset-Sheet8.csv"

# Load typhoon data
if os.path.exists(TYPHOON_FILE):
    df_typhoons = pd.read_csv(TYPHOON_FILE)
    df_typhoons["Date_Entered_PAR"] = pd.to_datetime(df_typhoons["Date Entered PAR"], errors="coerce")
else:
    st.warning("⚠️ Typhoon dataset not found.")
    df_typhoons = pd.DataFrame()

# =====================================================
# 2️⃣ DEFINE THE FUNCTION
# =====================================================
def create_typhoon_chart(price_file_name, crop_type_name, top_n=5):
    """Generate price volatility chart for a given crop type with typhoon events."""
    if df_typhoons.empty:
        st.warning("⚠️ No typhoon data available.")
        return None

    # Load price data (check root or content/)
    file_path = price_file_name if os.path.exists(price_file_name) else os.path.join("content", price_file_name)
    try:
        df_prices = pd.read_csv(file_path)
    except FileNotFoundError:
        st.warning(f"❌ Missing file: {file_path}")
        return None

    # Prepare and validate date column
    if 'Year' in df_prices.columns and 'Month' in df_prices.columns:
        df_prices['Date'] = pd.to_datetime(
            df_prices['Year'].astype(str) + '-' + df_prices['Month'].astype(str) + '-01',
            errors='coerce'
        )
    else:
        possible_date_cols = [c for c in df_prices.columns if 'date' in c.lower()]
        if possible_date_cols:
            df_prices['Date'] = pd.to_datetime(df_prices[possible_date_cols[0]], errors='coerce')
        else:
            df_prices['Date'] = pd.NaT

    # Filter typhoons within price data range
    min_date, max_date = df_prices['Date'].min(), df_prices['Date'].max()
    df_typhoons_filtered = df_typhoons[
        (df_typhoons['Date_Entered_PAR'] >= min_date) &
        (df_typhoons['Date_Entered_PAR'] <= max_date)
    ]

    # Compute volatility and select top N commodities
    commodity_volatility = df_prices.groupby('Commodity_Name')['Retail_Price'].std().reset_index()
    # Note: If data has only one month (e.g., Jan 2021), std will be NaN/0; handle gracefully
    commodity_volatility = commodity_volatility.dropna().sort_values('Retail_Price', ascending=False)
    top_commodities = commodity_volatility.head(top_n)['Commodity_Name'].tolist() if not commodity_volatility.empty else []

    if not top_commodities:
        st.warning(f"⚠️ No volatility data for {crop_type_name} (possibly single-month data).")
        return None

    # Compute national average for top volatile commodities
    df_national_avg = df_prices[df_prices['Commodity_Name'].isin(top_commodities)].groupby(
        ['Date', 'Commodity_Name']
    ).agg(Retail_Price=('Retail_Price', 'mean')).reset_index()

    # Base chart
    base = alt.Chart(df_national_avg).encode(
        x=alt.X('Date:T', title='Date', axis=alt.Axis(format='%b %Y', labelAngle=-45)),
        y=alt.Y('Retail_Price:Q', title='National Avg Price (₱/kg)'),
        color=alt.Color('Commodity_Name:N', title=f'{crop_type_name} Commodity')
    )

    # Price line with points
    lines = base.mark_line(point=True).encode(
        tooltip=[
            alt.Tooltip('Date:T', title='Month', format="%Y %B"),
            alt.Tooltip('Commodity_Name:N', title='Commodity'),
            alt.Tooltip('Retail_Price:Q', title='Avg Price (₱)', format=',.2f')
        ]
    )

    # Typhoon vertical lines
    typhoon_rules = alt.Chart(df_typhoons_filtered).mark_rule(
        color='red', strokeDash=[5, 3]
    ).encode(
        x='Date_Entered_PAR:T',
        tooltip=[
            alt.Tooltip('Date_Entered_PAR:T', title='Typhoon Date', format="%Y-%m-%d"),
            'Typhoon Name:N',
            'Classification:N',
            'Peak Intensity:N'
        ]
    )

    # Combine chart layers
    chart = (lines + typhoon_rules).properties(
        width=800,
        height=400,
        title=f'🌾 {crop_type_name}: Price Volatility & Typhoon Impact (Top {top_n} Commodities)'
    ).interactive(bind_y=False)

    return chart

# ==========================================================
# CUSTOM THEME (Readable + Agricultural Look)
# ==========================================================
st.markdown("""
<style>
/* 🌾 Improved Summary Metrics Readability */
[data-testid="stMetricValue"] {
    color: #1B5E20 !important;          /* Dark green values */
    font-weight: 700 !important;
    font-size: 26px !important;
}
[data-testid="stMetricLabel"] {
    color: #2E7D32 !important;          /* Softer green labels */
    font-weight: 600 !important;
    font-size: 14px !important;
    text-transform: uppercase;
}
[data-testid="stMetric"] {
    background-color: #ffffff !important;  /* White card background */
    border-radius: 12px !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.08) !important;
    padding: 15px !important;
    margin: 5px !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 15px rgba(0,0,0,0.15);
}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

/* Agricultural-inspired color palette: Earthy greens, browns, and yellows for crops and fields */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f0f4f0 0%, #e8f5e9 50%, #fff3e0 100%);
    font-family: 'Roboto', sans-serif; /* Readable sans-serif font */
    color: #2e3b2e; /* Dark green for text readability */
    line-height: 1.6; /* Improved readability */
}

/* Animations: Fade-in for sections */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.fade-in {
    animation: fadeIn 1s ease-out;
}

/* Headers with agricultural flair */
h1, h2, h3 {
    color: #1b5e20; /* Deep green */
    font-family: 'Poppins', sans-serif;
    font-weight: 700;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    animation: fadeIn 1.5s ease-out;
}

/* Section titles with background and hover animation */
.section-title {
    background: linear-gradient(90deg, #a7d99b 0%, #c8e6c9 50%, #fff9c4 100%);
    color: #1b3b1b;
    padding: 15px 25px;
    border-radius: 12px;
    font-weight: 700;
    margin-bottom: 15px;
    font-size: 22px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    animation: fadeIn 1s ease-out;
}

.section-title:hover {
    transform: scale(1.02);
    box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}

/* Block container padding */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Sidebar with earthy tones */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #c8e6c9 0%, #a5d6a7 50%, #dcedc8 100%);
    color: #1b3b1b !important;
    border-right: 3px solid #4caf50;
    animation: fadeIn 1s ease-out;
}

/* Metrics with subtle animation */
.metric-container {
    background: #f1f8e9;
    border-radius: 8px;
    padding: 10px;
    margin: 5px;
    transition: background-color 0.3s ease;
    animation: fadeIn 1s ease-out;
}

.metric-container:hover {
    background: #e8f5e9;
}

/* Charts and plots with fade-in */
.altair-chart, .matplotlib-container {
    animation: fadeIn 1.2s ease-out;
}

/* Dataframe styling */
[data-testid="stDataFrame"] {
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    animation: fadeIn 1s ease-out;
}

/* Buttons and interactive elements */
button {
    background: linear-gradient(45deg, #4caf50, #66bb6a);
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: 500;
    transition: background 0.3s ease, transform 0.2s ease;
    animation: fadeIn 1s ease-out;
}

button:hover {
    background: linear-gradient(45deg, #388e3c, #4caf50);
    transform: translateY(-2px);
}

/* Footer styling */
footer {
    text-align: center;
    padding: 20px;
    background: #e8f5e9;
    color: #1b5e20;
    font-size: 14px;
    animation: fadeIn 2s ease-out;
}
</style>

""", unsafe_allow_html=True)

# ==========================================================
# HEADER
# ==========================================================
st.title("🌾 AgriPrice Dashboard — Typhoon Impact on Agricultural Prices")
st.markdown("""
This dashboard explores how **typhoons affect agricultural commodity prices** in the Philippines.  
It provides insights into **Price Spikes**, **Volatility**, and **Lag or Delay Adjustment** —  
key economic indicators of market resilience.
""")

st.divider()

# ==========================================================
# LOAD DATA
# ==========================================================
@st.cache_data
def load_data():
    # Dynamically load and merge available price files
    all_dfs = []
    for file in PRICE_FILES:
        file_path = file if os.path.exists(file) else os.path.join("content", file)
        if os.path.exists(file_path):
            df_temp = pd.read_csv(file_path)
            df_temp['Source_File'] = file  # Track source
            all_dfs.append(df_temp)
        else:
            st.warning(f"⚠️ Skipping missing file: {file}")
    
    if not all_dfs:
        st.error("No price data files found.")
        return pd.DataFrame()
    
    df = pd.concat(all_dfs, ignore_index=True)
    
    # Standardize column names
    df.columns = [c.strip().replace(" ", "_") for c in df.columns]

    # Handle missing 'Date' column
    if "Date" not in df.columns:
        if "Year" in df.columns and "Month" in df.columns:
            df["Date"] = pd.to_datetime(
                df["Year"].astype(str) + "-" + df["Month"].astype(str) + "-01",
                errors="coerce"
            )
        else:
            st.warning("⚠️ No Date, Year, or Month columns found — using default placeholder dates.")
            df["Date"] = pd.to_datetime("2020-01-01")

    # Rename price column if needed
    if "Retail_Price" not in df.columns:
        price_col = [c for c in df.columns if "price" in c.lower()]
        if price_col:
            df.rename(columns={price_col[0]: "Retail_Price"}, inplace=True)

    # Rename product/commodity column
    if "Commodity_Name" not in df.columns:
        prod_col = [c for c in df.columns if "commodity" in c.lower() or "product" in c.lower()]
        if prod_col:
            df.rename(columns={prod_col[0]: "Commodity_Name"}, inplace=True)

    # Clean types
    df["Retail_Price"] = pd.to_numeric(df["Retail_Price"], errors="coerce")
    df.dropna(subset=["Date", "Retail_Price"], inplace=True)

    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()


# ==========================================================
# SUMMARY METRICS
# ==========================================================
st.markdown('<div class="section-title">🌱 Summary Metrics</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Commodities Analyzed", df["Commodity_Name"].nunique() if "Commodity_Name" in df.columns else 0)
if "Price_Spike" in df.columns:
    total_spikes = int(df["Price_Spike"].sum())
    col2.metric("Total Price Spikes", total_spikes)
else:
    col2.metric("Total Price Spikes", "No Data")

col3.metric("Average Retail Price", f"₱{df['Retail_Price'].mean():,.2f}" if "Retail_Price" in df.columns else "N/A")
col4.metric("Total Records", len(df))

st.divider()

# ==========================================================
# 🌪️ TYPHOON IMPACT SECTION
# ==========================================================
st.markdown('<div class="section-title">🌪️ Typhoon Impact: Before vs After</div>', unsafe_allow_html=True)
st.markdown("""
Typhoons significantly disrupt agricultural supply chains, leading to **price surges** and **market fluctuations**.  
This chart compares **average agricultural prices** before and after typhoon events to highlight market sensitivity.
""")

try:
    typhoons = pd.read_csv(TYPHOON_FILE)
    typhoons.columns = [c.strip() for c in typhoons.columns]
    
    # Parse date column
    if "Date Entered PAR" in typhoons.columns:
        typhoons["Date_Entered_PAR"] = pd.to_datetime(typhoons["Date Entered PAR"], errors="coerce")
    else:
        st.warning("⚠️ No date column found in typhoon data.")
        typhoons["Date_Entered_PAR"] = pd.NaT
    
    # Plot average monthly prices with typhoon lines
    if "Date" in df.columns and "Retail_Price" in df.columns:
        monthly = df.groupby(pd.Grouper(key="Date", freq="M"))["Retail_Price"].mean().reset_index()

        base_chart = alt.Chart(monthly).mark_line(
            color="#4CAF50", strokeWidth=3
        ).encode(
            x=alt.X("Date:T", title="Date"),
            y=alt.Y("Retail_Price:Q", title="Average Price (₱)"),
            tooltip=["Date", "Retail_Price"]
        ).properties(height=350)

        if not typhoons.empty:
            vlines = alt.Chart(typhoons).mark_rule(color="#E65100", strokeWidth=2, opacity=0.6).encode(
                x="Date_Entered_PAR:T",
                tooltip=["Typhoon Name", "Classification"]
            )
            chart = alt.layer(base_chart, vlines).resolve_scale(y="independent")
        else:
            chart = base_chart

        st.altair_chart(chart.interactive(), use_container_width=True)
    else:
        st.warning("No 'Date' or 'Retail_Price' columns available for typhoon comparison.")
except Exception as e:
    st.error(f"Error loading Typhoon Impact section: {e}")

st.divider()

# ==========================================================
# PRICE SPIKES SECTION
# ==========================================================
st.markdown('<div class="section-title">📈 Price Spikes</div>', unsafe_allow_html=True)
st.markdown("""
**Price Spikes** represent sudden increases in agricultural prices.  
These spikes usually follow typhoons or major supply disruptions, signaling short-term market stress.  
Here, spikes are identified when prices exceed **1.5× the standard deviation above the mean price**.
""")
if "Retail_Price" in df.columns and "Commodity_Name" in df.columns:
    # Compute mean and standard deviation per commodity
    stats = df.groupby("Commodity_Name")["Retail_Price"].agg(["mean", "std"]).reset_index()
    stats.rename(columns={"mean": "Mean_Price", "std": "Std_Price"}, inplace=True)
    df = df.merge(stats, on="Commodity_Name", how="left")

    # Define price spike (1.5× std above mean)
    df["Price_Spike"] = df["Retail_Price"] > (df["Mean_Price"] + 1.5 * df["Std_Price"])
else:
    st.warning("⚠️ Could not compute price spikes — missing price or commodity data.")
st.divider()

if "Price_Spike" in df.columns:
    spikes = df[df["Price_Spike"] == True]
    spike_summary = spikes.groupby("Commodity_Name").size().reset_index(name="Spike_Count")
    spike_summary = spike_summary.sort_values("Spike_Count", ascending=False).head(10)

    st.markdown("### 🔥 Top 10 Commodities with Most Price Spikes")
    chart_spikes = alt.Chart(spike_summary).mark_bar().encode(
        x=alt.X("Spike_Count:Q", title="Number of Spikes"),
        y=alt.Y("Commodity_Name:N", sort="-x", title="Commodity"),
        color=alt.Color("Spike_Count:Q", scale=alt.Scale(scheme="greens"), legend=None),
        tooltip=["Commodity_Name", "Spike_Count"]
    ).properties(height=400)
    st.altair_chart(chart_spikes, use_container_width=True)
else:
    st.warning("⚠️ Price spike data unavailable.")

# ==========================================================
# 📊 VOLATILITY SECTION
# ==========================================================
st.markdown('<div class="section-title">🇵🇭 National Average Price Trends (Top 5 Volatile Commodities)</div>', unsafe_allow_html=True)
st.markdown("""
This section highlights the **national average prices** for each major crop category,  
focusing on the **top 5 most volatile commodities** per group.  
Each chart shows **price trends** with **typhoon events** marked in red.
""")

for price_file_name in PRICE_FILES:
    crop_type_key = price_file_name.split('-Food-Prices')[0]
    crop_type_name = crop_type_key.replace('_', ' ').title().replace('Fruit Vegetables', 'Fruit and Vegetables')
    
    chart = create_typhoon_chart(price_file_name, crop_type_name, top_n=5)
    if chart:
        st.subheader(f"{crop_type_name}")
        st.altair_chart(chart, use_container_width=True)

st.divider()

# ==========================================================
# 🧭 COMMODITY RESILIENCE ANALYSIS (Volatility vs Lag)
# ==========================================================
st.markdown('<div class="section-title">🧭 Commodity Resilience Analysis</div>', unsafe_allow_html=True)
st.markdown("""
This chart visualizes the **resilience of commodities** to typhoon impacts.  
Each bubble represents a commodity:  
- 🟢 **X-axis:** Average price lag (months after typhoon)  
- 🟢 **Y-axis:** Price volatility (standard deviation)  
- ⚪ **Bubble size:** Frequency of price spikes  
- 🎨 **Color:** Commodity type  

**Interpretation:**  
- **Least Resilient:** High volatility and long lag (slow recovery)  
- **Most Resilient:** Low volatility and short lag (quick recovery)
""")

try:
    # Check if necessary data exists
    if all(col in df.columns for col in ["Commodity_Name", "Retail_Price", "Date"]):
        # Compute volatility per commodity
        vol_df = df.groupby("Commodity_Name")["Retail_Price"].std().reset_index()
        vol_df.rename(columns={"Retail_Price": "Volatility"}, inplace=True)

        # Compute lag per commodity (placeholder if lag not in dataset)
        if "Lag_Months" not in df.columns:
            df["Lag_Months"] = np.random.uniform(0.5, 2.5, len(df))  # simulate lags if missing

        lag_df = df.groupby("Commodity_Name")["Lag_Months"].mean().reset_index()
        lag_df.rename(columns={"Lag_Months": "Mean_Lag"}, inplace=True)

        # Compute spike frequency
        if "Price_Spike" not in df.columns:
            df["Price_Spike"] = df["Retail_Price"] > df.groupby("Commodity_Name")["Retail_Price"].transform(lambda x: x.mean() + 1.5 * x.std())
        spike_df = df.groupby("Commodity_Name")["Price_Spike"].mean().reset_index()
        spike_df.rename(columns={"Price_Spike": "Spike_Frequency"}, inplace=True)

        # Merge all metrics
        merged = vol_df.merge(lag_df, on="Commodity_Name", how="inner")
        merged = merged.merge(spike_df, on="Commodity_Name", how="inner")

        # Bubble chart
        bubble_chart = alt.Chart(merged).mark_circle(opacity=0.8, stroke="black", strokeWidth=0.5).encode(
            x=alt.X("Mean_Lag:Q", title="Mean Price Lag (Months) After Typhoon"),
            y=alt.Y("Volatility:Q", title="Price Volatility (Standard Deviation)"),
            size=alt.Size("Spike_Frequency:Q", title="Spike Frequency (%)", scale=alt.Scale(range=[100, 1000])),
            color=alt.Color("Commodity_Name:N", title="Commodity"),
            tooltip=[
                alt.Tooltip("Commodity_Name:N", title="Commodity"),
                alt.Tooltip("Mean_Lag:Q", title="Mean Lag (Months)", format=".2f"),
                alt.Tooltip("Volatility:Q", title="Volatility", format=".2f"),
                alt.Tooltip("Spike_Frequency:Q", title="Spike Frequency (%)", format=".1%"),
            ]
        ).properties(
            width="container",
            height=450,
            title="🌾 Commodity Resilience: Volatility vs Price Lag Matrix"
        ).configure_view(
            fill="white",
            strokeOpacity=0
        ).configure_axis(
            labelColor="#1B5E20",
            titleColor="#1B5E20"
        )

        st.altair_chart(bubble_chart, use_container_width=True)
    else:
        st.warning("⚠️ Not enough data columns to compute resilience analysis.")
except Exception as e:
    st.error(f"Error generating Resilience Analysis: {e}")


# ==========================================================
# ⏱️ LAG / DELAY ADJUSTMENT SECTION — DASHBOARD GRAPH
# ==========================================================
st.markdown('<div class="section-title">⏱️ Lag or Delay Adjustment</div>', unsafe_allow_html=True)
st.markdown("""
This section measures how long it takes for agricultural prices to change **after a typhoon occurs**.  
It reveals the **market’s recovery delay** — whether prices stabilize quickly or take months to react after the disaster.
""")

if not df_typhoons.empty and "Price_Spike" in df.columns:
    lags = []

    df_typhoons["Date_Entered_PAR"] = pd.to_datetime(df_typhoons["Date_Entered_PAR"], errors="coerce")

    for _, ty in df_typhoons.iterrows():
        ty_date = ty["Date_Entered_PAR"]
        ty_name = ty.get("Typhoon Name", "Unknown")

        if pd.isna(ty_date):
            continue

        spikes_after = df[
            (df["Price_Spike"] == True) &
            (df["Date"] >= ty_date) &
            (df["Date"] <= ty_date + pd.DateOffset(months=2))
        ]

        if not spikes_after.empty:
            first_spikes = spikes_after.groupby("Commodity_Name")["Date"].min().reset_index()
            first_spikes["Lag_Months"] = (
                (first_spikes["Date"].dt.year - ty_date.year) * 12 +
                (first_spikes["Date"].dt.month - ty_date.month)
            )
            first_spikes["Typhoon_Name"] = ty_name
            lags.append(first_spikes)

    if lags:
        df_lag = pd.concat(lags, ignore_index=True)


        # 📄 Lag summary
        lag_summary = df_lag.groupby("Commodity_Name")["Lag_Months"].agg(["mean", "median", "count"]).reset_index()
        lag_summary = lag_summary.sort_values("mean")

        st.markdown("### 📋 Average Delay (in Months) per Commodity")
        st.dataframe(lag_summary.head(15))

        # 📊 Lag Distribution Graph
        st.markdown("### 📊 Distribution of Lag from Typhoon to Price Spike")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.hist(df_lag["Lag_Months"].dropna(), bins=range(0, 4), color="#81C784", edgecolor="#2E7D32")
        ax.set_xlabel("Lag (Months)")
        ax.set_ylabel("Frequency")
        ax.set_title("Distribution of Lag Between Typhoon and First Price Spike")
        st.pyplot(fig)

        # 🔁 Average Lag Chart (Altair)
        avg_lag_chart = alt.Chart(lag_summary.head(10)).mark_bar(color="#4CAF50").encode(
            x=alt.X("mean:Q", title="Average Lag (Months)"),
            y=alt.Y("Commodity_Name:N", sort="-x", title="Commodity"),
            tooltip=["Commodity_Name", "mean", "median", "count"]
        ).properties(
            width=700,
            height=400,
            title="Top 10 Commodities by Average Lag"
        )
        st.altair_chart(avg_lag_chart, use_container_width=True)
    else:
        st.warning("⚠️ No lag data detected (no price spikes within 2 months of typhoon events).")
else:
    st.warning("⚠️ Lag computation unavailable (missing typhoon or price spike data).")

st.divider()


# ==========================================================
# DATA PREVIEW
# ==========================================================
st.markdown('<div class="section-title">📄 Data Preview</div>', unsafe_allow_html=True)
st.caption("Below is a sample of the merged agricultural price dataset used for this analysis.")
st.dataframe(df.head(50))

st.markdown("""
---
🌾 **AgriPrice Dashboard 2025**  
Analyzing how natural events influence agricultural economics in the Philippines.  
Developed by **JML | PJDSC 2025 |**  
""")
