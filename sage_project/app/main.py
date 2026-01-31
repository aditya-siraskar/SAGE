import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys

# --- PATH SETUP ---
# Adds project root to python path so we can import the agent logic
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from sage_project.agent.skills.pdf_extractor.extract import PDFExtractor
from sage_project.agent.skills.satellite_fetcher.fetch_logic import SatelliteFetcher

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SAGE | Geo-Audit",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. VISUAL STYLING (CSS) ---
st.markdown("""
<style>
    /* Dark Theme Background */
    .stApp {
        background-color: #0E1117;
    }
    
    /* 1. HEADER GRADIENT */
    .header-container {
        padding: 3rem 2rem;
        border-radius: 15px;
        background: linear-gradient(120deg, #4f46e5, #0ea5e9);
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    .header-title {
        font-size: 3.5rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -2px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .header-subtitle {
        font-size: 1.2rem;
        font-weight: 300;
        opacity: 0.9;
        margin-top: 0.5rem;
    }

    /* 2. METRIC CARDS */
    div[data-testid="stMetric"] {
        background-color: #1a1c24;
        border: 1px solid #2d3748;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    div[data-testid="stMetricLabel"] {
        color: #a0aec0;
        font-size: 0.9rem;
    }
    div[data-testid="stMetricValue"] {
        color: white;
        font-size: 2rem;
    }

    /* 3. VERDICT BADGES (For the table) */
    .positive-badge { color: #4ade80; font-weight: bold; }
    .negative-badge { color: #f87171; font-weight: bold; }
    .neutral-badge { color: #94a3b8; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR (CONTROLS) ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Simple, clear headings as requested
    st.markdown("### 1. Upload Report")
    uploaded_file = st.file_uploader("Drop PDF here", type=["pdf"], label_visibility="collapsed")
    
    st.markdown("### 2. Set Timeline")
    col1, col2 = st.columns(2)
    start_year = col1.number_input("Baseline", value=2022, step=1)
    end_year = col2.number_input("Target", value=2023, step=1)
    
    st.markdown("---")
    run_btn = st.button("🚀 Run Analysis", type="primary", use_container_width=True)

# --- 4. MAIN SCREEN LOGIC ---

# HEADER SECTION (Always Visible)
st.markdown("""
    <div class="header-container">
        <div class="header-title">SAGE</div>
        <div class="header-subtitle">Satellite-Verified Environmental Intelligence</div>
    </div>
""", unsafe_allow_html=True)

# MAIN CONTENT
if not uploaded_file:
    # Empty State - Clean instruction
    st.info("👈 Please upload a PDF report in the sidebar to begin the audit.")

elif run_btn and uploaded_file:
    
    # A. INITIALIZATION
    progress_bar = st.progress(0, text="Initializing SAGE Agents...")
    
    # Save file
    temp_path = f"sage_project/data/temp/{uploaded_file.name}"
    os.makedirs("sage_project/data/temp", exist_ok=True)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Load Agents
    nlp_agent = PDFExtractor()
    sat_agent = SatelliteFetcher()
    
    # B. NLP PHASE
    claims = nlp_agent.extract_claims(temp_path)
    if not claims:
        progress_bar.empty()
        st.error("❌ No verifiable locations found in this document.")
        st.stop()
        
    progress_bar.progress(30, text=f"Found {len(claims)} sites. Accessing Satellite Feed...")

    # C. SATELLITE PHASE
    results = []
    
    for i, claim in enumerate(claims):
        bbox = claim['bbox']
        
        # Format Dates
        date_start = f"{start_year}-01-01/{start_year}-01-30"
        date_end   = f"{end_year}-01-01/{end_year}-01-30"
        
        # Fetch Data
        s1, _ = sat_agent.get_ndvi(bbox, date_start)
        s2, _ = sat_agent.get_ndvi(bbox, date_end)
        
        # Calculate Logic
        v1 = s1 if s1 else 0
        v2 = s2 if s2 else 0
        delta = v2 - v1
        
        # Verdict Logic
        sentiment = "NEUTRAL ⚖️"
        if delta > 0.05: sentiment = "POSITIVE ✅"
        elif delta < -0.05: sentiment = "SUSPICIOUS ⚠️"
        
        results.append({
            "Location": claim['loc'],
            "Lat": claim['coords'][0],
            "Lon": claim['coords'][1],
            "Baseline": round(v1, 3),
            "Target": round(v2, 3),
            "Change": round(delta, 3),
            "Sentiment": sentiment,
            "Claim": claim['text'][:80] + "..."
        })
        
        # Smooth Progress Bar
        prog = 30 + int(((i+1) / len(claims)) * 70)
        progress_bar.progress(prog, text=f"Auditing: {claim['loc']}")

    progress_bar.empty()
    df = pd.DataFrame(results)

    # --- D. DASHBOARD VISUALIZATION ---
    
    # 1. STATISTICS ROW
    st.markdown("### 📊 Mission Statistics")
    m1, m2, m3, m4 = st.columns(4)
    
    verified = len(df[df['Sentiment'].str.contains("POSITIVE")])
    suspicious = len(df[df['Sentiment'].str.contains("SUSPICIOUS")])
    
    m1.metric("Locations Audited", len(df))
    m2.metric("Verified Growth", verified)
    m3.metric("Suspicious Drops", suspicious, delta_color="inverse")
    m4.metric("Avg. Vegetation Change", f"{df['Change'].mean():.3f}")
    
    st.markdown("---")

    # 2. MAP & LIST COMPOSITE LAYOUT
    col_map, col_list = st.columns([1.5, 1])
    
    with col_map:
        st.subheader("🌍 Geospatial Verification")
        # Visual Map
        st.map(df, latitude="Lat", longitude="Lon", zoom=1, use_container_width=True)
        
    with col_list:
        st.subheader("📝 Location Sentiments")
        # Clean List View
        st.dataframe(
            df[["Location", "Change", "Sentiment"]],
            use_container_width=True,
            height=350,
            column_config={
                "Change": st.column_config.NumberColumn(
                    "NDVI Delta",
                    format="%.3f"
                ),
                "Sentiment": st.column_config.TextColumn(
                    "Verdict",
                    width="medium"
                )
            }
        )

    # 3. CHARTS SECTION
    st.markdown("---")
    st.subheader("📈 Deep Dive Analytics")
    
    chart1, chart2 = st.columns(2)
    
    with chart1:
        # A. NDVI Comparison (Grouped Bar Chart)
        # We need to melt the dataframe to make it suitable for a grouped bar chart
        df_melted = df.melt(id_vars=["Location"], value_vars=["Baseline", "Target"], var_name="Year", value_name="NDVI")
        
        fig_bar = px.bar(
            df_melted, 
            x="Location", 
            y="NDVI", 
            color="Year", 
            barmode="group",
            title="Vegetation Index: Baseline vs Target",
            color_discrete_sequence=["#94a3b8", "#4ade80"], # Grey (Old) -> Green (New)
            height=400
        )
        fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with chart2:
        # B. Verdict Distribution (Donut Chart)
        # Count values
        verdict_counts = df["Sentiment"].value_counts().reset_index()
        verdict_counts.columns = ["Verdict", "Count"]
        
        # Define colors mapping
        color_map = {
            "POSITIVE ✅": "#4ade80",
            "SUSPICIOUS ⚠️": "#f87171",
            "NEUTRAL ⚖️": "#94a3b8"
        }
        
        fig_pie = px.pie(
            verdict_counts, 
            values="Count", 
            names="Verdict",
            title="Audit Verdict Distribution",
            hole=0.4,
            color="Verdict",
            color_discrete_map=color_map,
            height=400
        )
        fig_pie.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig_pie, use_container_width=True)

    # 4. DOWNLOAD
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Full Audit Report",
        data=csv,
        file_name="sage_audit_report.csv",
        mime="text/csv",
        use_container_width=True
    )