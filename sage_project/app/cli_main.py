import sys
import os

# Ensure we can import from our local folders
sys.path.append(os.getcwd())

from sage_project.agent.skills.pdf_extractor.extract import PDFExtractor
from sage_project.agent.skills.satellite_fetcher.fetch_logic import SatelliteFetcher

def run_sage_analysis(pdf_filename):
    print("\n" + "="*50)
    print(f"   🚀 SAGE SYSTEM ACTIVATED: Analyzing {pdf_filename}")
    print("="*50 + "\n")

    # 1. Initialize Agents
    nlp_agent = PDFExtractor()
    sat_agent = SatelliteFetcher()

    # 2. Define File Path
    pdf_path = os.path.join("sage_project", "data", "raw", pdf_filename)
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: File not found at {pdf_path}")
        return

    # 3. Extract Claims (Phase 1)
    print(f"\n📖 Reading Report...")
    claims = nlp_agent.extract_claims(pdf_path)
    
    if not claims:
        print("❌ No verifyable locations found.")
        return

    print(f"\n✅ Found {len(claims)} locations to verify.\n")

    # 4. Verify with Satellite (Phase 2)
    print("🛰️ REQUESTING SATELLITE IMAGERY...")
    print("-" * 60)
    
    for i, claim in enumerate(claims):
        loc = claim['loc']
        text = claim['text'][:80] + "..." # Truncate for display
        
        print(f"\n🔎 [Target #{i+1}] {loc}")
        print(f"   📝 Claim: \"{text}\"")
        
        # We compare Jan 2022 vs Jan 2023 (1 year interval)
        # In a real app, you would extract dates from the text too
        date_before = "2022-01-01/2022-01-30"
        date_after  = "2023-01-01/2023-01-30"
        
        score_before, msg_b = sat_agent.get_ndvi(claim['bbox'], date_before)
        score_after,  msg_a = sat_agent.get_ndvi(claim['bbox'], date_after)
        
        # 5. The Logic (The "Judge")
        if score_before and score_after:
            delta = score_after - score_before
            
            print(f"   📅 2022 NDVI: {score_before:.3f}")
            print(f"   📅 2023 NDVI: {score_after:.3f}")
            print(f"   📊 Change:    {delta:+.3f}")
            
            # --- THE VERDICT ---
            if delta > 0.05:
                print("   ✅ VERDICT: POSITIVE IMPACT (Vegetation Increased)")
            elif delta < -0.05:
                print("   ⚠️ VERDICT: SUSPICIOUS (Vegetation Decreased)")
            else:
                print("   ⚖️ VERDICT: NEUTRAL (No significant change)")
        else:
            print("   ❌ Satellite Data Unavailable (Cloud cover or API error)")
            
    print("\n" + "="*50)
    print("   🏁 ANALYSIS COMPLETE")
    print("="*50)

if __name__ == "__main__":
    # You can change this to any PDF you drop in the folder
    run_sage_analysis("test_report.pdf")