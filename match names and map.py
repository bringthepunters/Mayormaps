import geopandas as gpd
import pandas as pd
import folium
import matplotlib.pyplot as plt

# File paths
shapefile_path = "LGA_2024_AUST_GDA2020.shp"  # Path to the shapefile
csv_path = "LGA&TOURISM_REGIONS.csv"  # Path to the CSV file

# LGA name mapping to handle discrepancies
lga_name_mapping = {
    'ararat': 'ararat rural city council',
    'bayside': 'bayside city council',
    'benalla': 'benalla rural city council',
    'colac otway': 'colac otway shire council',
    'horsham': 'horsham rural city council',
    'kingston': 'kingston city council',
    'latrobe': 'latrobe city council',
    'mildura': 'mildura rural city council',
    'queenscliff': 'queenscliffe borough council',
    'swan hill': 'swan hill rural city council',
    'wangaratta': 'wangaratta rural city council'
}

# Load the shapefile
print("Loading shapefile...")
lga_data = gpd.read_file(shapefile_path)

# Load the CSV
print("Loading CSV...")
csv_data = pd.read_csv(csv_path)

# Normalize LGA names
def normalize_name(name):
    if pd.isna(name):
        return ""
    return (
        name.lower()
        .replace(" city council", "")
        .replace(" shire council", "")
        .replace(" borough council", "")
        .replace(" rural city council", "")
        .replace("-", " ")
        .strip()
    )

# Apply normalization to both shapefile and CSV
print("Normalizing names...")
lga_data["LGA_NAME24"] = lga_data["LGA_NAME24"].apply(normalize_name)
csv_data["LGA_normalized"] = csv_data["LGA"].apply(normalize_name)

# Apply additional mapping for shapefile LGAs
print("Applying LGA name mapping...")
lga_data["LGA_NAME24"] = lga_data["LGA_NAME24"].replace(lga_name_mapping)

# Filter Victorian LGAs
print("Filtering Victorian LGAs...")
victorian_lgas = set(csv_data["LGA_normalized"])
vic_lga_shapefile = lga_data[lga_data["LGA_NAME24"].isin(victorian_lgas)]

# Merge shapefile and CSV
print("Merging shapefile and CSV...")
merged_data = vic_lga_shapefile.merge(csv_data, left_on="LGA_NAME24", right_on="LGA_normalized")

# Check unmatched LGAs
unmatched_lgas = set(vic_lga_shapefile["LGA_NAME24"]).difference(set(csv_data["LGA_normalized"]))
if unmatched_lgas:
    print("\nUnmatched LGAs from the shapefile (not in CSV):")
    print(unmatched_lgas)
    pd.DataFrame(list(unmatched_lgas), columns=["Unmatched LGAs"]).to_csv("unmatched_lgas.csv", index=False)
    print("Saved unmatched LGAs to 'unmatched_lgas.csv'.")

# Dissolve by Tourism Region
print("Dissolving LGAs into Tourism Regions...")
tourism_regions = merged_data.dissolve(by="Tourism Area")

# Rename columns for shapefile compatibility
tourism_regions = tourism_regions.rename(columns={
    "Tourism Area": "TourismAr",
    "LGA_normalized": "LGA_norm"
})

# Save the dissolved shapefile
print("Saving dissolved shapefile...")
tourism_regions.to_file("tourism_regions.shp")

# Save as GeoJSON for interactive mapping
tourism_regions.to_file("tourism_regions.geojson", driver="GeoJSON")

# Create an interactive map with Folium
print("Creating interactive map...")
tourism_map = folium.Map(location=[-37, 144], zoom_start=7)
for _, row in tourism_regions.iterrows():
    folium.GeoJson(
        row["geometry"],
        name=row.name,
        tooltip=folium.Tooltip(row.name)
    ).add_to(tourism_map)
tourism_map.save("tourism_regions_map.html")

# Static map with annotations
print("Creating static map...")
fig, ax = plt.subplots(1, 1, figsize=(12, 12))
tourism_regions.plot(cmap="tab20", ax=ax, legend=True)
for idx, row in tourism_regions.iterrows():
    if row.geometry.centroid.is_empty:
        continue
    plt.annotate(
        text=row.name,
        xy=(row.geometry.centroid.x, row.geometry.centroid.y),
        xytext=(0, 0),
        textcoords="offset points",
        horizontalalignment='center',
        fontsize=8,
        color="black"
    )
ax.set_title("Tourism Regions in Victoria", fontsize=16)
plt.savefig("tourism_regions_map_with_labels.png", dpi=300)
plt.show()

print("All files and maps with region names created successfully!")
