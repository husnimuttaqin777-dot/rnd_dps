import re

RPL_lat = []
RPL_long = []

with open("PKKPRL Dumai Rupat.kml", "r", encoding="utf-8") as f:
    data = f.read()

coords = re.findall(r"<coordinates>(.*?)</coordinates>", data)

for c in coords:
    lon, lat, alt = map(float, c.split(","))
    
    RPL_lat.append(lat)
    RPL_long.append(lon)

print("RPL_lat =", RPL_lat)
print("RPL_long =", RPL_long)