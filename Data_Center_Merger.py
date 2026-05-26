import pandas as pd

dcs = pd.read_csv("Data_centers_raw.csv")
uscounties = pd.read_csv("uscounties.csv")

dcmerged = pd.merge(dcs, 
                    uscounties, 
                    left_on = "County", 
                    right_on = "county")
dcmerged = dcmerged[["lat", "lng", "Low", "High"]]

with open("Geospatial_Data_Centers_2026.csv", "w") as f:
    dcmerged.to_csv(f, index=False)