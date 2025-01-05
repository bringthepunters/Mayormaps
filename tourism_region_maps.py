import geopandas as gpd
import pandas as pd
import folium
import matplotlib.pyplot as plt

# File paths
shapefile_path = "LGA_2024_AUST_GDA2020.shp"  # Update this path
csv_path = "LGA&TOURISM_REGIONS.csv"

# Load LGA shapefile
lga_data = gpd.read_file(shapefile_path)

# Load Tourism Region data
tourism_data = pd.read_csv(csv_path)

# Merge shapefile and CSV on LGA name
merged_data = lga_data.merge(tourism_data, left_on="LGA_NAME24", right_on="LGA")

# Dissolve by Tourism Region
tourism_regions = merged_data.dissolve(by="Tourism Area")

# Save the dissolved shapefile for future use
tourism_regions.to_file("tourism_regions.shp")

# Ensure geometries are valid and non-empty
tourism_regions = tourism_regions[tourism_regions.is_valid]
tourism_regions = tourism_regions[tourism_regions.geometry.notnull()]

# Create an interactive map with Folium
tourism_map = folium.Map(location=[-37, 144], zoom_start=7)  # Adjust as needed
folium.GeoJson(tourism_regions.to_crs("EPSG:4326")).add_to(tourism_map)

# Save interactive map as HTML
tourism_map.save("tourism_regions_map.html")

# Plot static map for printing
tourism_regions.plot(cmap="tab20", figsize=(10, 10))
plt.title("Tourism Regions in Victoria")
plt.savefig("tourism_regions_map.png", dpi=300)  # Save as high-res image
plt.show()

print("Tourism Region maps have been created!")
