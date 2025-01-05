import pandas as pd
import geopandas as gpd

# File paths
shapefile_path = "LGA_2024_AUST_GDA2020.shp"  # Shapefile with all LGAs
csv_path = "LGA&TOURISM_REGIONS.csv"  # CSV with full LGA names

# Load the shapefile
print("Loading shapefile...")
lga_data = gpd.read_file(shapefile_path)

# Load the CSV
print("Loading CSV...")
csv_data = pd.read_csv(csv_path)

# Filter Victorian LGAs from shapefile
print("Filtering Victorian LGAs...")
victorian_lgas = [
    "alpine", "ararat", "ballarat", "banyule", "bass coast", "baw baw", "bayside (vic.)",
    "benalla", "boroondara", "brimbank", "buloke", "campaspe", "cardinia", "casey",
    "central goldfields", "colac otway", "corangamite", "darebin", "east gippsland",
    "frankston", "gannawarra", "glen eira", "glenelg", "golden plains", "greater bendigo",
    "greater dandenong", "greater geelong", "greater shepparton", "hepburn", "hindmarsh",
    "hobsons bay", "horsham", "hume", "indigo", "kingston (vic.)", "knox",
    "latrobe (vic.)", "loddon", "macedon ranges", "manningham", "mansfield", "maribyrnong",
    "maroondah", "melbourne", "melton", "merri-bek", "mildura", "mitchell", "moira",
    "monash", "moonee valley", "moorabool", "mornington peninsula", "mount alexander",
    "moyne", "murrindindi", "nillumbik", "northern grampians", "port phillip", "pyrenees",
    "queenscliffe", "south gippsland", "southern grampians", "stonnington", "strathbogie",
    "surf coast", "swan hill", "towong", "wangaratta", "warrnambool", "wellington",
    "west wimmera", "whitehorse", "whittlesea", "wodonga", "wyndham", "yarra",
    "yarra ranges", "yarriambiack"
]

# Filter the shapefile for Victorian LGAs
lga_data["LGA_NAME24"] = lga_data["LGA_NAME24"].str.strip().str.lower()
vic_lga_shapefile = lga_data[lga_data["LGA_NAME24"].isin(victorian_lgas)]

# Normalize CSV names (remove council-related terms)
csv_data["LGA_normalized"] = csv_data["LGA"].str.strip().str.lower()
csv_data["LGA_normalized"] = (
    csv_data["LGA_normalized"]
    .str.replace(" city council", "", regex=False)
    .str.replace(" rural city council", "", regex=False)
    .str.replace(" shire council", "", regex=False)
    .str.replace("borough council", "", regex=False)
)

# Perform mapping
print("Performing LGA name mapping...")
mapped_lgas = []
unmatched_lgas = []

for shapefile_lga in vic_lga_shapefile["LGA_NAME24"].unique():
    # Try to find a match in the normalized CSV names
    match = csv_data[csv_data["LGA_normalized"] == shapefile_lga]
    if not match.empty:
        mapped_lgas.append({"Shapefile LGA": shapefile_lga, "Mapped Full Name": match.iloc[0]["LGA"]})
    else:
        unmatched_lgas.append(shapefile_lga)

# Save matched LGAs
mapped_df = pd.DataFrame(mapped_lgas)
mapped_df.to_csv("mapped_victorian_lgas.csv", index=False)
print(f"Saved mapped Victorian LGAs to 'mapped_victorian_lgas.csv'.")

# Save unmatched LGAs
unmatched_df = pd.DataFrame(unmatched_lgas, columns=["Unmatched Shapefile LGA"])
unmatched_df.to_csv("unmatched_victorian_lgas.csv", index=False)
print(f"Saved unmatched Victorian LGAs to 'unmatched_victorian_lgas.csv'.")
