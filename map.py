import pandas as pd
import plotly.express as px
from urllib.request import urlopen
import json


# GeoJson Web Url
geoJson = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"

# Load GeoJSON data
with urlopen(geoJson) as response:
    counties = json.load(response)

counties["features"][0]


# Change the names of the CSVs to match your files
population_csv = "./csvs/population.csv"
hospital_csv = "./csvs/hospitals.csv"
rehab_csv = "./csvs/rehabs_within_30.csv"

# Load the population data
# Change the names input to match the column names in your CSV
# Make sure there are no headers in your CSV
# Change Data Types as needed
df = pd.read_csv(
    population_csv,
    names=[
        "fips",
        "Population",
        "Name",
        "Land Area (sq mi)",
        "Mean Income",
        "Mean Age",
    ],
    dtype={
        "fips": str,
        "Population": float,
        "Land Area (sq mi)": float,
        "Mean Income": float,
        "Mean Age": float,
    },
)


# Compute density
# If you want to add population density to your CSV
df["Density (pop/sq mi)"] = df["Population"] / df["Land Area (sq mi)"]


# Create the plot
# Change hover_data and labels as needed
# The color input determins what is used for the coloring of the map
# Change color_continuous_scale as needed
# Change range_color as needed
fig = px.choropleth(
    df,
    geojson=counties,
    locations="fips",
    color="Density (pop/sq mi)",
    color_continuous_scale="Viridis",
    range_color=(0, 300),
    scope="usa",
    labels={
        "Density (pop/sq mi)": "Density (pop/sq mi)",
    },
    hover_data={
        "Land Area (sq mi)",
        "Population",
        "Name",
        "Mean Age",
        "Mean Income",
        "Density (pop/sq mi)",
    },
)


# Load the hospital data
# Change the names input to match the column names in your CSV
# Make sure there are no headers in your CSV
# Change Data Types as needed
hf = pd.read_csv(
    hospital_csv,
    names=[
        "Id",
        "Name",
        "Address",
        "City",
        "State",
        "Zip",
        "Type",
        "Population",
        "latitude",
        "longitude",
        "Beds",
    ],
    dtype={"id": str},
)

# Create the plot
# Change hover_data and labels as needed
fig_h = px.scatter_geo(
    hf,
    lat="latitude",
    lon="longitude",
    hover_name="Name",
    hover_data=[
        "Id",
        "Address",
        "City",
        "State",
        "Zip",
        "Type",
        "Population",
        "Beds",
    ],
    title="Hospital Locations",
    scope="usa",
    color_discrete_sequence=["#ff0000"],
)

# Load the rehab data
# Change the names input to match the column names in your CSV
# Make sure there are no headers in your CSV
r3 = pd.read_csv(
    rehab_csv,
    names=[
        "Name",
        "Address",
        "latitude",
        "longitude",
        "State",
        "Hospital beds within 30 mi",
        "Rehabs within 30 mi",
        "Hospitals within 30 mi",
    ],
)

# Use if you want to calculate patients by splitting with other rehabs
r3["Patients"] = r3["Hospital beds within 30 mi"] / r3["Rehabs within 30 mi"]

# Create the plot
# Change hover_data and labels as needed
fig_px = px.scatter_geo(
    r3,
    lat="latitude",
    lon="longitude",
    hover_name="Name",
    hover_data=[
        "Address",
        "Patients",
        "Rehabs within 30 mi",
        "Hospital beds within 30 mi",
        "Hospitals within 30 mi",
    ],
    title="Filtered Hospital Locations",
    scope="usa",
    color_discrete_sequence=["#0000ff"],
)

# Adds the Hospital data points to the Population map
fig.add_trace(fig_h.data[0])
for i, frame in enumerate(fig.frames):
    fig.frames[i].data += (fig_h.frames[i].data[0],)

# Adds the Rehab data points to the Population map
fig.add_trace(fig_px.data[0])
for i, frame in enumerate(fig.frames):
    fig.frames[i].data += (fig_px.frames[i].data[0],)


fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig.show()
