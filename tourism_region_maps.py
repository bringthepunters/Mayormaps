import geopandas as gpd
import pandas as pd
import folium
import matplotlib.pyplot as plt

# File paths
shapefile_path = "LGA_2024_AUST_GDA2020.shp"  # Update this path if needed
csv_path = "LGA&TOURISM_REGIONS.csv"  # Correct path to your CSV file

# Load LGA shapefile
try:
    lga_data = gpd.read_file(shapefile_path)
    print("Loaded LGA shapefile successfully.")
    print(f"LGA CRS: {lga_data.crs}")
except Exception as e:
    print(f"Error loading LGA shapefile: {e}")
    exit(1)

# Align CRS to EPSG:4326
try:
    lga_data = lga_data.to_crs("EPSG:4326")
    print(f"LGA CRS after transformation: {lga_data.crs}")
except Exception as e:
    print(f"Error aligning LGA CRS: {e}")
    exit(1)

# Load Tourism Region data
try:
    tourism_data = pd.read_csv(csv_path)
    print("Loaded Tourism Region CSV successfully.")
    print(f"Tourism Region columns: {tourism_data.columns}")
except Exception as e:
    print(f"Error loading CSV file: {e}")
    exit(1)

# Normalize LGA names to ensure matching
lga_data["LGA_NAME24"] = lga_data["LGA_NAME24"].str.strip().str.lower()
tourism_data["LGA"] = tourism_data["LGA"].str.strip().str.lower()

# Save unique LGA names for debugging
pd.DataFrame(lga_data["LGA_NAME24"].unique(), columns=["Shapefile LGA"]).to_csv("shapefile_lga_names.csv", index=False)
pd.DataFrame(tourism_data["LGA"].unique(), columns=["CSV LGA"]).to_csv("csv_lga_names.csv", index=False)
print("\nSaved unique LGA names to 'shapefile_lga_names.csv' and 'csv_lga_names.csv' for manual inspection.")

# Check for unmatched LGAs
unmatched_lgas = set(lga_data["LGA_NAME24"]).difference(set(tourism_data["LGA"]))
if unmatched_lgas:
    print("\nUnmatched LGAs found in shapefile (not in CSV):")
    print(unmatched_lgas)
    pd.DataFrame(list(unmatched_lgas), columns=["Unmatched LGAs"]).to_csv("unmatched_lgas.csv", index=False)
    print("Saved unmatched LGAs to 'unmatched_lgas.csv'.")

# Merge shapefile and CSV on LGA name
try:
    merged_data = lga_data.merge(tourism_data, left_on="LGA_NAME24", right_on="LGA")
    print("Merged shapefile and CSV successfully.")
    print(f"Merged data rows: {len(merged_data)}")
except KeyError as e:
    print(f"Error merging dataframes: {e}")
    print("Check that the LGA names in both files match.")
    exit(1)
except Exception as e:
    print(f"An unexpected error occurred during merging: {e}")
    exit(1)

# Filter out rows with null Tourism Areas
merged_data = merged_data[~merged_data["Tourism Area"].isnull()]

# Dissolve by Tourism Region
try:
    tourism_regions = merged_data.dissolve(by="Tourism Area")
    print("Dissolved LGAs into Tourism Regions successfully.")
    print(f"Tourism Regions rows: {len(tourism_regions)}")
except Exception as e:
    print(f"Error dissolving data: {e}")
    exit(1)

# Debugging: Log geometries at each step
print("\nBefore Filtering:")
print(f"Total geometries: {len(tourism_regions)}")

# Log invalid geometries
invalid_geometries = tourism_regions[~tourism_regions.is_valid]
if not invalid_geometries.empty:
    print("\nInvalid geometries found:")
    print(invalid_geometries)
else:
    print("No invalid geometries found.")

# Remove invalid geometries
tourism_regions = tourism_regions[tourism_regions.is_valid]
print("\nAfter Validity Check:")
print(f"Valid geometries: {len(tourism_regions)}")

# Ensure non-empty geometries
empty_geometries = tourism_regions[tourism_regions.geometry.is_empty]
if not empty_geometries.empty:
    print("\nEmpty geometries found:")
    print(empty_geometries)
else:
    print("No empty geometries found.")

# Drop empty geometries
tourism_regions = tourism_regions[~tourism_regions.geometry.is_empty]
print("\nAfter Empty Geometry Check:")
print(f"Non-empty geometries: {len(tourism_regions)}")

# Log geometries before saving
print("\nBefore Saving Shapefile:")
print(f"Total geometries remaining: {len(tourism_regions)}")

# Shorten column names to avoid ESRI Shapefile truncation
tourism_regions = tourism_regions.rename(columns={"Tourism Area": "TourismAr"})

# Save the dissolved shapefile for future use
try:
    tourism_regions.to_file("tourism_regions.shp")
    print("Saved shapefile as 'tourism_regions.shp'.")
except Exception as e:
    print(f"Error saving shapefile: {e}")

# Check if valid data exists before creating maps
if tourism_regions.empty:
    print("No valid geometries remain after processing. Exiting.")
    exit(1)

# Create an interactive map with Folium
try:
    tourism_map = folium.Map(location=[-37, 144], zoom_start=7)  # Adjust as needed
    folium.GeoJson(tourism_regions).add_to(tourism_map)
    tourism_map.save("tourism_regions_map.html")
    print("Saved interactive map as 'tourism_regions_map.html'.")
except Exception as e:
    print(f"Error creating interactive map: {e}")

# Plot static map for printing
try:
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    tourism_regions.plot(cmap="tab20", ax=ax)
    ax.set_title("Tourism Regions in Victoria", fontsize=16)
    plt.savefig("tourism_regions_map.png", dpi=300)  # Save as high-res image
    plt.show()
    print("Saved static map as 'tourism_regions_map.png'.")
except Exception as e:
    print(f"Error creating static map: {e}")
