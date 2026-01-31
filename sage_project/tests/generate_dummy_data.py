# ground-truth-esg/generate_dummy.py
from reportlab.pdfgen import canvas
import os

# Ensure the directory exists
# Ensure the directory exists
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
output_dir = os.path.join(project_root, "sage_project", "data", "raw")
os.makedirs(output_dir, exist_ok=True)

filename = os.path.join(output_dir, "test_report.pdf")

def create_pdf():
    print(f"Generating dummy PDF at: {filename}")
    c = canvas.Canvas(filename)
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, "SAGE Test Sustainability Report 2023")
    
    # Content (We put clear claims here to test our NLP)
    c.setFont("Helvetica", 12)
    
    # Claim 1: Specific City
    c.drawString(100, 750, "1. We initiated a massive reforestation project in Bangalore to improve urban air quality.")
    
    # Claim 2: Well-known Region
    c.drawString(100, 730, "2. Our water conservation efforts in California have restored 500 acres of wetlands.")
    
    # Claim 3: Noise (No location)
    c.drawString(100, 710, "3. We are committed to reducing plastic waste in all our offices globally.")
    
    # Claim 4: Specific Region in Indonesia
    c.drawString(100, 690, "4. Palm oil plantations in Sumatra were replanted with native species.")

    c.save()
    print("Dummy PDF created successfully!")

if __name__ == "__main__":
    create_pdf()