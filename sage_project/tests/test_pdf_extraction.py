import sys
import os

# --- PATH FIX ---
# Point to the PROJECT ROOT (2 levels up from tests/)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)
# ----------------

from sage_project.agent.skills.pdf_extractor.extract import PDFExtractor

# Create path to our dummy file
# We look in sage_project/data/raw
pdf_path = os.path.join(project_root, "sage_project", "data", "raw", "test_report.pdf")

def test_reader():
    print("--- TESTING PHASE 1: NLP READER ---")
    
    # Check if file exists first
    if not os.path.exists(pdf_path):
        print(f"❌ Error: Test PDF not found at {pdf_path}")
        print("   Did you run 'generate_dummy.py' inside the new folder?")
        return

    # Initialize
    agent = PDFExtractor()
    
    # Run
    results = agent.extract_claims(pdf_path)
    
    print("\n--- FINAL RESULTS ---")
    if not results:
        print("⚠️ No results found. Check your keywords or PDF content.")
        
    for i, item in enumerate(results):
        print(f"\nClaim #{i+1}:")
        print(f"Text:   {item['text']}")
        print(f"Target: {item['loc']}")
        print(f"Coords: {item['coords']}")

if __name__ == "__main__":
    test_reader()