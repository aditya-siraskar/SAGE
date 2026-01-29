import spacy

# 1. Load the model
print("⏳ Loading Spacy model...")
nlp = spacy.load("en_core_web_sm")

# 2. The exact text from your dummy PDF
sentences = [
    "We initiated a massive reforestation project in Bangalore to improve urban air quality.",
    "Our water conservation efforts in California have restored 500 acres of wetlands.",
    "Palm oil plantations in Sumatra were replanted with native species."
]

print("\n--- 🕵️ NER DIAGNOSTIC REPORT ---")

for text in sentences:
    doc = nlp(text)
    print(f"\nSentence: '{text}'")
    
    if not doc.ents:
        print("   ❌ NO ENTITIES FOUND. (The model is blind to this location)")
    
    for ent in doc.ents:
        # Print the text and the label (GPE, LOC, ORG, etc.)
        print(f"   👉 Found: '{ent.text}' | Label: {ent.label_}")

print("\n--------------------------------")
print("💡 IF Bangalore/Sumatra show up as 'LOC' or 'ORG', we just need to update the code to accept those labels.")