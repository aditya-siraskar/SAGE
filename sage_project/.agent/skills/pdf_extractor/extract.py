import pypdf
import spacy
from geopy.geocoders import Nominatim

class PDFExtractor:
    def __init__(self):
        print("🔧 DEBUG: Running V3 (Fixed Logic) - Isolated Sentences")
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
        # 1. First pass: Split into sentences
        main_doc = self.nlp(text)
        found = []
        
        keywords = ["planted", "restored", "reforestation", "conservation", "project", "located", "water", "mining", "replanted"]
        
        print(f"   Analysing {len(list(main_doc.sents))} sentences...")
        
        for sent in main_doc.sents:
            # 2. String isolation (This kills the link to the original doc)
            clean_text = sent.text.strip().replace("\n", " ")
            
            # Check keywords
            if any(k in clean_text.lower() for k in keywords):
                
                # 3. Create a totally new NLP object for just this string
                # This guarantees it cannot see "California" if it's not here
                iso_doc = self.nlp(clean_text)
                
                # Extract entities from the ISOLATED doc
                locs = [e.text for e in iso_doc.ents if e.label_ == "GPE"]
                
                # Debug print to prove what it sees
                # print(f"     [Debug] Sentence: '{clean_text[:20]}...' -> Found: {locs}")

                if locs:
                    found.append({"text": clean_text, "loc": locs[0]})
        
        return found

    def _geocode_claims(self, claims):
        results = []
        for c in claims:
            try:
                # Get coords
                loc = self.geolocator.geocode(c["loc"], timeout=10)
                if loc:
                    c["bbox"] = [loc.longitude - 0.05, loc.latitude - 0.05, loc.longitude + 0.05, loc.latitude + 0.05]
                    c["coords"] = (loc.latitude, loc.longitude)
                    results.append(c)
            except:
                continue
        return results