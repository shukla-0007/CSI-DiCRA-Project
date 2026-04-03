import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Set page configuration
st.set_page_config(page_title="CSI Predictive Dashboard", layout="wide")

def main():
    st.title("🛡️ CSI: Compound Stress Index - Prediction Engine")
    st.markdown("### Next-Generation Climate Hazard Forecasting (Madhya Pradesh)")

    file_path = "data/processed/district_2026_2041_risk_trajectory.csv" 

    if not os.path.exists(file_path):
        st.error(f"❌ Predicted data file not found.")
        st.info("Run 'python src/engine_stage_2.py' first.")
        return

    # Load and clean data
    df = pd.read_csv(file_path)
    df = df.dropna(subset=['year'])
    df['year'] = df['year'].astype(int)
    
    available_years = sorted(df['year'].unique())

    # --- SIDEBAR LOGIC ---
    st.sidebar.header("Navigation")
    
    # Check if we have multiple years or just one
    if len(available_years) > 1:
        year_to_filter = st.sidebar.slider(
            "Select Forecast Year", 
            min_value=int(min(available_years)), 
            max_value=int(max(available_years)), 
            value=int(min(available_years))
        )
    elif len(available_years) == 1:
        year_to_filter = available_years[0]
        st.sidebar.info(f"Viewing Forecast for: **{year_to_filter}**")
        st.sidebar.caption("Note: Current dataset only provides single-year high-res projection.")
    else:
        st.error("No valid data found.")
        return

    # --- DASHBOARD CONTENT ---
    filtered_df = df[df['year'] == year_to_filter]

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(f"📊 Compound Stress Risk by District ({year_to_filter})")
        
        # Sort for better visualization
        chart_data = filtered_df.sort_values("csi_score", ascending=False)
        
        fig = px.bar(
            chart_data,
            x="district_name",
            y="csi_score",
            color="risk_tier",
            color_discrete_map={
                1: "#2ecc71", 2: "#f1c40f", 3: "#e67e22", 
                4: "#e74c3c", 5: "#9b59b6"
            },
            title="Aggregated CSI Stress Probability",
            category_orders={"risk_tier": [1, 2, 3, 4, 5]}
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("⚠️ Vulnerability Alerts")
        # Find high risk districts
        critical = filtered_df[filtered_df['risk_tier'] >= 3]
        if not critical.empty:
            for _, row in critical.iterrows():
                st.warning(f"**{row['district_name'].title()}**: Tier {row['risk_tier']} Risk")
        else:
            st.success("All districts within acceptable risk parameters.")

    # --- 15-YEAR TREND (STUB IF ONLY 1 YEAR EXISTS) ---
    st.markdown("---")
    st.subheader("📈 Long-Term Risk Trajectory")
    
    selected_dist = st.selectbox("Select District for Deep Dive", options=sorted(df['district_name'].unique()))
    
    dist_trend = df[df['district_name'] == selected_dist].sort_values("year")
    
    if len(available_years) > 1:
        line_fig = px.line(dist_trend, x="year", y="csi_score", markers=True)
        st.plotly_chart(line_fig, use_container_width=True)
    else:
        st.info(f"Historical vs Future comparison for {selected_dist.title()}")
        st.write(f"The predicted CSI score for the year 2030 is **{dist_trend['csi_score'].values[0]:.2f}**.")
        st.caption("Upload additional CMIP6 decades (2031-2040) to unlock trend lines.")

if __name__ == "__main__":
    main() 