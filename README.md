# 🛰️ SAGE / Temporal-Earth-Observation-for-Corporate-Audit

**SAGE (Satellite Analysis for Greenwashing Evaluation)** is an AI-powered auditing system that cross-references corporate sustainability claims with real-time earth observation data. 

It automatically reads PDF reports, extracts claimed project locations, and uses historical satellite imagery to verify if vegetation actually grew—detecting potential "greenwashing" in seconds.

---

## 🚀 How It Works (The Flow)

SAGE operates as a pipeline of three autonomous agents:

### 1. The Reader Agent (NLP Phase)
* **Input:** A Corporate Sustainability Report (PDF).
* **Action:** Scans the text using Natural Language Processing (NLP).
* **Logic:** Identifies specific environmental claims (e.g., *"We restored 500 hectares of forest in Bangalore"*).
* **Output:** Extracts the location name and converts it into Geocoordinates (Lat/Lon).

### 2. The Watcher Agent (Satellite Phase)
* **Input:** Coordinates + A user-defined timeline (e.g., 2022 vs. 2023).
* **Action:** Connects to the **Microsoft Planetary Computer** API.
* **Logic:** Fetches **Sentinel-2** satellite imagery for both time periods and calculates the **NDVI** (Normalized Difference Vegetation Index).
* **Output:** A vegetation health score (-1.0 to +1.0) for "Before" and "After."

### 3. The Judge (Auditing Phase)
* **Action:** Compares the two satellite scores.
* **Logic:**
    * `Delta > +0.05` → ✅ **Verified Positive** (Growth Detected).
    * `Delta < -0.05` → ⚠️ **Suspicious** (Vegetation Decreased).
    * `Else` → ⚖️ **Neutral** (No significant change).
* **Output:** A visual dashboard with maps, charts, and a downloadable audit report.

---

## 🛠️ Tech Stack & Design Choices

We chose a lightweight, open-source stack to ensure the project is reproducible and free to run.

| Component | Technology Used | Specific Use Case |
| :--- | :--- | :--- |
| **Language** | **Python 3.10+** | The standard for Data Science and Geospatial logic. |
| **Frontend** | **Streamlit** | Builds the interactive dashboard (Map/Charts) in pure Python without needing React/HTML. |
| **NLP** | **Spacy (`en_core_web_sm`)** | Extracts geopolitical entities (GPE) like cities and regions from raw text. |
| **Satellite Data** | **Microsoft Planetary Computer** | Provides free, token-less access to Sentinel-2 (10m resolution) imagery via STAC API. |
| **Geocoding** | **Geopy (Nominatim)** | Converts location names (strings) into GPS coordinates. |
| **Data Viz** | **Plotly Express** | Renders the interactive scatter maps and pie charts. |

---

## 🔄 Alternatives Considered

While designing SAGE, we evaluated other technologies. Here is why we chose our current stack:

### 1. Satellite Data Source
* **Current:** **Microsoft Planetary Computer** (Free, Open STAC standard).
* **Alternative:** **Google Earth Engine (GEE)**.
    * *Why not?* GEE requires a complex sign-up approval process and uses a proprietary Javascript/Python API that is harder to deploy locally.

### 2. NLP Engine
* **Current:** **Spacy (Small Model)**.
    * *Why?* It runs locally on any laptop without a GPU.
* **Alternative:** **OpenAI API (GPT-4)** or **HuggingFace BERT**.
    * *Why not?* LLMs are expensive (per token cost) and slow for scanning hundreds of pages. Spacy is instant and free.

### 3. Frontend
* **Current:** **Streamlit**.
    * *Why?* Rapid prototyping; allows us to focus on the data logic rather than CSS/state management.
* **Alternative:** **React + FastAPI**.
    * *Why not?* Too much boilerplate code for a data science project.

---

## 💻 Installation & Usage

1. **Clone the Repository**
   ```bash
   git clone [https://github.com/your-username/SAGE.git](https://github.com/your-username/SAGE.git)
   cd SAGE
