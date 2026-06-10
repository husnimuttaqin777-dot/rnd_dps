import json

with open("offset_steering.json", "r") as f:
    data_steering_offset = json.load(f)

print(data_steering_offset["steering1_offset"])

data_steering_offset["steering1_offset"] = 200
data_steering_offset["steering2_offset"] = 500

with open("offset_steering.json", "w") as f:
    json.dump(data_steering_offset, f, indent=4)