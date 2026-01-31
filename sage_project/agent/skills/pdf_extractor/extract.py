
import pypdf
import spacy
from geopy.geocoders import Nominatim

class PDFExtractor:
    def __init__(self):
        print("SUCCESS: Running V4 Logic (Expanded Entity Types)")
        self.nlp = spacy.load("en_core_web_sm")
        self.geolocator = Nominatim(user_agent="sage_project_student_final")

    def extract_claims(self, pdf_path):
        text = self._read_pdf(pdf_path)
        if not text: return []
        
        claims = self._find_locations(text)
        return self._geocode_claims(claims)

    def _read_pdf(self, path):
        try:
            reader = pypdf.PdfReader(path)
            return "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
        except Exception as e:
            print(f"Read Error: {e}")
            return ""

    def _find_locations(self, text):
        main_doc = self.nlp(text)
        found = []
        keywords = ["planted", "restored", "reforestation", "conservation", "project", "located", "water", "mining", "replanted"]
        
        # --- THE FIX ---
        # We accept these labels because the small model is dumb
        # PERSON = It thinks Bangalore is a person
        # NORP = It thinks Sumatra is a political group
        ACCEPTED_LABELS = ["GPE", "LOC", "ORG", "PERSON", "NORP"]

        for sent in main_doc.sents:
            clean_text = sent.text.strip().replace("\n", " ")
            
            if any(k in clean_text.lower() for k in keywords):
                # Isolate sentence
                iso_doc = self.nlp(clean_text)
                
                # Check for ANY of our accepted labels
                locs = [e.text for e in iso_doc.ents if e.label_ in ACCEPTED_LABELS]
                
                if locs:
                    found.append({"text": clean_text, "loc": locs[0]})
        return found

    def _geocode_claims(self, claims):
        results = []
        print(f"Geocoding {len(claims)} potential locations...")
        for c in claims:
            try:
                # Get coords
                loc = self.geolocator.geocode(c["loc"], timeout=10)
                if loc:
                    c["bbox"] = [loc.longitude - 0.05, loc.latitude - 0.05, loc.longitude + 0.05, loc.latitude + 0.05]
                    c["coords"] = (loc.latitude, loc.longitude)
                    results.append(c)
                    print(f"     Mapped '{c['loc']}' -> {c['coords']}")
            except:
                continue
        return results
