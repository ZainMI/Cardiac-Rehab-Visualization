import time
import pandas as pd
import haversine as hs


# Computes distance between two points


def distance(lat1, lon1, lat2, lon2):
    return hs.haversine((lat1, lon1), (lat2, lon2)) * 0.621371


# Set the Radius of the search
max_distance = 30

# Change the names of the CSVs to match your files
rehab_csv = "rehabs.csv"
hospital_csv = "hospitals.csv"
output_csv = f"rehabs_within_{max_distance}.csv"

# Load the rehab data
# Change the names input to match the column names in your CSV
# Make sure there are no headers in your CSV
rehabs = pd.read_csv(
    rehab_csv,
    names=["name", "address", "latitude", "longitude", "state", "beds", "rehabs"],
)

# Load the hospital data
# Change the names input to match the column names in your CSV
# Make sure there are no headers in your CSV
hospitals = pd.read_csv(
    hospital_csv,
    names=[
        "id",
        "name",
        "address",
        "city",
        "state",
        "zip",
        "type",
        "population",
        "latitude",
        "longitude",
        "beds",
    ],
    dtype={"id": str},
)

# Initialize a new column for total bed count
# Depends on your dataset and what you want to do
# rehabs["hos within 30"] = 0

# Initialize a new dataframe to store the results
new_df = pd.DataFrame(
    columns=[
        "id",
        "name",
        "address",
        "city",
        "state",
        "zip",
        "type",
        "population",
        "latitude",
        "longitude",
        "beds",
    ]
)

# Computes distance between each rehab and hospital
# Only adds hospital to new_df if it is outside of the max_distance
time_start = time.time()
for hospital_index, hospital_row in hospitals.iterrows():
    within = True
    for rehab_index, rehab_row in rehabs.iterrows():
        d = distance(
            rehab_row["latitude"],
            rehab_row["longitude"],
            hospital_row["latitude"],
            hospital_row["longitude"],
        )
        if d <= max_distance:
            within = False
    if within:
        new_df = new_df.append(rehab_row)


time_end = time.time()

print(f"Time: {time_end - time_start}")
new_df.to_csv(output_csv, index=False)
print("Completed")
