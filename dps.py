######  PROGRAM MEMANGGIL WINDOWS PYQT5 ##########################

####### memanggil library PyQt5 ##################################

#---------------------------------------------------------------#
import sys
import datetime as dt
import numpy as np
import csv
import json
import glob



from PyQt5.QtCore import * 
from PyQt5.QtGui import * 
from PyQt5.QtQml import * 
from PyQt5.QtWidgets import *
from PyQt5.QtQuick import * 
import sys
import time
import paho.mqtt.client as paho
import numpy as np
from math import sqrt


import math
from math import sin, cos, sqrt, atan2, radians, atan
#----------------------------------------------------------------#
from PyQt5.QtPositioning import QGeoCoordinate
from collections import defaultdict
import threading




isobath_file = "isobath_batam.csv"


intersection_points = []
lines_with_intersection = []


payout = 0

def find_intersection_theta(A, B, P, theta_deg):
    theta_rad = np.radians(theta_deg)

    v_AB = np.array(B) - np.array(A)
    v_theta = np.array([np.cos(theta_rad), np.sin(theta_rad)])

    M = np.column_stack((v_AB, -v_theta))
    rhs = np.array(P) - np.array(A)

    if np.linalg.matrix_rank(M) < 2:
        return None

    try:
        sol = np.linalg.solve(M, rhs)
        s = sol[0]
        intersection = np.array(A) + s * v_AB

        # Pastikan arah dari P ke intersection sesuai arah theta
        direction_vec = intersection - np.array(P)
        if np.dot(direction_vec, v_theta) < 0:
            return None

        # Pastikan titik potong di segmen AB
        if not (0 <= s <= 1):
            return None

        return intersection
    except np.linalg.LinAlgError:
        return None





#################Joystick

from math import sqrt


def geo_to_dict(coord):
    return {"latitude": coord.latitude(), "longitude": coord.longitude()}

def get_color(value):
    return (
        "#a80000" if value < 0 else
        "#df4000" if value < 4 else
        "#f37700" if value < 8 else
        "#f8ab00" if value < 12 else
        "#f8d800" if value < 16 else
        "#f2f200" if value < 20 else
        "#cef400" if value < 24 else
        "#87e602" if value < 28 else
        "#21d824" if value < 32 else
        "#00c846" if value < 36 else
        "#00b46b" if value < 40 else
        "#009d8d" if value < 44 else
        "#00b8d3" if value < 48 else
        "#00daf8" if value < 60 else
        "white"
    )

def rdp_simplify(points, epsilon=0.00003):
    if len(points) < 3:
        return points
    def dist(p, a, b):
        if a == b:
            return math.hypot(p[0]-a[0], p[1]-a[1])
        dx, dy = b[0]-a[0], b[1]-a[1]
        mag = math.hypot(dx, dy)
        u = max(0, min(1, ((p[0]-a[0])*dx + (p[1]-a[1])*dy) / (mag*mag)))
        return math.hypot(p[0]-(a[0]+u*dx), p[1]-(a[1]+u*dy))
    def rdp(pts):
        if len(pts) < 3: return pts
        s, e = pts[0], pts[-1]
        md, mi = max((dist(pts[i], s, e), i) for i in range(1, len(pts)-1))
        if md > epsilon:
            return rdp(pts[:mi+1])[:-1] + rdp(pts[mi:])
        return [s, e]
    tuples = [(p.latitude(), p.longitude()) for p in points]
    return [QGeoCoordinate(lat, lon) for lat, lon in rdp(tuples)]

def load_depth_points_from_isobath(file_path=isobath_file):
    pts = []
    with open(file_path, newline='') as f:
        for row in csv.DictReader(f):
            try:
                pts.append((float(row["Latitude"]), float(row["Longitude"]),
                             float(row["Value1"]) if row["Value1"] else 0.0))
            except ValueError:
                continue
    return pts  # list of (lat, lon, depth) tuples — faster than dicts

def find_two_nearest_points(lat, lon, depth_points):
    # Uses tuples now: (lat, lon, depth)
    if not depth_points:
        return None
    key = lambda p: (lat - p[0])**2 + (lon - p[1])**2
    s = sorted(depth_points, key=key)
    if len(s) >= 2:
        return s[0], s[1]
    return s[0], s[0]

def idw_from_two_points(lat, lon, p1, p2, power=2):
    d1 = math.hypot(lat - p1[0], lon - p1[1])
    d2 = math.hypot(lat - p2[0], lon - p2[1])
    if d1 == 0: return p1[2]
    if d2 == 0: return p2[2]
    w1 = 1 / d1**power
    w2 = 1 / d2**power
    return (w1*p1[2] + w2*p2[2]) / (w1 + w2)

def load_polygons(label_min_zoom_area=0.0001):
    component_polygons = defaultdict(lambda: {"points": [], "type": "", "value": 0.0})
    with open(isobath_file, newline='') as f:
        for row in csv.DictReader(f):
            try:
                cid = int(row["ComponentId"])
                lat = float(row["Latitude"])
                lon = float(row["Longitude"])
                val = float(row["Value1"]) if row["Value1"] else 0.0
            except ValueError:
                continue
            component_polygons[cid]["points"].append((lat, lon))
            component_polygons[cid]["type"] = row["Type"]
            component_polygons[cid]["value"] = val

    polygons = []
    for comp in component_polygons.values():
        raw = comp["points"]
        if len(raw) < 3:
            continue
        coords = rdp_simplify([QGeoCoordinate(la, lo) for la, lo in raw])
        if len(coords) < 3:
            continue
        lats = [c.latitude()  for c in coords]
        lons = [c.longitude() for c in coords]
        val  = comp["value"]
        area = (max(lats)-min(lats)) * (max(lons)-min(lons))
        polygons.append({
            "points":    [geo_to_dict(p) for p in coords],
            "type":      comp["type"],
            "value":     f"{val:.1f}",
            "color":     get_color(val),
            "center":    {"latitude": sum(lats)/len(lats), "longitude": sum(lons)/len(lons)},
            "showLabel": area >= label_min_zoom_area,
        })
    print(f"Loaded {len(polygons)} polygons "
          f"(avg {sum(len(p['points']) for p in polygons)//max(len(polygons),1)} pts each)")
    return polygons





rpl1_lat = [1.153244444444444, 1.1533, 1.153038888888889, 1.152772222222222, 1.152508333333333, 1.152022222222222, 1.151761111111111, 1.151686111111111, 1.151613888888889, 1.151258333333333, 1.151258333333333, 1.150755555555556, 1.150252777777778, 1.149750833333333, 1.149247222222222, 1.148697222222222, 1.148022222222222, 1.146836111111111, 1.145575, 1.144311111111111, 1.14305, 1.141786111111111, 1.140561111111111, 1.139358333333333, 1.139241666666667, 1.139069444444444]

rpl1_long = [103.8943583333333, 103.8949166666667, 103.8962397222222, 103.8975638888889, 103.8988852777778, 103.9001272222222, 103.9014202777778, 103.9027675, 103.9041147222222, 103.9054622222222, 103.9067638888889, 103.9080138888889, 103.9092669444445, 103.9105194444444, 103.9117722222222, 103.9130027777778, 103.9141555555556, 103.9147444444445, 103.9152222222222, 103.9156972222222, 103.9161722222222, 103.91665, 103.9172111111111, 103.9178222222222, 103.9188333333333, 103.9191]

names = []
colors = []

n = len(rpl1_lat)

names = [str(i+1) for i in range(n)]
colors = ["black"] * n

rpl2_lat = [1.652269444444444, 1.652316666666667, 1.652963888888889, 1.653, 1.653038888888889, 1.6538, 1.65515, 1.655158333333334, 1.656647222222222, 1.657602777777778, 1.659116666666666, 1.660066666666666, 1.661325, 1.663758333333333, 1.663794444444444, 1.663836111111111, 1.663877777777778, 1.663916666666666, 1.663955555555555, 1.665241666666667, 1.665263888888889, 1.665294444444444, 1.665713888888889, 1.66575, 1.665775, 1.667236111111111, 1.668508333333333, 1.67005, 1.671352777777778, 1.671558333333333, 1.671591666666667, 1.673816666666667, 1.673880555555555, 1.673908333333333, 1.674308333333333, 1.674347222222222, 1.674383333333333, 1.674397222222222, 1.674452777777778, 1.674497222222222, 1.675933333333333, 1.675944444444444, 1.675969444444444, 1.677819444444444, 1.677866666666667, 1.677911111111111, 1.677961111111111, 1.679808333333333, 1.679836111111111, 1.679852777777778, 1.681430555555555, 1.681480555555555, 1.681527777777778, 1.681572222222222, 1.681619444444444, 1.681669444444444, 1.682861111111111, 1.682891666666666, 1.682927777777777, 1.682952777777778, 1.682997222222222, 1.683011111111111, 1.683016666666667, 1.683055555555555, 1.683086111111111, 1.683119444444444, 1.683141666666667, 1.6838, 1.683847222222222, 1.683891666666667, 1.683938888888889, 1.683988888888889, 1.684041666666667, 1.690041666666667, 1.690505555555555, 1.690508333333333, 1.690513888888889, 1.690516666666667, 1.690522222222222, 1.690527777777778, 1.690533333333333, 1.690561111111111, 1.690722222222222, 1.690738888888889, 1.690763888888889, 1.690791666666667, 1.690825, 1.690863888888889, 1.692141666666667, 1.692013888888889, 1.692008333333334, 1.691836111111111, 1.691836111111111, 1.691841666666667, 1.691852777777778, 1.691869444444444, 1.691891666666667, 1.692519444444444, 1.692525, 1.692533333333333, 1.692536111111111, 1.692538888888889, 1.69255, 1.692572222222222, 1.692597222222223, 1.692613888888889, 1.692636111111111, 1.692652777777778, 1.692663888888889, 1.692875, 1.692930555555555, 1.693, 1.693002777777778, 1.693075, 1.698830555555556, 1.698911111111111, 1.698991666666667, 1.699022222222222, 1.699066666666667, 1.699858333333333, 1.699975, 1.700108333333333, 1.700325, 1.700883333333333]
#[0.503896, 0.505756, 0.508288, 0.510599, 0.512910, 0.515221, 0.517532, 0.519842, 0.522154, 0.524464, 0.528279]
rpl2_long = [101.5189472222222, 101.5189597222222, 101.519125, 101.5191313888889, 101.5191327777778, 101.5191111111111, 101.5190736111111, 101.5190730555556, 101.5189833333333, 101.5189083333333, 101.5188638888889, 101.519025, 101.519475, 101.5204222222222, 101.5204305555556, 101.5204416666667, 101.52044, 101.5204311111111, 101.5204222222222, 101.5199147222222, 101.5199125, 101.5199158333333, 101.5200480555555, 101.5200555555556, 101.5200583333333, 101.5201691666667, 101.5203308333333, 101.5207838888889, 101.5210163888889, 101.5210486111111, 101.5210527777778, 101.5212888888889, 101.5212916666667, 101.5212916666667, 101.5212694444444, 101.5212722222222, 101.5212805555555, 101.5212833333333, 101.5212972222222, 101.521305, 101.5214777777778, 101.5214797222222, 101.5214861111111, 101.5220425, 101.5220555555556, 101.5220619444444, 101.5220663888889, 101.5221555555556, 101.5221583333333, 101.5221627777778, 101.5225841666667, 101.5225952777778, 101.5226013888889, 101.5226038888889, 101.5226027777778, 101.5225972222222, 101.5224, 101.5223944444444, 101.5223888888889, 101.5223916666667, 101.5223972222222, 101.5223972222222, 101.5224, 101.5224083333333, 101.5224161111111, 101.5224333333333, 101.5224444444444, 101.5228516666667, 101.5228488888889, 101.5228675, 101.5228833333333, 101.5228916666667, 101.5228972222222, 101.5233194444444, 101.5235388888889, 101.5235388888889, 101.5235436111111, 101.5235491666667, 101.5235611111111, 101.5235777777778, 101.5235972222222, 101.5236722222222, 101.5241277777778, 101.5241663888889, 101.5242027777778, 101.5242333333333, 101.5242611111111, 101.5243, 101.5248725, 101.5254805555555, 101.5255055555556, 101.5270222222222, 101.5270638888889, 101.5271055555556, 101.5271444444444, 101.5271833333333, 101.5272166666667, 101.5280166666666, 101.528025, 101.5280361111111, 101.5280388888889, 101.5280416666667, 101.5280638888889, 101.5281041666667, 101.52815, 101.528175, 101.5282083333334, 101.5282333333333, 101.5282527777778, 101.5287972222222, 101.5289027777778, 101.529025, 101.5290294444444, 101.5291666666667, 101.5365111111111, 101.5366111111111, 101.5367094444444, 101.5367361111111, 101.5367722222222, 101.5374613888889, 101.5375611111111, 101.5376613888889, 101.5378133333333, 101.538275]
#[103.283846, 103.283380, 103.282697, 103.282072, 103.281447, 103.280822, 103.280200, 103.279575, 103.278950, 103.278326, 103.277294]

names2 = [str(i+1) for i in range(len(rpl2_long))]
colors2 = ["black"] * len(rpl2_long)

#names2 = ["Titik Joint Sokoi", "WP1", "WP2", "WP3", "WP4", "WP5", "WP6", "WP7", "WP8", "WP9", "WP10", "L2 WP11", "L2 WP12"]
#colors2 = ["red", "navy", "navy", "navy", "navy", "navy", "navy", "navy", "navy", "navy", "navy", "red", "red"]


points = [
    {"latitude": lat, "longitude": lon, "name": name, "color": color}
    for lat, lon, name, color in zip(rpl1_lat, rpl1_long, names, colors)
]

points2 = [
    {"latitude": lat, "longitude": lon, "name": name, "color": color}
    for lat, lon, name, color in zip(rpl2_lat, rpl2_long, names2, colors2)
]


R_EARTH = 6378137  # meter

def body_to_latlon(lat_o, lon_o, heading_deg, relative_points):

    psi = np.deg2rad(360 - heading_deg)
    R = np.array([
        [np.cos(psi), -np.sin(psi)],
        [np.sin(psi),  np.cos(psi)]
    ])
    lat_rad = np.deg2rad(lat_o)

    global_points = {}

    for name, p_body in relative_points.items():
        dx, dy = R @ p_body

        dlat = dy / R_EARTH
        dlon = dx / (R_EARTH * np.cos(lat_rad))

        lat_new = lat_o + np.rad2deg(dlat)
        lon_new = lon_o + np.rad2deg(dlon)

        global_points[name] = (lat_new, lon_new)

    return global_points
'''
 a > haluan kiri
 b > haluan
 c > haluan kanan
 d > buritan kanan
 e > burita kiri
 chute > posisi chute
'''
relative_points = {
    "a": np.array([0, 35]),
    "b": np.array([8, 40]),
    "c": np.array([16, 35]),
    "d": np.array([16, -10]),
    "e": np.array([0, -10]),
    "chute": np.array([8, -10]),
}

#lat_a = global_points[0]
lat_a =  0
long_a =  0


lat_b =  0
long_b =  0

lat_c =  0
long_c =  0

lat_d =  0
long_d =  0

lat_e =  0
long_e =  0

lat_chute = 0
long_chute = 0

rpl_long_calc = np.array(rpl1_long)
rpl_lat_calc = np.array(rpl1_lat)


################### GUI Variable ##################################
analog1_x = 0
analog1_y = 0
analog1_x_prev = 0
analog1_y_prev = 0

analog2_x = 0
analog2_y = 0
analog2_x_prev = 0
analog2_y_prev = 0

hat = ""
hat_prev = ""


up_color = "#122e55"
left_color = "#122e55"
right_color = "#122e55"
down_color = "#122e55"

button1_color = "#122e55"
button2_color = "#122e55"
button3_color = "#122e55"
button4_color = "#122e55"

button_L1_color = "#122e55"
button_L2_color = "#122e55"
button_R1_color = "#122e55"
button_R2_color = "#122e55"

analog1_color = "#122e55"
analog2_color = "#122e55"

analog1_angle = 0
control_direction = 0


control_direction_send = 0
control_direction_send1 = 0
control_direction_send2 = 0
control_direction_send3 = 0
control_direction_send4 = 0

####################################

#broker="123.45.0.10"
broker="127.0.0.1"
port = 1883

pubdelay = 2 #delay publish to all wind and engine box
counter = 0

thruster1_command = 0
thruster2_command = 0
thruster3_command = 0
thruster4_command = 0


thruster1_speed_target = 0
thruster2_speed_target = 0
thruster3_speed_target = 0
thruster4_speed_target = 0

thruster1_speed_sensor = 0
thruster2_speed_sensor = 0
thruster3_speed_sensor = 0
thruster4_speed_sensor = 0


aggresivity_time = 0
aggresivity_time_prev = 0
aggresivity_value = 1
max_aggresivity_value = 2


min_thruster = 0
max_thruster = 1000




S1 = 0
S2 = 0
S3 = 0
S4 = 0
EC1 = 0
EC1_time = 0
EC1_time_prev = time.time()

EC2 = 0
EC2_time = 0
EC2_time_prev = time.time()

EC3 = 0
EC3_time = 0
EC3_time_prev = time.time()

EC4 = 0
EC4_time = 0
EC4_time_prev = time.time()

str1 = 0
str2 = 0
str3 = 0
str4 = 0

str1_target = 0
str2_target = 0
str3_target = 0
str4_target = 0

str1_target_buffer = 0
str2_target_buffer = 0
str3_target_buffer = 0
str4_target_buffer = 0


SP1 = 0
SP2 = 0
SP3 = 0
SP4 = 0

rpm1 = 0
rpm2 = 0
rpm3 = 0
rpm4 = 0

target_rpm1 = 0
target_rpm2 = 0
target_rpm3 = 0
target_rpm4 = 0

target_lat =0
target_long = 0
error_long =0
error_lat = 0

distance = 0

Wspeed=0
Wdirect=0


latitude_integer = 1
latitude_fractional = 0.153461

longitude_integer = 103
longitude_fractional = 0.894775


lat_offset = 0
long_offset = 0

lat_slope = 0
long_slope = 0

slope = 0


val_latitude =  1.153461 #centre
filtered_val_latitude = val_latitude#centre
val_longitude = 103.894775   #centre
filtered_val_longitude = filtered_val_latitude  #centre

lat_front = 0
long_front = 0

latitude_prev = val_latitude
longitude_prev = val_longitude

latitude_target = -0.33026899613145305
longitude_target = 104.60042691242732

speed_measurement_time = 0
speed_measurement_time_prev = 0

latitude = ""
longitude = ""

heading = 0
heading_magneto = 0
heading_dual_gps = 0
heading_method = "magneto"

heading_error = 0
heading_prev = 0
heading_speed = 0
heading_target = 180

get_lat_GUI = 0
get_lon_GUI = 0
get_lat_GUI1 = 0
get_lon_GUI1 = 0
get_lat_GUI_last = 0
get_lon_GUI_last = 0
counter_distance_mea = 0
dst_bw_line = 0

station_keeping_state = "off"
station_keeping_state_prev = "off"
autopilot_state = 0

delta_lat = 0
delta_lat = 0

message_time = 0
message_time_prev = 0

mqtt_transmit_time = 0
mqtt_transmit_time_prev = 0

day = 0
day_prev = 0

current_time = dt.datetime.now()

aggresivity_coefficient = 0

minval = 0
thruster_mode = ""

payout= 0
water_depth = 0

position_error = 0
position_error_dot = 0
position_error_prev = 0


dir_error = 0
dir_error_earth_fixed = 0

control_style = "individual"
control_style_prev = ""

filtered_psi_error = 0

utm_lat_lon_wp = ""

x = 0
y = 0

x_input = 0
y_input = 0

x_error = 0
y_error = 0

psi_error = 0
psi_input = 0

spc_message_time = 0
spc_message_time_prev = 0

gyro_message_time = 0
gyro_message_time_prev = 0

spc_indicator_color1 = "red"
spc_indicator_color2 = "red"
spc_indicator_color3 = "red"
spc_indicator_color4 = "red"


throttle_indicator_color1 = "#F28705"
throttle_indicator_color2 = "#F28705"
throttle_indicator_color3 = "#F28705"
throttle_indicator_color4 = "#F28705"

speed_ship = 0

gps_time = 0
gps_time_prev = 0

front_gps_time = 0
front_gps_time_prev = 0

front_gps_color = "red"





gps_type = 0

cog = 0


latitude_aux = 0
longitude_aux = 0

gps_aux_time = 0
gps_aux_time_prev = 0

gps_status_color = "red"

track_time = 0
track_time_prev = 0

flow_lpm = 0
flow_lpm2 = 0

time_loop = 0
time_loop_prev = 0

latitude_dms = ""
longitude_dms = ""

lat_pole = "S"
long_pole = "E"

rpl_lat = []
rpl_long = []

#rpl_lat = ['-7.745436', '-7.745402', '-7.745064', '-7.744931', '-7.744583', '-7.744312', '-7.74377', '-7.743055']
#rpl_long = ['108.99344', '108.993896', '108.994878', '108.995411', '108.996321', '108.996879', '108.997866', '108.998837']

direction_degree = 0

pitch = 0
roll = 0

csv_file = ""

ly1 = 10
lx1 = 25
ly2 = -20
lx2 = 25
ly3 = -20
lx3 = -25
ly4 = 10
lx4 = -25

transformation_allocation = [[1,0,1,0,1,0,1,0],
                            [0,1,0,1,0,1,0,1],
                            [-ly1, lx1, -ly2, lx2, -ly3, lx3, -ly4, lx4]]

target_distance = 0
target_degree = 0

y_est = 0

user_control = "manual"

mqtt_message_time = 0
mqtt_message_time_prev = 0

csv_message_time = 0
csv_message_time_prev = 0

navigation = "a"
propeller_speed = 0
propeller_speed1 = 0
propeller_speed2 = 0
propeller_speed3 = 0
propeller_speed4 = 0

propeller_speed1_buffer = 0
propeller_speed2_buffer = 0
propeller_speed3_buffer = 0
propeller_speed4_buffer = 0

steering1_color = "#00ff00"
steering2_color = "#00ff00"
steering3_color = "#00ff00"
steering4_color = "#00ff00"


steering1_sensor = 0
steering2_sensor = 0
steering3_sensor = 0
steering4_sensor = 0


heading_first = ""

speed_button = 0

propeller_mode = 0 
propeller_mode_prev = 0

propeller_switch = 0

direction_angle = 0

navigation_mode = 0
navigation_mode_text = "forward"

drive_mode = "normal"
drive_mode_count = 0

analog_lock = 0
analog_lock_prev = 0

power = 0
power_set = 0

heading_target_status = 0


select1 = 0
select2 = 0
select3 = 0
select4 = False


central_status = "local"

sway_dir = "left"

zone = 1

radius_zone = 1
radius_zone_prev = 1

joystick1_status = "off"
joystick2_status = "off"
joystick2_time = time.time()
joystick2_time_prev = 0
joystick_mode = 0


##################################### Ship Modelling Variable ##############################
psi = 0
psi_prev = 0
n_dot = 0
e_dot = 0
psi_dot = 0
x_dot = 0
y_dot = 0

j_theta = np.array([[0,0,0],[0,0,0],[0,0,0]])
v = np.array([[0],[0],[0]])
n_error = 0
e_error = 0
error_body_fixed = np.array([[0],[0],[0]])


############ Model Kinetik ################################
print("==== Kinetik =======")



xg = 0.5 #posisi x center of gravity
yg = 0.4 #posisi y center of gravity
mass = 1000 #massa kapal
r = 0 #posisi arah surge / kecepatan sudut (psi_dot)
Iz = 0 #momen inersia akibat percepatan sumbu y

x_u = 0.9
y_v = 0.6
n_r = 0.3
y_r = 0.1
n_v = 0.2

x_udot = 0.9
y_vdot = 0.6
y_rdot = 0.7
n_vdot = 0.3
n_rdot = 0.4
u = 0
v = 0
r = 0

j_theta = np.array([[0,0,0],[0,0,0],[0,0,0]])
v = np.array([[0],[0],[0]])
n_error = 0
e_error = 0
error_body_fixed = np.array([[0],[0],[0]])

x_error = 0
y_error = 0


ship_radius_zone = 3
#gaya akibat massa



#dari Thomas P. DeRensis
m = np.array([[mass, -0, 0], [0.0, mass, mass*xg], [-0.00, mass*xg, Iz]])
+ np.array([[-x_udot,-0.00,0.00],[-0.00,y_vdot,y_rdot],[-0.00,n_vdot,n_rdot]])
print(m)



#gaya akibat coriolis
c = np.array([ [0, 0, -mass * (xg*r + float(y_dot))],
               [0, 0, -mass * (yg*r + float(x_dot))],
               [-mass * (xg*r + float(y_dot)),-mass * (yg*r + float(x_dot)), 0]]) + np.array([[0,0,-y_vdot*float(y_dot) - ((y_rdot+n_vdot)/2)*r],
            [0,0,x_udot*float(x_dot)],
            [-y_vdot*float(y_dot) - ((y_rdot+n_vdot)/2)*r,x_udot*float(x_dot),0]])

#gaya akibat drag
d = np.array([[x_u,-0.00,-0.00],
    [-0.00,y_v,y_r],
    [-0.00,n_v,n_r]]) 

print("d",d)


A = np.block([
    [np.zeros((3, 3)), np.eye(3)],
    [np.zeros((3, 3)), -np.linalg.inv(m) @ d]
])

B = np.block([
    [np.zeros((3, 3))],
    [np.linalg.inv(m)]
])
C = np.block([
    [np.eye(3), np.zeros((3, 3))]
])
D = np.zeros((3, 3))


x_next = np.array([[0], [0], [0], [0], [0], [0]])
 

x = np.array([[0], [0], [0], [0], [0], [0]]) 
u_optimal = np.array([[0], [0], [0]])
y = np.array([[0], [0.0], [0]])

print("Continous state space : ")
print("A")
print(str(A))

print("B")
print(B)

print("C")
print(C)


print("D")
print(D)

# Mendiskretisasi matriks A dan B
# Matriks identitas
I = np.eye(A.shape[0])
T = 1

# Menghitung Ad dan Bd dengan Tustin
A = np.linalg.inv(I - (T/2) * A) @ (I + (T/2) * A)
B = np.linalg.inv(I - (T/2) * A) @ (T * B)

# Cd dan Dd tetap sama
C = C
D = D


print("Discrete state space : ")
print("A")
print(str(A))

print("B")
print(B)

print("C")
print(C)


print("D")
print(D)


y_ref = np.array([x_error, y_error, heading]).reshape(-1, 1)

# Menyimpan matriks dalam bentuk dictionary
try:
    state_space = {
        "A_discrete": A.tolist(),
        "B_discrete": B.tolist(),
        "C_discrete": C.tolist(),
        "D_discrete": D.tolist(),
        "y_ref" : y_ref.tolist(),
        "lat" : val_latitude,
        "long" : val_longitude,
        "lat_target": rpl_lat[0],
        "lon_target":rpl_long[0]
    }

except:
    state_space = {
        "A_discrete": A.tolist(),
        "B_discrete": B.tolist(),
        "C_discrete": C.tolist(),
        "D_discrete": D.tolist(),
        "y_ref" : y_ref.tolist(),
        "lat" : val_latitude,
        "long" : val_longitude,
        "lat_target": val_latitude,
        "lon_target": val_longitude
    }

fsm_scheme = "scheme1"

est = 0

# Menyimpan ke dalam file JSON
file_path = 'state_space.json'
with open(file_path, 'w') as f:
    json.dump(state_space, f)
    

print(f"File JSON disimpan di: {file_path}")

x_gain = np.array([[5,5,5,5,5,5,5,5,5]])
y_gain = np.array([[5,5,5,5,5,5,5,5,5]])
yaw_positive_gain = np.array([[5,5,5,5,5,5,5,5,5]])
yaw_negative_gain = np.array([[5,5,5,5,5,5,5,5,5]])



try:
    with open("fsm_gain.json", 'r') as file:
        data = json.load(file)

    # Mengonversi data JSON menjadi variabel
    x_gain = data.get("x_gain", 0)
    y_gain = data.get("y_gain", 0)
    yaw_positive_gain = data.get("yaw_positive_gain", 0)
    yaw_negative_gain = data.get("yaw_negative_gain", 0)


    print(x_gain[0][1])
    print(y_gain)
    print(yaw_positive_gain)
    print(yaw_negative_gain)

except:
    print("membuat file fsm_gain.json")
    #lat_gain = np.array([[1,2,3,4,5,6,7,8,9]]])
    #long_gain = np.array([[1,2,3,4,5,6,7,8,9]]])
    #yaw_positive_gain = np.array([[1,2,3,4,5,6,7,8,9]]])
    #yaw_negative_gain = np.array([[1,2,3,4,5,6,7,8,9]]])



    fsm_gain = {
        "x_gain": x_gain.tolist(),
        "y_gain": y_gain.tolist(),
        "yaw_positive_gain": yaw_positive_gain.tolist(),
        "yaw_negative_gain": yaw_negative_gain.tolist()
    }


    with open("fsm_gain.json", 'w') as f:
        json.dump(fsm_gain, f)
        

    print(f"File JSON disimpan di: {file_path}")



scontrol_prop = ""
waktu = dt.datetime.now()
filename = str("DP Experimental RECORD " ) + str(current_time.day)+str("-")+str(current_time.month)+str("-")+str(current_time.year) + str(".csv")
with open(filename, 'a') as csvfile:
    csvwriter = csv.writer(csvfile)
    rows = [ [str("date"),str("val latitude"), str("val longitude"), str("propeller speed1"), str("propeller speed2"), str("propeller speed3"), str("propeller speed4"), str("str1 target"), str("str2 target"), str("str3 target"), str("str4 target"), str("heading")
              ,str("heading target"),str("mode"), str("position_error"), str("dir_error"), str("payout"), str("lat chute"),str("long chute") ]]
    csvwriter.writerows(rows)


previous_values = {'lat_index': None, 'y': None}


lat_index = 0
#prev_val('x', x)
def prev_val(var_name, input_val):
    global previous_values
    if previous_values[var_name] is None:  # If it's the first time the function is called for this variable
        result = 0
    else:
        result = 1 if input_val == previous_values[var_name] else 0
    previous_values[var_name] = input_val
    return result




def shortest_psi(psi_ref, psi_d):
    psi_temp = (psi_ref-psi_d)%360
    psi_shortest = (psi_temp + 360) *-1 %360 
    if (psi_shortest > 180):
        psi_shortest = psi_shortest - 360
    return psi_shortest   


def decimal_to_dms(decimal):
    degrees = int(decimal)
    minutes_float = abs((decimal - degrees)) * 60
    minutes = int(minutes_float)
    seconds = abs((minutes_float - minutes) * 60)

    return (str(str(abs(degrees))+ str("°") + str(minutes) + ("'") + str(round(seconds,2))+ str("\"")))


def meter_conversion(lat1, long1, lat2, long2):
    delta_lat = (lat1 - lat2)*111000
    delta_lon = (long1 - long2)*111000
    distance = sqrt(pow(delta_lat, 2) +  pow(delta_lon, 2))
    return distance

def map_angle_conversion(lat1, long1, lat2, long2):
    delta_lat = (lat1 - lat2)*111000
    delta_lon = (long1 - long2)*111000
    map_angle_conversion = math.atan2(float(delta_lon),float(delta_lat)) * (180/math.pi)
    return map_angle_conversion


def degree_conversion(x,y):
    degree = math.atan2(float(y),float(x)) * (180/math.pi)
    return degree

def length_conversion(x,y):
    length = abs(x**2 + y **2)
    return length


def rotation(x, y, theta):
    j_theta = np.array([[np.cos(theta * float(np.pi/180)), -np.sin(theta * float(np.pi/180)), 0],
              [np.sin(theta * float(np.pi/180)), np.cos(theta* float(np.pi/180)), 0],
              [0, 0, 1]])
    result = ((j_theta)@ np.array([[x],[y],[theta]]))
    
    x_accent = result[1]
    y_accent = result[0]

    return x_accent, y_accent



def polynomial_linearization(input, a1, a2, a3, a4):
    result = a1*(input**3) + a2*(input**2) + a3*(input) + a4
    return result


def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min



def sgn(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0
    
def integral(x, x_integral, dt, reset):
    if (reset == 1):
        try:
            x_integral = (x + x_integral)/dt
        except:
            pass
            
    else:
        x_integral = 0
    
    return x_integral

def constrain(x, min, max):
    if (x > max):
        x = max
    if (x < min):
        x = min
    return x



def integral_correction(heading_error, gain, prev_val,steering, zero):
    if zero == 1:
        if (abs(steering < 90)):
            result = (gain*heading_error) - prev_val
        else:
            result = (gain*heading_error) + prev_val

    if zero == 0:
        result = prev_val
    return result



def map_angle_with_offset(value, from_low, from_high, to_low, to_high, offset):
    mapped_value = (value - from_low) * (to_high - to_low) / (from_high - from_low) + to_low
    return (mapped_value + offset) % 360



def dual_gps_heading(lat1, lon1, lat2, lon2):
    # Konversi ke radian
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlon = lon2 - lon1

    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)

    theta = math.atan2(x, y)  # hasil radian

    # Konversi ke derajat
    bearing_deg = math.degrees(theta)

    # Normalisasi 0–360°
    bearing_deg = (bearing_deg + 360) % 360

    return round(bearing_deg, 2)


########## mengisi class table dengan instruksi pyqt5#############
#----------------------------------------------------------------#

global_points = body_to_latlon(val_latitude , val_longitude, heading_magneto, relative_points)


# ── Background worker: runs tick() logic in a separate thread ─────────────────
# This is the KEY fix: main.py does ZERO work on the Qt main thread after
# startup. dps.py was running heavy numpy math, json.dump, csv writes, and
# MQTT publishes inside a @pyqtSlot called by QML's 100ms timer — all on the
# main thread, blocking every frame.  Moving it here frees the render loop.
class BackgroundWorker(QObject):
    def __init__(self, backend_ref):
        super().__init__()
        self.backend = backend_ref
        self._running = True

    @pyqtSlot()
    def run(self):
        while self._running:
            try:
                self.backend._do_tick()
            except Exception as e:
                print("Worker tick error:", e)
            # 100 ms between ticks — same cadence as the old QML timer
            QThread.msleep(100)

    def stop(self):
        self._running = False


class table(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = QApplication(sys.argv)
        self.engine = QQmlApplicationEngine(self)

        # Load sonar data (fast tuples, not dicts)
        self.depth_data = load_depth_points_from_isobath(isobath_file)
        print("✅ Titik sonar terload:", len(self.depth_data))

        polygons = load_polygons()
        self.engine.rootContext().setContextProperty("allPolygons", polygons)
        self.engine.rootContext().setContextProperty("backend", self)
        self.engine.load(QUrl("dps.qml"))

        # Start background worker thread
        self._worker_thread = QThread()
        self._worker = BackgroundWorker(self)
        self._worker.moveToThread(self._worker_thread)
        self._worker_thread.started.connect(self._worker.run)
        self._worker_thread.start()

        sys.exit(self.app.exec_())


    
    @pyqtSlot(result='QVariantList')
    def point_a(self):
        lat_a, long_a = global_points["a"]
        return [float(lat_a), float(long_a)]
    
    @pyqtSlot(result='QVariantList')
    def point_b(self):
        lat_b, long_b = global_points["b"]
        return [float(lat_b), float(long_b)]
    
    
    @pyqtSlot(result='QVariantList')
    def point_c(self):
        lat_c, long_c = global_points["c"]
        return [float(lat_c), float(long_c)]
    
    
    @pyqtSlot(result='QVariantList')
    def point_d(self):
        lat_d, long_d = global_points["d"]
        return [float(lat_d), float(long_d)]
            
    
    @pyqtSlot(result='QVariantList')
    def point_e(self):
        lat_e, long_e = global_points["e"]
        return [float(lat_e), float(long_e)]
    
    
    @pyqtSlot(result='QVariantList')
    def point_chute(self):
        lat_chute, long_chute = global_points["chute"]
        return [float(lat_chute), float(long_chute)]
        
    
    @pyqtSlot(result=str)
    def payout_value(self):  return str(round(payout,0))
      

    @pyqtSlot(result=float)
    def Set_Speed1(self):  return round(propeller_speed1_buffer,0)
            
    @pyqtSlot(result=float)
    def Set_Speed2(self):  return round(propeller_speed2_buffer,0)

    @pyqtSlot(result=float)
    def Set_Speed3(self):  return round(propeller_speed3_buffer,0)

    @pyqtSlot(result=float)
    def Set_Speed4(self):  return round(propeller_speed4_buffer,0)

    @pyqtSlot(result=float)
    def engineconect1(self):  return EC1

    @pyqtSlot(result=float)
    def engineconect2(self):  return EC2

    @pyqtSlot(result=float)
    def engineconect3(self):  return EC3

    @pyqtSlot(result=float)
    def engineconect4(self):  return EC4
    
   
    @pyqtSlot(result=float)
    def rpm1(self):  return rpm1
    
    @pyqtSlot(result=float)
    def rpm2(self):  return rpm2
    
    @pyqtSlot(result=float)
    def rpm3(self):  return rpm3
    
    @pyqtSlot(result=float)
    def rpm4(self):  return rpm4
    
    
    @pyqtSlot(result=str)
    def slope(self):  return str(round(slope,2))
    
    
    @pyqtSlot(result=float)
    def target_rpm1(self):  return target_rpm1
    
    @pyqtSlot(result=float)
    def target_rpm2(self):  return target_rpm2
    
    @pyqtSlot(result=float)
    def target_rpm3(self):  return target_rpm3
    
    @pyqtSlot(result=float)
    def target_rpm4(self):  return target_rpm4
    

    @pyqtSlot(result=float)
    def steering1(self):  return steering1_sensor

    @pyqtSlot(result=float)
    def steering2(self):  return steering2_sensor

    @pyqtSlot(result=float)
    def steering3(self):  return steering3_sensor

    @pyqtSlot(result=float)
    def steering4(self):  return steering4_sensor

    @pyqtSlot(result=float)
    def power(self):  return power

    
    @pyqtSlot(result=float)
    def steering1_target(self):  return round(str1_target_buffer,0)

    @pyqtSlot(result=float)
    def steering2_target(self):  return round(str2_target_buffer,0)

    @pyqtSlot(result=float)
    def steering3_target(self):  return round(str3_target_buffer,0)

    @pyqtSlot(result=float)
    def steering4_target(self):  return round(str4_target_buffer,0)
    
    
    @pyqtSlot(result=list)
    def points(self):  return points
    
    @pyqtSlot(result=list)
    def points2(self):  return points2


    @pyqtSlot(result=str)
    def est(self):  return str(est)
    
    @pyqtSlot(str)
    def heading_method_setting(self, method):
        global heading_method
        heading_method = method
        #print(heading_method)
    
    @pyqtSlot(float)
    def estimate_rpl(self, line):
        global y_est
        global rpl_long_calc
        global rpl_lat_calc
        
        global rpl_lat
        global rpl_long
        
        global lat_chute
        global long_chute
        #rpl_lat = []
        #rpl_long = []
        
        print(rpl1_lat)
        if (line == 1):
            rpl_lat_calc = rpl1_lat
            rpl_long_calc = rpl1_long
            
        if (line == 2):
            rpl_lat_calc = rpl2_lat
            rpl_long_calc = rpl2_long
        
        
        theta_deg = 360 - (heading + 90)  # ke atas

        x = np.array(rpl_long_calc)
        y = np.array(rpl_lat_calc)
        # === TITIK ASAL RAY DAN ARAHNYA ===
        P = np.array([val_longitude, val_latitude])

        num_lines = len(x) - 1
        print("num lines", num_lines)
        for i in range(num_lines):
            A = np.array([x[i], y[i]])
            B = np.array([x[i + 1], y[i + 1]])
            A_offset = A - P
            B_offset = B - P

            #plt.plot([A_offset[0], B_offset[0]], [A_offset[1], B_offset[1]], 'k-', label=f"Garis {i+1}" if i == 0 else "")

            intersection = find_intersection_theta(A, B, P, theta_deg - 90)
            if intersection is not None:
                intersection_points.append(intersection)
                lines_with_intersection.append(i + 1)
                inter_offset = intersection - P
                #plt.plot(inter_offset[0], inter_offset[1], 'ro', label=f"Titik potong Garis {i+1}")
                print(f"Titik potong (Garis {i+1}):", intersection)
                print("kiri")
                print(intersection[1], intersection[0])
                
                if (len(rpl_lat) <1):
                    rpl_lat.append(float(intersection[1]))
                    rpl_long.append(float(intersection[0]))
                
                else :
                    rpl_lat[0] = float(intersection[1])
                    rpl_long[0] = float(intersection[0])
                
                #print(P[1], P[0])
                distance = meter_conversion(intersection[1], intersection[0], P[1], P[0])
                print(intersection[1], intersection[0])
            
            intersection = find_intersection_theta(A, B, P, theta_deg + 90)
            if intersection is not None:
                intersection_points.append(intersection)
                lines_with_intersection.append(i + 1)
                inter_offset = intersection - P
                #plt.plot(inter_offset[0], inter_offset[1], 'ro', label=f"Titik potong Garis {i+1}")
                print(f"Titik potong (Garis {i+1}):", intersection[0], intersection[1])
                print("kanan")
                
                #rpl_lat[0] = P[1]
                #rpl_lon[1] = P[0]
                
                if (len(rpl_lat) <1):
                    rpl_lat.append(float(intersection[1]))
                    rpl_long.append(float(intersection[0]))
                
                else :
                    rpl_lat[0] = float(intersection[1])
                    rpl_long[0] = float(intersection[0])
                
                
                
                distance = meter_conversion(float(intersection[1]), float(intersection[0]), float(P[1]), float(P[0]))
                #print(distance)
                #print(intersection[1])
                #print(rpl_long)
        
        
        
        #return y_est
    
    @pyqtSlot(float, float, result=float)
    def estimate_depth(self, lat, lon):
        global est
        nearest = find_two_nearest_points(lat, lon, self.depth_data)
        if nearest is None:
            return -1.0
        est = round(idw_from_two_points(lat, lon, nearest[0], nearest[1]), 2)
        return est
    
    
    @pyqtSlot(float, float, result=float)
    def calculate_slope(self, lat, lon):
        global slope
        
        slope_radius = 30
        
        lat_slope = slope_radius/111000 * np.cos(heading * np.pi/180)
        long_slope = slope_radius/111000 * np.sin(heading * np.pi/180)
        
        nearest = find_two_nearest_points(lat+ lat_slope, lon+ long_slope, self.depth_data)
        
        if nearest is None:
            return -1.0  # ➤ kode khusus untuk 'no data'
        
        
        depth_slope = round(idw_from_two_points((lat + lat_slope), (lon + long_slope), nearest[0], nearest[1]) ,2)
        
        
        
        
        slope = np.degrees(np.arctan2((est - depth_slope), slope_radius))
        
        #print(lat, lon, lat + lat_slope, lon + long_slope)
        #print(est ,depth_slope)
        #print(slope)
        
        return slope
    

    

    @pyqtSlot(result=float)
    def spc1(self):  return thruster1_command

    @pyqtSlot(result=float)
    def spc2(self):  return thruster2_command

    @pyqtSlot(result=float)
    def spc3(self):  return thruster3_command

    @pyqtSlot(result=float)
    def spc4(self):  return thruster4_command

    @pyqtSlot(result=float)
    def lat(self):  return round(val_latitude,9)

    @pyqtSlot(result=float)
    def long(self):  return round(val_longitude,9)

    @pyqtSlot(result=float)
    def headingship(self):  return heading

    @pyqtSlot(result=float)
    def winddirect(self):  return Wdirect

    @pyqtSlot(result=float)
    def windspeed(self):  return (Wspeed)

    @pyqtSlot(result = float)
    def position_error(self): return round(position_error,2)
    
    @pyqtSlot(result = float)
    def dir_error(self): return round(dir_error, 0)

    @pyqtSlot(result=float)
    def lat_target(self):  return target_lat

    @pyqtSlot(result=float)
    def long_target(self):  return target_long

    @pyqtSlot(result=float)
    def long_error(self):  return error_long  

    @pyqtSlot(result=float)
    def lat_error(self):  return error_lat
    

    @pyqtSlot(result=float)
    def orifice1_val(self):  return thruster1_speed_sensor

    @pyqtSlot(result=float)
    def orifice2_val(self):  return thruster2_speed_sensor

    @pyqtSlot(result=float)
    def orifice3_val(self):  return thruster3_speed_sensor

    @pyqtSlot(result=float)
    def orifice4_val(self):  return thruster4_speed_sensor
    
    @pyqtSlot(result=str)
    def line_length(self): return str(int(distance))
    

    @pyqtSlot(result=str)
    def pitch(self): return str(int(pitch))
    

    @pyqtSlot(result=str)
    def roll(self): return str(int(roll))
    
    
    @pyqtSlot(result = int)
    def heading_error(self): return heading_error
    
    
    @pyqtSlot(result=str)
    def throttle_indicator_color1(self): return throttle_indicator_color1

    @pyqtSlot(result=str)
    def throttle_indicator_color2(self): return throttle_indicator_color2
    
    @pyqtSlot(result=str)
    def throttle_indicator_color3(self): return throttle_indicator_color3

    @pyqtSlot(result=str)
    def throttle_indicator_color4(self): return throttle_indicator_color4
    

    #spc_indicator_color1
    @pyqtSlot(result=str)
    def spc_indicator_color1(self): return spc_indicator_color1

    @pyqtSlot(result=str)
    def spc_indicator_color2(self): return spc_indicator_color2
    
    @pyqtSlot(result=str)
    def spc_indicator_color3(self): return spc_indicator_color3

    @pyqtSlot(result=str)
    def spc_indicator_color4(self): return spc_indicator_color4
    



    @pyqtSlot(result=str)
    def navigation_mode(self): return navigation_mode_text
    
    @pyqtSlot(result=str)
    def control_style(self): return control_style

    @pyqtSlot(result=int)
    def radius_zone(self): return radius_zone
    
        
    @pyqtSlot(str)
    def payout_reset (self, command):
        print(command)
        if (command == "zero"):
            client.publish("tension_reset", "1")
            
        if (command == "reset"):    
            client.publish("reset_payout", "1")
    
    
    @pyqtSlot(float)
    def line_reset(self, msg):
        global distance
        distance = msg
    

    @pyqtSlot(float)
    def get_lat (self, lat_GUI):
        global get_lat_GUI
        get_lat_GUI = float(lat_GUI)
        print("Lat = ", get_lat_GUI)

    @pyqtSlot(float)
    def get_lon (self, lon_GUI):
        global get_lon_GUI
        get_lon_GUI = float(lon_GUI)
        print("Lon = ", get_lon_GUI)


    
        
    @pyqtSlot(float)
    def payout(self, get_distance_G):
        global payout
        if (get_distance_G == ""):
            get_distance_G = 0
        payout= int(get_distance_G)
        #print(distance_G)
        
    @pyqtSlot(float)
    def water_depth (self, get_water_depth):
        if (get_water_depth == ""):
            get_water_depth = 0
        global water_depth
        water_depth = int(get_water_depth)
        #print(water_depth)
    
    @pyqtSlot(str)
    def folder_read (self, value):
        global csv_file
        #csv_file = value
        csv_file = str(value).replace(r"\\", '/').replace(r"\"", '/').replace(r"file:///", "")
        print(csv_file)
        
        try:
            # Buka file CSV
            with open(str(csv_file), mode='r') as file:
                # Membuat objek pembaca CSV
                csv_reader = csv.reader(file)
                
                # Loop melalui setiap baris dalam file CSV
                for row in csv_reader:
                    # Tampilkan baris
                    print(row, row[0],row[1])
                    rpl_lat.append(row[0])
                    rpl_long.append(row[1])

        except FileNotFoundError:
            print("File tidak ditemukan. Pastikan path file benar.")
        except Exception as e:
            print("Terjadi kesalahan saat membaca file:", e)
            
    @pyqtSlot(result = float)
    def speed_ship(self):return round(speed_ship,2)
    
    @pyqtSlot(result = str)
    def central_status(self):return (central_status)
    
    
    
    @pyqtSlot(result = float)
    def heading_speed(self):return round(heading_speed,2)
    
    
    @pyqtSlot(result=str)
    def gps_status_color(self):return gps_status_color
    
    @pyqtSlot(result=str)
    def latitude_dms(self):return latitude_dms
    
    @pyqtSlot(result=str)
    def longitude_dms(self):return longitude_dms

    @pyqtSlot(result=str)
    def lat_pole(self):return lat_pole

    @pyqtSlot(result=str)
    def long_pole(self):return long_pole

    @pyqtSlot(result=str)
    def longitude_dms(self):return longitude_dms

    @pyqtSlot(result=str)
    def latitude_target(self):return str(latitude_target)

    @pyqtSlot(result=str)
    def longitude_target(self):return str(longitude_target)
    
    @pyqtSlot(result=str)
    def direction_degree(self):return str(direction_degree)

    
    @pyqtSlot(result=str)
    def drive_mode(self):return drive_mode
    
    @pyqtSlot(result=str)
    def zone(self):return str(zone)


    @pyqtSlot(result=list)
    def rpl_lat(self):return rpl_lat


    @pyqtSlot(result=list)
    def rpl_long(self):return rpl_long


    @pyqtSlot(int)
    def heading_target_slot(self, value):
        global heading_target
        heading_target = value
        print(heading_target)

    @pyqtSlot(result=str)
    def control_prop(self):return control_prop


    @pyqtSlot(result=str)
    def joystick1_status(self):return joystick1_status
    

    @pyqtSlot(result=str)
    def joystick2_status(self):return joystick2_status
    
    
    @pyqtSlot(result = str)
    def front_gps_color(self):return front_gps_color
    
    
    @pyqtSlot(result = str)
    def cog(self):return str(cog)
    
    
    @pyqtSlot(result=str)
    def lat_front(self):return str(lat_front)
    
    @pyqtSlot(result=str)
    def long_front(self):return str(long_front)
    

    @pyqtSlot(str)
    def fsm_scheme(self, value):
        global fsm_scheme
        fsm_scheme = value
    

    @pyqtSlot('QString')
    def heading_first(self, value):
        global heading_first
        heading_first = value
        print(heading_first)
    
    
    @pyqtSlot('QString')
    def thrusterMode(self, value):
        global thruster_mode        
        thruster_mode =str(value)
        #print(thruster_mode)
        
        
    @pyqtSlot('QString')
    def user_control(self, value):
        global user_control
        user_control = value
        print(user_control)

    

    @pyqtSlot('int')
    def joystick_mode(self, value):
        global joystick_mode
        global propeller_switch

        joystick_mode = value
        if (joystick_mode == 2):
            propeller_switch = 1
        #print(joystick_mode)
        
    
        
        
    @pyqtSlot("QString",'QString', 'QString')
    def station_keeping(self,status, val1, val2):
        global rpl_lat
        global rpl_long
        global station_keeping_state
        #print(status)
        station_keeping_state = status
        if (station_keeping_state == "off"):
            print("remove station")
            rpl_lat = rpl_lat[1:]
            rpl_long = rpl_long[1:]
        
        if(station_keeping_state == "on"):
            rpl_lat.insert(0, float(val1))
            rpl_long.insert(0, float(val2))



    @pyqtSlot('QString', 'QString')
    def target_destination(self, value1, value2):
        global latitude_target
        global longitude_target
        global rpl_lat
        global rpl_long
        print("change point") 
        rpl_lat.append(round(float(val_latitude),6))
        rpl_long.append(round(float(val_longitude), 6))
        print(latitude_target, longitude_target)
    
    @pyqtSlot(str)
    def remove(self, message):
        global clear_mode
        global rpl_lat
        global rpl_long
        clear_mode = message
        if (clear_mode == "front"):
            if (len(rpl_lat)>0):
                rpl_lat.pop()
                rpl_long.pop()

        if (clear_mode == "back"):
            try:
                rpl_lat = rpl_lat[1:]
                rpl_long = rpl_long[1:]
            except:
                pass
    
    @pyqtSlot('QString')
    def clear_rpl(self, value1):
        global rpl_lat
        global rpl_long
        rpl_lat.clear()
        rpl_long.clear()
        print("station keeping end")

    @pyqtSlot('QString', 'QString')
    def rpl_point(self, value1, value2):
        global rpl_lat
        global rpl_long
        global heading_target

        rpl_lat.append(str(round(float(value1), 6)))
        rpl_long.append(str(round(float(value2), 6)))
        print(rpl_lat)
        print(rpl_long)
        

        if (heading_first == "yes"):
            try:
                heading_target = int(shortest_psi(heading, map_angle_conversion(float(rpl_lat[0]), float(rpl_long[0]), val_latitude, val_longitude)))
                
            except:
                heading_target = 0

            print(f"heading target = {heading_target}")
        
         

    @pyqtSlot('QString')
    def autopilot(self, value):
        global autopilot_state
        autopilot_state = value
        #print(autopilot_state)
        

    @pyqtSlot(str)
    def tracking(self, value):
        global track_time
        global track_time_prev
        
        track_time = time.time() - track_time_prev
        if (track_time > 20):
            print(value)
            track_time_prev = time.time()
            waktu = dt.datetime.now()
            filename = str("TRACK RECORD " ) + str(current_time.day)+str("-")+str(current_time.month)+str("-")+str(current_time.year) + str(".csv")
            with open(filename, 'a') as csvfile:
                csvwriter = csv.writer(csvfile)
                rows = [ [str(str(waktu.hour) + str(":") + str(waktu.minute)+ str(":") + str(waktu.second)),str(val_latitude),
                          str(val_longitude), str(payout), str(lat_chute), str(long_chute)]]                
                csvwriter.writerows(rows)



#----------------------------------------------------------------#
    @pyqtSlot(str)
    def tick(self, value):
        # No-op: tick logic now runs in BackgroundWorker thread.
        # QML still calls this from its timer — that's fine, it returns instantly.
        pass

    def _do_tick(self):
        global heading_target
        global gps_time
        global gps_time_prev
        
        global gps_type
        
        global gps_aux_time
        global gps_aux_time_prev
        
        global gps_status_color

        global spc_message_time
        global spc_message_time_prev
        
        global gyro_message_time
        global gyro_message_time_prev

        global str1_target
        global str2_target
        global str3_target
        global str4_target

        global str1_target_buffer
        global str2_target_buffer
        global str3_target_buffer
        global str4_target_buffer

        global S1
        global S2
        global S3
        global S4

        global psi_error
        global spc_message_time
        
        global latitude_prev
        global longitude_prev
        
        global speed_measurement_time
        global speed_measurement_time_prev

        global speed_ship
        
        global gps_time
        global gps_time_prev
        global gps_status_color
        
        global val_latitude
        global val_longitude

        global latitude_target
        global longitude_target

        global thruster1_command
        global thruster2_command
        global thruster3_command
        global thruster4_command
        global position_error
        global position_error_prev
        global position_error_dot

        global dir_error
        global dir_error_earth_fixed
        global heading_error
        global filtered_psi_error

        global psi_input
        global utm_lat_lon_wp
        global x
        global y
        # NOTE: 'global time' removed — do not shadow the time module
        
        global target_rpm1
        global target_rpm2
        global target_rpm3
        global target_rpm4
        
        global rpm1
        global rpm2
        global rpm3
        global rpm4

        global time_loop
        global time_loop_prev

        global latitude_dms
        global longitude_dms
        
        global control_style
        global control_style_prev

        global direction_degree
        global target_distance
        global rpl_lat
        global rpl_long
        global mqtt_message_time
        global mqtt_message_time_prev
        global speed_button

        global control_direction_send
        global control_direction_send1
        global control_direction_send2
        global control_direction_send3
        global control_direction_send4


        global propeller_speed

        global propeller_speed1
        global propeller_speed2
        global propeller_speed3
        global propeller_speed4

        global propeller_speed1_buffer
        global propeller_speed2_buffer
        global propeller_speed3_buffer
        global propeller_speed4_buffer

        global propeller_mode
        global propeller_mode_prev

        global spc_indicator_color1
        global spc_indicator_color2
        global spc_indicator_color3
        global spc_indicator_color4

        global throttle_indicator_color1
        global throttle_indicator_color2
        global throttle_indicator_color3
        global throttle_indicator_color4

        global analog_lock

        global power
        global power_set

        global csv_message_time
        global csv_message_time_prev

        

        global heading_prev
        global heading_speed

        global n_dot
        global e_dot
        global psi_dot
        global x_dot
        global y_dot

        global control_prop
        global j_theta
        global v

        global n_error
        global e_error

        global error_body_fixed
        global x_error
        global y_error

        global zone

        global str1_target_buffer
        global str2_target_buffer
        global str3_target_buffer
        global str4_target_buffer

        global latitude_integer
        global latitude_fractional

        global longitude_integer
        global longitude_fractional
        
        global latitude_aux
        global longitude_aux
        
        global gps_time_prev
        global lat_pole

        global long_pole

        global radius_zone
        global lat_index

        global joystick1_status
        global joystick2_status
        global joystick2_time
        global joystick2_time_prev

        global state_space

        global ship_radius_zone


        global x_gain
        global y_gain
        global yaw_positive_gain
        global yaw_negative_gain

        global steering1_sensor
        
        global station_keeping_state_prev
        
        global front_gps_time
        global front_gps_time_prev
        global front_gps_color
        global heading
        global heading_magneto
        global heading_dual_gps
        global global_points
        global lat_chute, long_chute
        
        global_points = body_to_latlon(val_latitude , val_longitude, heading_magneto, relative_points)        
        
        lat_chute, long_chute = global_points["chute"]
        #print(global_points)
        front_gps_time = time.time() - front_gps_time_prev
        if (front_gps_time < 5):
            front_gps_color = "green"
            
        else :
            front_gps_color = "red"
        


        joystick2_time = time.time() - joystick2_time_prev
        if(joystick2_time > 5):
            joystick2_status = "off"
        else:
            joystick2_status = "on"


        spc_message_time = time.time() - spc_message_time_prev
        if (spc_message_time > 2):
            spc_indicator_color1 = "red"
            spc_indicator_color4 = "red"
        else:
            spc_indicator_color1 = "green"
            spc_indicator_color4 = "green"
            
            
        
        gyro_message_time = time.time() - gyro_message_time_prev
        if (gyro_message_time > 2):
            spc_indicator_color2 = "red"
            spc_indicator_color3 = "red"
            
        else:
            spc_indicator_color2 = "green"
            spc_indicator_color3 = "green"


        lat_index = len(rpl_lat)
        #print(position_error)
        
        
        if ((lat_index > 1) and (position_error < 5) and (station_keeping_state == "off") and (station_keeping_state_prev == station_keeping_state)):
            
            print("clear point")
            rpl_lat = rpl_lat[1:]
            rpl_long = rpl_long[1:]
                    
        
        if (prev_val("lat_index", lat_index) == 0):
            print(lat_index)
            print("index changed")
            
        if (gps_type  == 1):
            val_latitude = latitude_integer + latitude_fractional
            val_longitude = longitude_integer + longitude_fractional

        if (gps_type == 2):
            if (abs(latitude_aux) > 0.00001):
                val_latitude = latitude_aux
            if (abs(longitude_aux) > 0.00001):
                val_longitude = longitude_aux
            
        if (val_latitude > 0):
            lat_pole = "N"
        else:
            lat_pole = "S"
            
        #print(msg)

        
        if (val_longitude > 0):
            long_pole = "E"
            
        else:
            long_pole = "W"
        
        
        
        try:
            position_error = round(meter_conversion(val_latitude, val_longitude, float(rpl_lat[0]), float(rpl_long[0])),2)
        except:
            position_error = 0

        
        try:
            dir_error = int(shortest_psi(heading, map_angle_conversion(float(rpl_lat[0]), float(rpl_long[0]), val_latitude, val_longitude)))
            
        except:
            dir_error = 0


        try:
            dir_error_earth_fixed = int(map_angle_conversion(float(rpl_lat[0]), float(rpl_long[0]), val_latitude, val_longitude))%360
        except:
            dir_error_earth_fixed = 0

        

        time_loop = time.time() - time_loop_prev
        if (time_loop > 0.01):
            #print("looping")
            time_loop_prev = time.time()
        
        
        gps_time = time.time() - gps_time_prev
        gps_aux_time = time.time() - gps_aux_time_prev
        
        if (gps_time > 4 and gps_aux_time > 4):
            gps_type = 0
            gps_status_color = "red"
        else:
            if (gps_time < 4):
                gps_type  = 1
                gps_status_color = "green"
            else :
                if (gps_aux_time < 4):
                    gps_type  = 2
                    gps_status_color = "yellow"


        latitude_dms = decimal_to_dms(val_latitude)
        longitude_dms = decimal_to_dms(val_longitude)
        
        heading_dual_gps = dual_gps_heading(val_latitude, val_longitude, lat_front, long_front)
        
        if (heading_method == "magneto"):
            heading = heading_magneto
            
        if (heading_method == "dual"):
            heading = heading_dual_gps
        

        heading_error = shortest_psi(heading, heading_target)
        
        try:
            n_error = round(meter_conversion(val_latitude, 0, float(rpl_lat[0]), 0),2)
            e_error = round(meter_conversion(val_longitude, 0, float(rpl_long[0]), 0),2)
        except:
            n_error = 0
            e_error = 0

        psi_dot = round(heading_speed, 2)

        j_theta = np.array([[np.cos(heading * float(np.pi/180)), -np.sin(heading * float(np.pi/180)), 0],
              [np.sin(heading * float(np.pi/180)), np.cos(heading* float(np.pi/180)), 0],
              [0, 0, 1]])
        
        v = np.linalg.inv(j_theta) @ np.array([[n_dot],[e_dot],[psi_dot]])
        x_dot = round(v[0,0], 1)
        y_dot = round(v[1,0], 1)


        error_body_fixed = np.linalg.inv(j_theta) @ np.array([[n_error],[e_error],[psi_error]])
        x_error = abs(round(float(error_body_fixed[0]),0))
        y_error = abs(round(float(error_body_fixed[1]),0))
        
        y_ref = np.array([x_error, y_error, heading]).reshape(-1, 1)
        
        try:
            state_space = {
                "A_discrete": A.tolist(),
                "B_discrete": B.tolist(),
                "C_discrete": C.tolist(),
                "D_discrete": D.tolist(),
                "y_ref" : y_ref.tolist(),
                "lat" : val_latitude,
                "long" : val_longitude,
                "lat_target": rpl_lat[0],
                "lon_target":rpl_long[0]
            }

        except:
            state_space = {
                "A_discrete": A.tolist(),
                "B_discrete": B.tolist(),
                "C_discrete": C.tolist(),
                "D_discrete": D.tolist(),
                "y_ref" : y_ref.tolist(),
                "lat" : val_latitude,
                "long" : val_longitude,
                "lat_target": val_latitude,
                "lon_target": val_longitude
            }

        # Menyimpan ke dalam file JSON — throttled to 1 Hz, not 10 Hz
        file_path = 'state_space.json'
        if (time.time() - getattr(self, '_json_write_prev', 0)) > 1.0:
            try:
                with open(file_path, 'w') as f:
                    json.dump(state_space, f)
            except Exception:
                pass
            self._json_write_prev = time.time()
        
        '''
        if (control_style == "individual" and joystick_mode == 1):
            if (propeller_mode == 0):
                if speed_button > 0:
                    propeller_speed1_buffer = propeller_speed1_buffer + 5
                    propeller_speed2_buffer = propeller_speed2_buffer + 5
                    propeller_speed3_buffer = propeller_speed3_buffer + 5
                    propeller_speed4_buffer = propeller_speed4_buffer + 5

                if speed_button < 0:
                    propeller_speed1_buffer = propeller_speed1_buffer - 5
                    propeller_speed2_buffer = propeller_speed2_buffer - 5
                    propeller_speed3_buffer = propeller_speed3_buffer - 5
                    propeller_speed4_buffer = propeller_speed4_buffer - 5

            if (propeller_mode == 1):
                str1_target_buffer = (control_direction)
                if speed_button > 0:
                    propeller_speed1_buffer = propeller_speed1_buffer + 5
                if speed_button < 0:
                    propeller_speed1_buffer = propeller_speed1_buffer - 5


            if (propeller_mode == 2):
                str2_target_buffer = (control_direction)
                if speed_button > 0:
                    propeller_speed2_buffer = propeller_speed2_buffer + 5
                if speed_button < 0:
                    propeller_speed2_buffer = propeller_speed2_buffer - 5

            if (propeller_mode == 3):
                str3_target_buffer = (control_direction)
                if speed_button > 0:
                    propeller_speed3_buffer = propeller_speed3_buffer + 5

                if speed_button < 0:
                    propeller_speed3_buffer = propeller_speed3_buffer - 5

            if (propeller_mode == 4):
                str4_target_buffer = (control_direction)
                if speed_button > 0:
                    propeller_speed4_buffer = propeller_speed4_buffer + 5
                if speed_button < 0:
                    propeller_speed4_buffer = propeller_speed4_buffer - 5
                
        '''  

       
        #codingan otomatis
        
        '''
        #if (control_style == "central"):
        #print(user_control)
        if (user_control == "auto" and central_status == "central"):
            #print("auto")
            
            if (heading_error > 0):
                propeller_speed1_buffer = (heading_speed*-1)*3
                propeller_speed4_buffer = (heading_error) * 3
                                
            else :
                propeller_speed1_buffer = abs(heading_error) * 3
                propeller_speed4_buffer = (heading_speed)* 3

            heading_target = (heading_target + heading_target_status)%360
                        
            if(abs(dir_error) > 90 and abs(dir_error) < 180):    
                str1_target_buffer = - (90 + constrain((y_error*20), 0, 50))     
                str4_target_buffer = (90 + constrain((y_error*20), 0, 50))   
            else:
                str1_target_buffer = -(90 - constrain((y_error*20), 0, 50))  
                str4_target_buffer = (90 - constrain((y_error*20), 0, 50)) 

            str2_target_buffer = dir_error
            str3_target_buffer = dir_error

            
            if(str1_target_buffer < 0):
               str1_target_buffer = 360 - abs(str1_target_buffer)
        
            if(str2_target_buffer < 0):
               str2_target_buffer = 360 - abs(str2_target_buffer)
               
            if(str3_target_buffer < 0):
               str3_target_buffer = 360 - abs(str3_target_buffer)
               
            if(str4_target_buffer < 0):
               str4_target_buffer = 360 - abs(str4_target_buffer)
            
            power = constrain(((position_error * 100) + (position_error_dot * 5)), -100 ,100)


            print("auto ",heading_target, propeller_speed1_buffer, propeller_speed4_buffer)
            #propeller_speed2_buffer = constrain(power,0,50)#integral_correction(heading_error, 0.1, propeller_speed3_buffer, str2_target_buffer,1)
            #propeller_speed3_buffer = constrain(power,0,50)
                        
            
            if (navigation_mode_text == "forward"):
                pass
                
                if (user_control == "auto"):
                    #steering control
                    print("auto")
                    heading_target = (heading_target + heading_target_status)%360
                    
                    
                    
                    if (fsm_scheme == "scheme1"):
                        #print("scheme1")
                        if (heading_error > 0):
                            propeller_speed1_buffer = (heading_speed*-1)*3
                            propeller_speed4_buffer = (heading_error) * 3
                                
                        else :
                            propeller_speed1_buffer = abs(heading_error) * 3
                            propeller_speed4_buffer = (heading_speed)* 3

                        heading_target = (heading_target + heading_target_status)%360
                        
                        if(abs(dir_error) > 90 and abs(dir_error) < 180):    
                            str1_target_buffer = - (90 + constrain((y_error*20), 0, 50))     
                            str4_target_buffer = (90 + constrain((y_error*20), 0, 50))   
                        else:
                            str1_target_buffer = -(90 - constrain((y_error*20), 0, 50))  
                            str4_target_buffer = (90 - constrain((y_error*20), 0, 50)) 

                        str2_target_buffer = dir_error
                        str3_target_buffer = dir_error

                        power = constrain(((position_error * 100) + (position_error_dot * 5)), -100 ,100)

                        propeller_speed2_buffer = constrain(power,0,50)#integral_correction(heading_error, 0.1, propeller_speed3_buffer, str2_target_buffer,1)
                        propeller_speed3_buffer = constrain(power,0,50)
                        
                   
                    
                    
                    if (fsm_scheme == "scheme2"):
                        #print("scheme2")
                        if (position_error < ship_radius_zone):
                            #didalam radius
                            radius_zone = 1
                            str1_target_buffer = -90
                            str2_target_buffer = -90
                            str3_target_buffer = 90
                            str4_target_buffer = 90

                            propeller_speed1_buffer = yaw_negative_gain[0][0] * -heading_error #yaw_pos
                            propeller_speed2_buffer = yaw_positive_gain[0][0] * heading_error #yaw_pos
                            propeller_speed3_buffer = yaw_negative_gain[0][0] * -heading_error #yaw_pos
                            propeller_speed4_buffer = yaw_positive_gain[0][0] * heading_error #yaw_pos

                        if ((position_error) > ship_radius_zone and (-80 < dir_error < -10)):
                            #maju kiri
                            radius_zone = 2
                            str1_target_buffer = -90
                            str2_target_buffer = -45
                            str3_target_buffer = 0
                            str4_target_buffer = 90

                            propeller_speed1_buffer = yaw_negative_gain[0][1] * -heading_error #yaw_pos
                            propeller_speed2_buffer = y_gain[0][1]* y_error# y_gain
                            propeller_speed3_buffer = x_gain[0][1] * x_error #x_gain
                            propeller_speed4_buffer = (yaw_positive_gain[0][1] * heading_error)#yaw neg
                            
                            
                        if ((position_error) > ship_radius_zone and (-10 < dir_error < 10)):
                            #maju lurus
                            radius_zone = 3
                            str1_target_buffer = -90
                            str2_target_buffer = -45
                            str3_target_buffer = 45
                            str4_target_buffer = 90


                            propeller_speed1_buffer =  yaw_negative_gain[0][2] * -heading_error #yaw_neg
                            propeller_speed2_buffer =  x_gain[0][2] * x_error #x_gain
                            propeller_speed3_buffer =  x_gain[0][2] * x_error #y_gain
                            propeller_speed4_buffer = (yaw_positive_gain[0][2] * heading_error)#yaw pos
                        
                        if ((position_error) > ship_radius_zone and (10 < dir_error < 80)):
                            radius_zone = 4
                            #maju kanan
                            str1_target_buffer = -90
                            str2_target_buffer = 0
                            str3_target_buffer = 45
                            str4_target_buffer = 90

                            propeller_speed1_buffer = 0
                            propeller_speed2_buffer = 0
                            propeller_speed3_buffer = 0
                            propeller_speed4_buffer = 0

                            propeller_speed1_buffer = yaw_positive_gain[0][3] * -heading_error #yaw_pos
                            propeller_speed2_buffer = x_gain[0][3] * x_error# x_gain
                            propeller_speed3_buffer = y_gain[0][3]  * y_error #x_gain
                            propeller_speed4_buffer = (yaw_negative_gain[0][3] * heading_error)#yaw neg

                        if ((position_error) > ship_radius_zone and (80 < dir_error < 100)):
                            #kanan
                            radius_zone = 5
                            str1_target_buffer = -180
                            str2_target_buffer = 0
                            str3_target_buffer = 45
                            str4_target_buffer = 135

                            propeller_speed1_buffer =  yaw_positive_gain[0][4] * heading_error #yaw_pos
                            propeller_speed2_buffer =  yaw_negative_gain[0][4] * -heading_error# yaw neg
                            propeller_speed3_buffer = y_gain[0][4]  * y_error #y_gain
                            propeller_speed4_buffer = (y_gain[0][4] * y_error)#y_gain

                        if ((position_error) > ship_radius_zone and (100 < dir_error < 170)):
                            #kanan mundur
                            radius_zone = 6
                            str1_target_buffer = -180
                            str2_target_buffer = -90
                            str3_target_buffer = 90
                            str4_target_buffer = 135

                            propeller_speed1_buffer = x_gain[0][5] * x_error
                            propeller_speed2_buffer = yaw_positive_gain[0][5] * heading_error
                            propeller_speed3_buffer = yaw_negative_gain[0][5] * -heading_error
                            propeller_speed4_buffer = y_gain[0][5] * y_error
                        
                        if ((position_error) > ship_radius_zone and (abs(dir_error) > 170)):
                            #mundur
                            radius_zone = 7
                            str1_target_buffer = -135
                            str2_target_buffer = -90
                            str3_target_buffer = 90
                            str4_target_buffer = 135

                            propeller_speed1_buffer = x_gain[0][6] * x_error
                            propeller_speed2_buffer = yaw_positive_gain[0][6] * heading_error
                            propeller_speed3_buffer = yaw_negative_gain[0][6] * -heading_error
                            propeller_speed4_buffer = x_gain[0][6] * x_error

                        if ((position_error) > ship_radius_zone and (-170 < dir_error < -100)):
                            #mundur kiri
                            radius_zone = 8
                            str1_target_buffer = -135
                            str2_target_buffer = -90
                            str3_target_buffer = 90
                            str4_target_buffer = 180

                            propeller_speed1_buffer = y_gain[0][7] * y_error
                            propeller_speed2_buffer = yaw_positive_gain[0][7] * heading_error
                            propeller_speed3_buffer = yaw_negative_gain[0][7] * -heading_error
                            propeller_speed4_buffer = x_gain[0][7] * x_error

                        if ((position_error) > ship_radius_zone and (-100 < dir_error < -80)):
                            #kiri 
                            radius_zone = 9
                            str1_target_buffer = -135
                            str2_target_buffer = -45
                            str3_target_buffer = 0
                            str4_target_buffer = 180

                            propeller_speed1_buffer = y_gain[0][8] * y_error
                            propeller_speed2_buffer = y_gain[0][8] *y_error
                            propeller_speed3_buffer = yaw_positive_gain[0][8] * heading_error
                            propeller_speed4_buffer = yaw_negative_gain[0][8] * -heading_error


                        propeller_speed1_buffer = max(0, min(100, propeller_speed1_buffer))
                        propeller_speed2_buffer = max(0, min(100, propeller_speed2_buffer))
                        propeller_speed3_buffer = max(0, min(100, propeller_speed3_buffer))
                        propeller_speed4_buffer = max(0, min(100, propeller_speed4_buffer))

                    
                    
                    
                    print(radius_zone)
                    
                    
                    if (fsm_scheme = "scheme1"):
                        if (heading_error > 0):
                            propeller_speed1_buffer = (heading_speed*-1)*10
                            propeller_speed4_buffer = (heading_error) * 1
                                
                        else :
                            propeller_speed1_buffer = abs(heading_error) * 10
                            propeller_speed4_buffer = (heading_speed)*1

                        heading_target = (heading_target + heading_target_status)%360
                        
                        if(abs(dir_error) > 90 and abs(dir_error) < 180):    
                            str1_target_buffer = - (90 + constrain((y_error*20), 0, 50))     
                            str4_target_buffer = (90 + constrain((y_error*20), 0, 50))   
                        else:
                            str1_target_buffer = -(90 - constrain((y_error*20), 0, 50))  
                            str4_target_buffer = (90 - constrain((y_error*20), 0, 50)) 

                        str2_target_buffer = dir_error
                        str3_target_buffer = dir_error

                        power = constrain(((position_error * 100) + (position_error_dot * 5)), -100 ,100)

                        propeller_speed2_buffer = (power)#integral_correction(heading_error, 0.1, propeller_speed3_buffer, str2_target_buffer,1)
                        propeller_speed3_buffer = (power)
                        
                    
        
                    
                
                
                if (user_control == "manual"):
                    str1_target_buffer = -90 
                    str2_target_buffer = 0 
                    str3_target_buffer = 0 
                    str4_target_buffer = 90 
                    
                    if (power_set == -1):
                        power = power - 2

                    if (power_set == 1):
                        power = power + 2

                    power = constrain(power, -100, 100)

                    heading_target = (heading_target + heading_target_status)%360
                    

                    if power >= 0:
                        str1_target_buffer = -90 #-90 
                        str2_target_buffer = 0
                        str3_target_buffer = 0
                        str4_target_buffer = 90 #90

                        
                        propeller_speed2_buffer = abs(power) - (heading_error * 0.05)#integral_correction(heading_error, 0.01, propeller_speed3_buffer, str2_target_buffer, 1)
                        propeller_speed3_buffer = abs(power)

                        if (heading_error > 0):
                            propeller_speed1_buffer = (heading_speed*-1)*3
                            propeller_speed4_buffer = (heading_error) * 3
                                
                        else :
                            propeller_speed1_buffer = abs(heading_error) * 3
                            propeller_speed4_buffer = (heading_speed)*3


                    else :
                        str1_target_buffer = -90 #-90
                        str2_target_buffer = 180
                        str3_target_buffer = 180
                        str4_target_buffer = 90 #90

                        propeller_speed2_buffer = abs(power)
                        propeller_speed3_buffer = abs(power)


                        if (heading_error > 0):
                            propeller_speed1_buffer = (heading_speed*-1)*5
                            propeller_speed4_buffer = (heading_error) * 5
                                
                        else :
                            propeller_speed1_buffer = abs(heading_error) * 5
                            propeller_speed4_buffer = (heading_speed)*5

                    

                        
                
                        
            if (navigation_mode_text == "sway"):

                heading_target = (heading_target + heading_target_status)%360
                if (user_control == "auto"):
                    propeller_speed1_buffer = power 
                    propeller_speed2_buffer = power 
                    propeller_speed3_buffer = power
                    propeller_speed4_buffer = power 
                    

                if (user_control == "manual"):
                    if (power_set == -1):
                        power = power - 2

                    if (power_set == 1):
                        power = power + 2

                    power = constrain(power, -100, 100)

                    if (heading_error > 0):
                        propeller_speed1_buffer = (heading_speed*-1)*5
                        propeller_speed4_buffer = abs(heading_error) * 5
                                
                    else :
                        propeller_speed1_buffer = abs(heading_error) * 5
                        propeller_speed4_buffer = (heading_speed)*5


                    
                    if (power > 0):
                        propeller_speed2_buffer = 0
                        propeller_speed3_buffer = abs(power)

                    else:
                        propeller_speed2_buffer = abs(power)
                        propeller_speed3_buffer = 0

                   
        
        else:
            heading_target = heading
        
        
        if (propeller_switch == 0):
            throttle_indicator_color1 = "red"
            throttle_indicator_color2 = "red"
            throttle_indicator_color3 = "red"
            throttle_indicator_color4 = "red"

            propeller_speed1_buffer = 0
            propeller_speed2_buffer = 0
            propeller_speed3_buffer = 0
            propeller_speed4_buffer = 0

            if (propeller_mode == 1):
                
                str1_target_buffer = (control_direction)
                control_direction_send1 = control_direction_send
                    #propeller_speed1 = propeller_speed1_buffer + propeller_speed
                    #S1 = propeller_speed1
                    

                throttle_indicator_color1 = "#F77E00"
                throttle_indicator_color2 = "red"
                throttle_indicator_color3 = "red"
                throttle_indicator_color4 = "red"

            if (propeller_mode == 2):

                str2_target_buffer = (control_direction)
                #propeller_speed2 = propeller_speed2_buffer + propeller_speed
                control_direction_send2 = control_direction_send
                #S2 = propeller_speed2

                throttle_indicator_color1 = "red"
                throttle_indicator_color2 = "#F77E00"
                throttle_indicator_color3 = "red"
                throttle_indicator_color4 = "red"

            if (propeller_mode == 3):
                str3_target_buffer = (control_direction)
                #propeller_speed3 = propeller_speed3_buffer + propeller_speed
                control_direction_send3 = control_direction_send
                #S3 = propeller_speed3

                throttle_indicator_color1 = "red"
                throttle_indicator_color2 = "red"
                throttle_indicator_color3 = "#F77E00"
                throttle_indicator_color4 = "red"

            if (propeller_mode == 4):
                str4_target_buffer = (control_direction)
                #propeller_speed4 = propeller_speed4_buffer + propeller_speed
                control_direction_send4 = control_direction_send
                #S4 = propeller_speed4
                throttle_indicator_color1 = "red"
                throttle_indicator_color2 = "red"
                throttle_indicator_color3 = "red"
                throttle_indicator_color4 = "#F77E00"

            str1_target = str1_target_buffer
            str2_target = str2_target_buffer
            str3_target = str3_target_buffer
            str4_target = str4_target_buffer
            


        if (propeller_switch == 1):
            throttle_indicator_color1 = "green"
            throttle_indicator_color2 = "green"
            throttle_indicator_color3 = "green"
            throttle_indicator_color4 = "green"
                
            str1_target = str1_target_buffer
            str2_target = str2_target_buffer
            str3_target = str3_target_buffer
            str4_target = str4_target_buffer

            propeller_speed1_buffer = constrain(propeller_speed1_buffer, 0, 100)
            propeller_speed2_buffer = constrain(propeller_speed2_buffer, 0, 100)
            propeller_speed3_buffer = constrain(propeller_speed3_buffer, 0, 100)
            propeller_speed4_buffer = constrain(propeller_speed4_buffer, 0, 100)

            
            if (propeller_mode == 0):
                throttle_indicator_color1 = "green"
                throttle_indicator_color2 = "green"
                throttle_indicator_color3 = "green"
                throttle_indicator_color4 = "green"

            if (propeller_mode == 1):
                if (analog_lock == 1):
                    str1_target_buffer = (control_direction)

                throttle_indicator_color1 = "#F77E00"
                throttle_indicator_color2 = "green"
                throttle_indicator_color3 = "green"
                throttle_indicator_color4 = "green"

            if (propeller_mode == 2):
                if (analog_lock == 1):
                    str2_target_buffer = (control_direction)
                throttle_indicator_color1 = "green"
                throttle_indicator_color2 = "#F77E00"
                throttle_indicator_color3 = "green"
                throttle_indicator_color4 = "green"

            if (propeller_mode == 3):
                if (analog_lock == 1):
                    str3_target_buffer = (control_direction)

                throttle_indicator_color1 = "green"
                throttle_indicator_color2 = "green"
                throttle_indicator_color3 = "#F77E00"
                throttle_indicator_color4 = "green"

            if (propeller_mode == 4):
                if (analog_lock == 1):
                    str4_target_buffer = (control_direction)
                throttle_indicator_color1 = "green"
                throttle_indicator_color2 = "green"
                throttle_indicator_color3 = "green"
                throttle_indicator_color4 = "#F77E00"

                
        propeller_mode_prev = propeller_mode
        '''

        
        control_prop = str(str("ṅ : ")+str(n_dot)+str("\nė : ")+str(e_dot)+str("\nψ_dot : ") + str(psi_dot)
                        +str("\nẋ : ")+str(x_dot)+ str("\nẏ : ")+str(y_dot) + str("\nn_error : ")+str(n_error)
                        + str("\ne_error : ")+str(e_error)+ str("\nx_error : ")+str(x_error)+ str("\ny_error : ")+str(y_error))


        mqtt_message_time = time.time() - mqtt_message_time_prev
        
        if (mqtt_message_time > 1):  
            
            heading_speed =(0.8 * heading_speed) + (0.2 *shortest_psi(heading,heading_prev)/0.2)
            
            str1_target = str1_target_buffer
            str2_target = str2_target_buffer
            str3_target = str3_target_buffer
            str4_target = str4_target_buffer
            
            ###################### Miniatur DPS #######################################
            #print(propeller_speed1_buffer)
            '''
            client.publish("propeller1", str(propeller_speed1_buffer))
            client.publish("propeller4", str(propeller_speed2_buffer))
            client.publish("propeller3", str(propeller_speed3_buffer))
            client.publish("propeller2", str(propeller_speed4_buffer))
            '''
            

            client.publish("steer1_command", str(str1_target))
            client.publish("steer2_command", str(str2_target))
            client.publish("steer3_command", str(str3_target))
            client.publish("steer4_command", str(str4_target))

            client.publish("user_control", str(user_control))
            client.publish("yaw_barge", str(heading_magneto))
            mqtt_message_time_prev = time.time()


        csv_message_time = time.time() - csv_message_time_prev

        if (csv_message_time > 2):
            waktu = dt.datetime.now()
            filename = str("DP Experimental RECORD " ) + str(current_time.day)+str("-")+str(current_time.month)+str("-")+str(current_time.year) + str(".csv")
            with open(filename, 'a') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    rows = [ [str(str(waktu.hour) + str(":") + str(waktu.minute)+ str(":") + str(waktu.second)),
                              str(val_latitude), str(val_longitude), 
                              str(round(propeller_speed1,0)), str(round(propeller_speed2,0)), str(round(propeller_speed3,0)), str(round(propeller_speed4,0)), 
                              str(round(str1_target,0)), str(round(str2_target,0)), str(round(str3_target,0)), str(round(str4_target,0)),
                              str(heading), str(heading_target), str(navigation_mode_text), str(position_error), str(dir_error), str(payout), str(lat_chute), str(long_chute)]]
                    csvwriter.writerows(rows)

            csv_message_time_prev = time.time()


        
        control_style_prev = control_style
        
        station_keeping_state_prev = station_keeping_state
        

        speed_measurement_time = time.time() - speed_measurement_time_prev
        if (speed_measurement_time > 1):
            position_error_dot = (position_error - position_error_prev)

            n_dot = round(meter_conversion(val_latitude,0, latitude_prev,0),2)
            e_dot = round(meter_conversion(0,val_longitude, 0,longitude_prev),2)
            
            try:
                speed_ship = round(float(np.sqrt(n_dot**2 + e_dot**2)) ,3)
            except:
                pass
            heading_prev = heading
            latitude_prev = val_latitude
            longitude_prev = val_longitude
            position_error_prev = position_error

            speed_measurement_time_prev = time.time()



        


def on_message(client, userdata, message):
    global gps_time_prev
    global gps_aux_time_prev
    msg = str(message.payload.decode("utf-8"))
    t = str(message.topic)

    if(msg[0] == 'c'):
        val =  1
    else:
        val = (msg)
        
        
    if (t == "payout"):
        global payout
        payout = float(msg) 
        #print(steering1_sensor)

    if (t == "steering1_sensor"):
        global steering1_sensor
        global spc_message_time_prev
        spc_message_time_prev = time.time()
        steering1_sensor = float(msg)
        #print(steering1_sensor)
        

    if (t == "steering2_sensor"):
        global steering2_sensor
        global gyro_message_time_prev
        steering2_sensor = float(msg)
        gyro_message_time_prev = time.time()

    if (t == "steering3_sensor"):
        global steering3_sensor
        steering3_sensor = float(msg)

    if (t == "steering4_sensor"):
        global steering4_sensor
        steering4_sensor = float(msg)

    if (t == "SPC1"):
        global SP1
        global EC1_time_prev
        if (msg =="Central"):
            EC1_time_prev = time.time()
        #print(msg)
            #SP1 = val

    if (t == "SPC2"):            
        global SP2
        global EC2_time_prev
        if (msg == "Central"):
            EC2_time_prev = time.time()
        #print(msg)
            #SP2 = val

    if (t == "SPC3"):
        global SP3
        global EC3_time_prev
        if (msg == "Central"):
            EC3_time_prev = time.time()
            #SP3 = val

    if (t == "SPC4"):
        global SP4
        global EC4_time_prev
        if (msg == "Central"):
            EC4_time_prev = time.time()
            #SP4 = val



    if (t == "lat_nmea_integer_pc"): #GPS/lat or lat_nmea
        global gps_time_prev
        global latitude_integer
        gps_time_prev = time.time()
        
        latitude_integer = float(msg)
        

    if (t == "lat_nmea_fractional_pc"): #GPS/lat or lat_nmea
        
        global latitude_fractional
        latitude_fractional = float(msg)

    
    if (t == "long_nmea_integer_pc"): #GPS/lat or lat_nmea

        global longitude_integer        
        longitude_integer = float(msg)

    if (t == "long_nmea_fractional_pc"): #GPS/lat or lat_nmea
        global longitude_fractional    
        longitude_fractional = float(msg)
        
        
    if (t == "latitude_aux"):
        global latitude_aux
        
        if (abs(float(msg)) > 0.0001):
            latitude_aux = float(msg)
        gps_aux_time_prev = time.time()
        #print(latitude_aux)
        
    if (t == "longitude_aux"):
        global longitude_aux
        if (abs(float(msg)) > 0.0001):
            longitude_aux = float(msg)
        #print(longitude_aux)
            
            
    if (t=="lat_front"):
        global lat_front
        global front_gps_time_prev
        lat_front = float(msg)
        front_gps_time_prev = time.time()
        
    if (t=="long_front"):
        global long_front
        long_front = float(msg)
 
    if (t == "yaw_actual"):
        global heading_magneto
        
        #try:
            # y =ax^2 + bx + c
        value = float(msg)
        
        '''
        if (value > 0 and value <= 90):
            heading_magneto = map_value(value, 0,90, 9,103)
        
        if (value > 90 and value <= 180):
            heading_magneto = map_value(value,90,180,103, 182)
                
        if (value > 180 and value <= 270):
            heading_magneto = map_value(value,180, 270, 182, 315)
        
        if (value > 270 and value <= 330):
            heading_magneto = map_value(value,270,330, 316, 355)
        
        if (value > 330 and value <= 347):
            heading_magneto = map_value(value,330,347, 355, 359)
        
        if (value > 347 and value <= 348):
            heading_magneto = map_value(value,347,348, 359, 0)
        
        if (value > 348 and value <= 359):
            heading_magneto = map_value(value,348,359, 0, 8)
        '''               
        #heading_magneto = int(heading_magneto)  # default jika tidak masuk range manapun
        heading_magneto = int(value)
        #    print (value)
        #except (TypeError, ValueError):
        #    print(f"Invalid heading value: {msg}")
        #    heading = 0  # atau nilai default lain sesuai kebutuhan
            
            
    if (t == "cog"):
        global cog
        cog = int(msg)
        

    if (t == "winddirect"):
        global Wdirect
        Wdirect = map_angle_with_offset((float(msg)),0, 360, 0, 360, 0) 

    if (t == "windspeed"):
        global Wspeed
        Wspeed = round(float(msg)/10,1)

    if (t == "roll_pontoon"):
        global pitch

        pitch = float(msg)


        

    if (t == "pitch_pontoon"):
        global roll
        roll = float(msg)

      
    if (t == 'rpm1'):
        global rpm1
        rpm1 = float(msg)
            
    if (t == 'rpm2'):
        global rpm2
        rpm2 = float(msg)
            
    if (t == 'rpm3'):
        global rpm3
        rpm3 = float(msg)
            
    if (t == 'rpm4'):
        global rpm4
        rpm4 = float(msg)
        #print(rpm4)
    
    
    if (t == 'flow_lpm'):
        global flow_lpm
        flow_lpm = float(msg)
        
    if (t == 'flow_lpm2'):
        global flow_lpm2
        flow_lpm2 = float(msg)

    if(t == 'joystick_mqtt'):
        global joystick2_time_prev
        joystick2_time_prev = time.time()

    
    if(t=='propeller1'):
        global propeller_speed1_buffer
        #if (joystick_mode == 2):
        propeller_speed1_buffer = int(msg)
            #print(propeller_speed1_buffer)

    if(t=='propeller2'):
        global propeller_speed2_buffer
        #if (joystick_mode == 2):
        propeller_speed2_buffer = int(msg)

    if(t=='propeller3'):
        global propeller_speed3_buffer
        #if (joystick_mode == 2):
        propeller_speed3_buffer = int(msg)

    if(t=='propeller4'):
        global propeller_speed4_buffer
        #if (joystick_mode == 2):
        propeller_speed4_buffer = int(msg)

    
    if(t=='central_status'):
        global central_status
        central_status = msg
    
    if(t=='steer1_req'):
        global str1_target_buffer
        if (user_control == "manual"):
        #if(central_status == "central"):
            str1_target_buffer = int(msg)
            #print(msg)
    
    if(t=='steer2_req'):
        global str2_target_buffer
        #if(central_status == "central"):
        if (user_control == "manual"):
            str2_target_buffer = int(msg)
        
    
    if(t=='steer3_req'):
        global str3_target_buffer
        if (user_control == "manual"):
        #if(central_status == "central"):
            str3_target_buffer = int(msg)
        
    if(t=='steer4_req'):
        global str4_target_buffer
        #if(central_status == "central"):
        if (user_control == "manual"):
            str4_target_buffer = int(msg)
        
    




########## memanggil class table di mainloop######################
#----------------------------------------------------------------#    
if __name__ == "__main__":


    
    ##Mosquitto Mqtt Configuration
    client= paho.Client("DPS_GUI")
    client.on_message=on_message

    print("connecting to broker ",broker)
    client.connect(broker,port)#connect
    print(broker," connected")
    
    client.loop_start()
    print("Subscribing")


    client.subscribe("propeller1")
    client.subscribe("propeller2")
    client.subscribe("propeller3")
    client.subscribe("propeller4")


    client.subscribe("Set_Speed1")
    client.subscribe("Set_Speed2")
    client.subscribe("Set_Speed3")
    client.subscribe("Set_Speed4")

    client.subscribe("engineconect1")
    client.subscribe("engineconect2")
    client.subscribe("engineconect3")
    client.subscribe("engineconect4")

    client.subscribe("steering1")
    client.subscribe("steering2")
    client.subscribe("steering3")
    client.subscribe("steering4")

    client.subscribe("steering1_sensor")
    client.subscribe("steering2_sensor")
    client.subscribe("steering3_sensor")
    client.subscribe("steering4_sensor")

    


    client.subscribe("SPC1")
    client.subscribe("SPC2")
    client.subscribe("SPC3")
    client.subscribe("SPC4")
    
    client.subscribe("rpm1")
    client.subscribe("rpm2")
    client.subscribe("rpm3")
    client.subscribe("rpm4")

    client.subscribe("GPS/lat")
    client.subscribe("GPS/long")
    client.subscribe("lat_nmea")
    client.subscribe("long_nmea")

    client.subscribe("lat_nmea_fractional")
    client.subscribe("long_nmea_fractional")

    client.subscribe("latitude_aux")
    client.subscribe("longitude_aux")

    client.subscribe("lat_nmea_fractional_pc")
    client.subscribe("long_nmea_fractional_pc")

    client.subscribe("lat_nmea_integer")
    client.subscribe("long_nmea_integer")

    client.subscribe("lat_nmea_integer_pc")
    client.subscribe("long_nmea_integer_pc")
    
    client.subscribe("lat_front")
    client.subscribe("long_front")


    client.subscribe("speed_nmea")
    client.subscribe("yaw")
    client.subscribe("cog")
    client.subscribe("yaw_actual")
    client.subscribe("winddirect")
    client.subscribe("windspeed")
    
    client.subscribe("ship_x")
    client.subscribe("ship_y")
    client.subscribe("roll")
    client.subscribe("pitch")
    client.subscribe("flow_lpm")
    client.subscribe("flow_lpm2")
    client.subscribe("joystick_mqtt")
    
    
    client.subscribe("steer1_command")
    client.subscribe("steer2_command")
    client.subscribe("steer3_command")
    client.subscribe("steer4_command")
    
    
    client.subscribe("steer1_req")
    client.subscribe("steer2_req")
    client.subscribe("steer3_req")
    client.subscribe("steer4_req")
    
    client.subscribe("central_status")
    
    client.subscribe("pitch_pontoon")
    client.subscribe("roll_pontoon")
    
    client.subscribe("payout")
    
    
        
    client.publish("MainControl", "active")#publish
    client.publish("dummyval", str(0))
    
    

    

    main = table()
    
    
#----------------------------------------------------------------#
