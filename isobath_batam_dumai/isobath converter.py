import pandas as pd
import re
import xml.etree.ElementTree as ET

def parse_average(name):
    nums = list(map(float, re.findall(r"\d+(?:\.\d+)?", name)))
    if not nums:
        return None
    return sum(nums) / len(nums)

# Load KML
tree = ET.parse("isobath_batam_rnd.kml")
root = tree.getroot()

ns = {'kml': 'http://www.opengis.net/kml/2.2'}

rows = []
component_id = 0

for placemark in root.findall(".//kml:Placemark", ns):

    name_elem = placemark.find("kml:name", ns)
    name = name_elem.text if name_elem is not None else ""
    avg_value = parse_average(name)

    # =========================
    # OUTER BOUNDARY
    # =========================
    outer = placemark.findall(".//kml:outerBoundaryIs//kml:coordinates", ns)

    for coords_elem in outer:
        coords_list = coords_elem.text.strip().split()

        for coord in coords_list:
            lon, lat, *_ = map(float, coord.split(","))
            rows.append({
                "ComponentId": component_id,
                "Layer": "Isobaths",
                "Type": "Isobath_shell",
                "Latitude": lat,
                "Longitude": lon,
                "Value1": avg_value,
                "Value2": avg_value
            })

        component_id += 1  # satu polygon luar = satu ID

    # =========================
    # INNER BOUNDARY (HOLE)
    # =========================
    inner = placemark.findall(".//kml:innerBoundaryIs//kml:coordinates", ns)

    for coords_elem in inner:
        coords_list = coords_elem.text.strip().split()

        for coord in coords_list:
            lon, lat, *_ = map(float, coord.split(","))
            rows.append({
                "ComponentId": component_id,
                "Layer": "Isobaths",
                "Type": "Isobath_hole",  # 🔥 beda type
                "Latitude": lat,
                "Longitude": lon,
                "Value1": avg_value,
                "Value2": avg_value
            })

        component_id += 1  # hole juga jadi komponen sendiri

# Save CSV
df = pd.DataFrame(rows)
df.to_csv("isobath_batam_rnd.csv", index=False)

print("Jumlah titik:", len(rows))
print("Sukses: CSV siap")