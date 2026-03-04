# Required packages
import json
import pandas as pd
import openeo

# Connect to openEO
conn = openeo.connect(url="openeo.dataspace.copernicus.eu")

try:       
    conn = conn.authenticate_oidc(
        max_poll_time=60,  
        display=True
    )
    print("✅ Authentication successful")
except Exception as e:
    print(f"❌ Authentication failed: {e}")


# Load AOI GeoJSON (must be in data folder)
aoi_path = "data/one-plot.geojson"
with open(aoi_path) as f:
    aoi_geojson = json.load(f)


# Load Sentinel-2 collection
s2 = conn.load_collection(
    "SENTINEL2_L2A",
    temporal_extent=["2017-01-01", "2025-12-31"],
    bands=["B04", "B08", "B03", "SCL"]
)

# Scale to reflectance
red = s2.band("B04") / 10000.0
nir = s2.band("B08") / 10000.0
green = s2.band("B03") / 10000.0
scl = s2.band("SCL")

# NDWI computation
NDWI = (green - nir) / (green + nir + 1e-6)

# Cloud and water mask (SCL classes: 3, 6, 8, 9, 10) AND NDWI > 0.3
cloud_mask = (scl == 8) | (scl == 9) | (scl == 10) | (scl == 3) | (scl == 6)
water_mask = NDWI > 0.3
valid_mask = ~(cloud_mask | water_mask)

# Resample mask to 10m
valid_mask_10m = valid_mask.resample_cube_spatial(red)

# Apply mask
red_masked = red.mask(valid_mask_10m)
nir_masked = nir.mask(valid_mask_10m)

# Compute NDVI
ndvi_s2 = (nir_masked - red_masked) / (nir_masked + red_masked + 1e-6)


# Create monthly time series taking the median and compute the mean for the AOI
timeseries = ndvi_s2.aggregate_temporal_period("month", reducer="median").aggregate_spatial(geometries=aoi_geojson, reducer="mean")

# Download time series
job = timeseries.execute_batch(out_format="CSV", title="NDVI timeseries")

job.get_results().download_file("Outputs/timeseries-mean-monthly-ndvi.csv")

# Read time series as dataFrame
pd.read_csv("Outputs/timeseries-mean-monthly-ndvi.csv", index_col=0).head()

#Call a function that:
#.Smooths NDVI values appling the Savitzky–Golay
#2.Plot raw and smoothed values
#3.Create a new pd that stores the smoothed NDVI values

from phenology_utils import smooth_and_plot_ndvi

csv_file = "Outputs/timeseries-mean-monthly-ndvi.csv"

df, smoothed = smooth_and_plot_ndvi(
    csv_file,
    window_length=7,
    polyorder=2
)

