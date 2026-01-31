
import pystac_client
import stackstac
import planetary_computer
import numpy as np

class SatelliteFetcher:
    def __init__(self):
        print("🛰️ Initializing SAGE Satellite Link...")
        self.catalog = pystac_client.Client.open(
            "https://planetarycomputer.microsoft.com/api/stac/v1",
            modifier=planetary_computer.sign_inplace
        )

    def get_ndvi(self, bbox, date_range):
        """
        Fetches Sentinel-2 data and calculates NDVI.
        bbox: [min_lon, min_lat, max_lon, max_lat]
        """
        print(f"   Searching satellite data for: {date_range}...")
        
        # 1. Search for clear images (<10% clouds)
        search = self.catalog.search(
            collections=["sentinel-2-l2a"],
            bbox=bbox,
            datetime=date_range,
            query={"eo:cloud_cover": {"lt": 10}}, 
            max_items=1
        )
        
        items = list(search.items())
        if not items:
            return None, "❌ No clear images found."

        item = items[0]
        
        # 2. Robust EPSG Handling (The fix for your previous error)
        try:
            # Try getting the integer code directly
            epsg_code = item.properties["proj:epsg"]
        except KeyError:
            try:
                # If missing, try parsing the string "EPSG:32643" -> 32643
                epsg_string = item.properties["proj:code"]
                epsg_code = int(epsg_string.split(":")[-1])
            except (KeyError, ValueError):
                # Fallback to Web Mercator if all else fails
                epsg_code = 3857 

        # 3. Stream Data (Red + NIR bands)
        try:
            stack = stackstac.stack(
                item,
                assets=["B04", "B08"], 
                bounds_latlon=bbox,     
                resolution=10,
                epsg=epsg_code
            )
            
            # Download the actual pixels now
            data = stack.compute()
            
            # 4. Calculate NDVI
            nir = data.sel(band="B08").astype("float32")
            red = data.sel(band="B04").astype("float32")
            
            # Formula: (NIR - Red) / (NIR + Red)
            ndvi = (nir - red) / (nir + red + 1e-8)
            mean_score = float(ndvi.mean().values)
            
            return mean_score, f"✅ Success (Image ID: {item.id})"
            
        except Exception as e:
            return None, f"❌ Error processing image: {str(e)}"
