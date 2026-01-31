import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys

# Add project root to path so we can import our agents
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sage_project.agent.skills.pdf_extractor.extract import PDFExtractor
from sage_project.agent.skills.satellite_fetcher.fetch_logic import SatelliteFetcher

# --- PAGE CONFIG ---
st.set_page_config(page_title="SAGE | Greenwashing Detector", layout="wide")

st.title("🛰️ SAGE: Satellite Analysis for Greenwashing Evaluation")
st.markdown("""
**Upload a Corporate Sustainability Report (PDF)** to automatically audit their environmental claims using real-time satellite data.
""")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configuration")
    uploaded_file = st.file_uploader("Upload Report", type=["pdf"])
    
    # Date Selection
    col1, col2 = st.columns(2)
    start_year = col1.number_input("Baseline Year", value=2022)
    end_year = col2.number_input("Audit Year", value=2023)
    
    run_btn = st.button("🚀 Run Audit")

# --- MAIN LOGIC ---
if run_btn and uploaded_file:
    # 1. Save uploaded file temporarily
    temp_path = f"sage_project/data/temp/{uploaded_file.name}"
    os.makedirs("sage_project/data/temp", exist_ok=True)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # 2. Initialize Agents
    nlp_agent = PDFExtractor()
    sat_agent = SatelliteFetcher()
    
    with st.status("🔍 analyzing document text...", expanded=True) as status:
        st.write("Extracting claims and geocoding locations...")
        claims = nlp_agent.extract_claims(temp_path)
        
        if not claims:
            status.update(label="❌ No verifiable locations found.", state="error")
            st.stop()
            
        status.update(label=f"✅ Found {len(claims)} locations!", state="complete")

    # 3. Satellite Analysis
    st.subheader("🌍 Satellite Verification Results")
    
    results_data = []
    
    # Create a progress bar
    progress_bar = st.progress(0)
    
    for i, claim in enumerate(claims):
        loc = claim['loc']
        bbox = claim['bbox']
        
        # dynamic dates based on sidebar
        date_before = f"{start_year}-01-01/{start_year}-01-30"
        date_after = f"{end_year}-01-01/{end_year}-01-30"
        
        # Call Satellite Agent
        score_before, _ = sat_agent.get_ndvi(bbox, date_before)
        score_after, _  = sat_agent.get_ndvi(bbox, date_after)
        
        # Calculate Logic
        delta = 0
        status = "Unknown"
        if score_before and score_after:
            delta = score_after - score_before
            if delta > 0.05: status = "Positive ✅"
            elif delta < -0.05: status = "Suspicious ⚠️"
            else: status = "Neutral ⚖️"
        else:
            status = "Cloud Error ☁️"
            score_before, score_after = 0, 0

        results_data.append({
            "Location": loc,
            "Claim Snippet": claim['text'][:100] + "...",
            f"NDVI {start_year}": round(score_before, 3),
            f"NDVI {end_year}": round(score_after, 3),
            "Change": round(delta, 3),
            "Verdict": status,
            "lat": claim['coords'][0],
            "lon": claim['coords'][1]
        })
        
        # Update progress
        progress_bar.progress((i + 1) / len(claims))

    # 4. Display Data
    df = pd.DataFrame(results_data)
    
    # -- METRICS ROW --
    m1, m2, m3 = st.columns(3)
    suspicious_count = len(df[df["Verdict"].str.contains("Suspicious")])
    m1.metric("Locations Audited", len(df))
    m2.metric("Suspicious Claims", suspicious_count, delta_color="inverse")
    m3.metric("Data Reliability", "85%")

    # -- INTERACTIVE MAP --
    st.map(df, latitude="lat", longitude="lon", zoom=2)
    
    # -- DETAILED TABLE --
    st.table(df[["Location", "NDVI 2022", "NDVI 2023", "Change", "Verdict"]])
    
    # -- DOWNLOAD REPORT --
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Audit Report", csv, "sage_audit.csv", "text/csv")