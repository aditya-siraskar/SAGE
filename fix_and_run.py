import os

# 1. Define the CORRECT logic (V3)
correct_code = r'''
import pypdf
import spacy
from geopy.geocoders import Nominatim

class PDFExtractor:
    def __init__(self):
        print("✅ SUCCESS: Running the FIXED V3 Code (Isolated Logic)")
        self.nlp = spacy.load("en_core_web_sm")
        self.geolocator = Nominatim(user_agent="sage_project_student_v3")

    def extract_claims(self, pdf_path):
        text = self._read_pdf(pdf_path)
        if not text: return []
        
        claims = self._find_locations(text)
        return self._geocode_claims(claims)

    def _read_pdf(self, path):
        try:
            reader = pypdf.PdfReader(path)
            return "\n".join([p.extract_text() for p in reader.pages[:5] if p.extract_text()])
        except Exception as e:
            print(f"❌ Read Error: {e}")
            return ""

    def _find_locations(self, text):
        main_doc = self.nlp(text)
        found = []
        keywords = ["planted", "restored", "reforestation", "conservation", "project", "located", "water", "mining", "replanted"]
        
        print(f"   Analysing {len(list(main_doc.sents))} sentences...")
        
        for sent in main_doc.sents:
            # Clean and ISOLATE the sentence string
            clean_text = sent.text.strip().replace("\n", " ")
            
            if any(k in clean_text.lower() for k in keywords):
                # Create NEW NLP object for just this sentence
                iso_doc = self.nlp(clean_text)
                
                # Extract entities from the ISOLATED doc
                locs = [e.text for e in iso_doc.ents if e.label_ == "GPE"]
                
                if locs:
                    found.append({"text": clean_text, "loc": locs[0]})
        return found

    def _geocode_claims(self, claims):
        results = []
        for c in claims:
            try:
                loc = self.geolocator.geocode(c["loc"], timeout=10)
                if loc:
                    c["bbox"] = [loc.longitude - 0.05, loc.latitude - 0.05, loc.longitude + 0.05, loc.latitude + 0.05]
                    c["coords"] = (loc.latitude, loc.longitude)
                    results.append(c)
                    print(f"     📍 Mapped '{c['loc']}' -> {c['coords']}")
            except:
                continue
        return results
'''

# 2. Path to the file we need to overwrite
target_path = os.path.join("sage_project", "agent", "skills", "pdf_extractor", "extract.py")

# 3. Force Write
print(f"🔧 Overwriting file at: {target_path}")
with open(target_path, "w", encoding="utf-8") as f:
    f.write(correct_code)
print("✅ File overwritten successfully.")

# 4. Run the Test immediately
print("\n--- STARTING TEST ---")
import sys
sys.path.append(os.getcwd()) # Add current folder to path
from sage_project.agent.skills.pdf_extractor.extract import PDFExtractor

pdf_path = os.path.join("sage_project", "data", "raw", "test_report.pdf")
agent = PDFExtractor()
results = agent.extract_claims(pdf_path)

print("\n--- FINAL RESULTS ---")
for i, item in enumerate(results):
    print(f"\nClaim #{i+1} Target: {item['loc']}")
    print(f"Coords: {item['coords']}")