import geopandas as gpd

# Path to your LGA shapefile (replace with your actual file path)
shapefile_path = "LGA_2024_AUST_GDA2020.shp"

# Load the shapefile
lga_data = gpd.read_file(shapefile_path)

# Display column names
print("Column Names in the Shapefile:")
print(lga_data.columns)

# Display the first few rows of data to understand its structure
print("\nFirst Few Rows of the Shapefile:")
print(lga_data.head())
