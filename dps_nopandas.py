######  PROGRAM MEMANGGIL WINDOWS PYQT5 ##########################

####### memanggil library PyQt5 ##################################

#---------------------------------------------------------------#
import sys
import datetime as dt
import numpy as np
import csv
import json
import os


from PyQt5.QtCore import * 
from PyQt5.QtGui import * 
from PyQt5.QtQml import * 
from PyQt5.QtWidgets import *
from PyQt5.QtQuick import * 
import sys
import time

import numpy as np
from math import sqrt


import math
from math import sin, cos, sqrt, atan2, radians, atan
#----------------------------------------------------------------#
from PyQt5.QtPositioning import QGeoCoordinate
from collections import defaultdict
import threading




isobath_file = "isobath_dumai.csv"


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
    return {
        "latitude": coord.latitude(),
        "longitude": coord.longitude()
    }

def load_depth_points_from_isobath(file_path=isobath_file):
    depth_points = []
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                lat = float(row["Latitude"])
                lon = float(row["Longitude"])
                val = float(row["Value1"]) if row["Value1"] else 0.0
                depth_points.append({"lat": lat, "lon": lon, "depth": val})
            except ValueError:
                continue
    return depth_points

def find_two_nearest_points(lat, lon, depth_points):
    distances = []
    for point in depth_points:
        if "lat" in point and "lon" in point and "depth" in point:
            try:
                dist = sqrt((lat - point["lat"])**2 + (lon - point["lon"])**2)
                distances.append((dist, point))
            except:
                continue
    distances.sort(key=lambda x: x[0])


    if len(distances) >= 2:
        return [distances[0][1], distances[1][1]]
    elif len(distances) == 1:
        return [distances[0][1], distances[0][1]]
    else:
        return None

def idw_from_two_points(lat, lon, p1, p2, power=2):
    def distance(p): return sqrt((lat - p["lat"])**2 + (lon - p["lon"])**2)

    d1 = distance(p1)
    d2 = distance(p2)

    if d1 == 0: return p1["depth"]
    if d2 == 0: return p2["depth"]

    w1 = 1 / (d1 ** power)
    w2 = 1 / (d2 ** power)

    return (w1 * p1["depth"] + w2 * p2["depth"]) / (w1 + w2)

def load_polygons():
    component_polygons = defaultdict(lambda: {"points": [], "type": "", "value": 0.0})
    polygons = []

    with open(isobath_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                cid = int(row["ComponentId"])
                lat = float(row["Latitude"])
                lon = float(row["Longitude"])
                val = float(row["Value1"]) if row["Value1"] else 0.0
            except ValueError:
                continue

            component_polygons[cid]["points"].append(QGeoCoordinate(lat, lon))
            component_polygons[cid]["type"] = row["Type"]
            component_polygons[cid]["value"] = val

    for comp in component_polygons.values():
        coords = comp["points"]
        if len(coords) < 3:
            continue

        center_lat = sum(c.latitude() for c in coords) / len(coords)
        center_lon = sum(c.longitude() for c in coords) / len(coords)

        polygons.append({
            "points": [geo_to_dict(p) for p in coords],
            "type": comp["type"],
            "value": comp["value"],
            "center": {"latitude": center_lat, "longitude": center_lon}
        })

    return polygons

from scipy.optimize import curve_fit

def identification(x, y):

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    def model(t, K, tau):
        return K * (1 - np.exp(-t / tau))

    p0 = [
        np.max(y),
        (x[-1] - x[0]) / 5
    ]

    popt, _ = curve_fit(
        model,
        x,
        y,
        p0=p0,
        bounds=([0,0], [np.inf,np.inf])
    )

    K, tau = popt

    return K, tau


def dir_check(command, direction):
    if ((command == "Kiri" or command == "Kanan")):
        if (direction == "CCW"):
            if (command == "Kanan"):
                return "Kiri"
            if (command == "Kiri"):
                return "Kanan"
    
        else:
            return command
    else:
        return command

sys.path.insert(0, "./lib")

import paho.mqtt.client as paho

steer1 = "Tahan" 
steer2 = "Tahan"
steer3 = "Tahan"
steer4 = "Tahan"

steer1_prev = "Tahan"
steer2_prev = "Tahan"
steer3_prev = "Tahan"
steer4_prev = "Tahan"

steer1_req = 0
steer2_req = 0
steer3_req = 0
steer4_req = 0

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
barge_relative_points = {
    "a": np.array([0, 35]),
    "b": np.array([8, 40]),
    "c": np.array([16, 35]),
    "d": np.array([16, -10]),
    "e": np.array([0, -10]),
    "chute": np.array([8, -10]),
}

tug_relative_points = {
    "a": np.array([-3, 5]),
    "b": np.array([0, 10]),
    "c": np.array([3, 5]),
    "d": np.array([3, -10]),
    "e": np.array([-3, -10]),
    "chute": np.array([0, 0]),
}

tug2_relative_points = {
    "a": np.array([-3, 5]),
    "b": np.array([0, 10]),
    "c": np.array([3, 5]),
    "d": np.array([3, -10]),
    "e": np.array([-3, -10]),
    "chute": np.array([0, 0]),
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

analog1_angle = 0
control_direction = 0



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

rpm_filter = [1,1,1,1]


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


val_latitude =  1.6533388071438695 #centre
filtered_val_latitude = val_latitude#centre
val_longitude = 101.51929189617022   #centre
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

steering1_raw = 0
steering2_raw = 0
steering3_raw = 0
steering4_raw = 0

steer1_error = 0
steer2_error = 0
steer3_error = 0
steer4_error = 0

steer1_error_prev = 0
steer2_error_prev = 0
steer3_error_prev = 0
steer4_error_prev = 0


with open("calib_param.json", "r") as f:
    calib_param = json.load(f)

steering1_offset = int(calib_param["steering1_offset"])
steering2_offset = int(calib_param["steering2_offset"])
steering3_offset = int(calib_param["steering3_offset"])
steering4_offset = int(calib_param["steering4_offset"])

steering_raw_min = calib_param["steering_raw_min"]
steering_raw_max = calib_param["steering_raw_max"]

rpm_filter = calib_param["rpm_filter"]

k_propeller = (calib_param["k_propeller"])
tau_propeller = (calib_param["tau_propeller"])

steer_dir = (calib_param["steer_dir"])

steer_status = ["S", "S", "S","S"]

print("steer dir", steer_dir)



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
central_status_prev = "local"

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


csv_file = "sea_current_now.csv"

#dibaca ulang di on_update_finished() lewat modul csv biasa
lat_seacurrent = []
long_seacurrent = []
dir_seacurrent = []
speed_seacurrent = []

print(lat_seacurrent)
print(long_seacurrent)
print(dir_seacurrent)

current_data = []

for i in range(len(lat_seacurrent)):

    current_data.append({

        "lat": lat_seacurrent[i],
        "lon": long_seacurrent[i],
        "dir": dir_seacurrent[i]

    })

print(current_data)


current_dir = 0
current_speed = 0

lat_wind = []
long_wind = []
wind_dir = 0
wind_speed = 0

def find_speed_seacurrent(lat_ref, lon_ref):

    min_dist = float('inf')
    nearest_idx = -1

    for i in range(len(lat_seacurrent)):

        # hitung jarak sederhana
        dist = math.sqrt(
            (lat_seacurrent[i] - lat_ref)**2 +
            (long_seacurrent[i] - lon_ref)**2
        )

        if dist < min_dist:
            min_dist = dist
            nearest_idx = i

    if nearest_idx == -1:
        return None, None

    return dir_seacurrent[nearest_idx], speed_seacurrent[nearest_idx]



control_prop = ""


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


def change_dir_json(thruster_idx):
    with open("calib_param.json", "r") as f:
        data = json.load(f)

    current = data["steer_dir"][thruster_idx]

    if current == "CW":
        data["steer_dir"][thruster_idx] = "CCW"
    else:
        data["steer_dir"][thruster_idx] = "CW"

    with open("calib_param.json", "w") as f:
        json.dump(data, f, indent=4)

    return data["steer_dir"]

    


def shortest_psi(psi_ref, psi_d):
    psi_temp = (psi_ref-psi_d)%360
    psi_shortest = (psi_temp + 360) *-1 %360 
    if (psi_shortest > 180):
        psi_shortest = psi_shortest - 360
    return psi_shortest   

def steering_direction(error, direction, deadband=5):
    if abs(error) <= deadband:
        return "Tahan"
    cmd = np.sign(error)
    if direction == "CW":
        cmd *= -1
    return "Kiri" if cmd > 0 else "Kanan"


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


# Definisikan kolom sekali di awal (global atau di luar loop)
CSV_COLUMNS = [
    "waktu", "latitude", "longitude",
    "propeller_speed1", "propeller_speed2", "propeller_speed3", "propeller_speed4",
    "str1_target", "str2_target", "str3_target", "str4_target",
    "heading", "heading_target", "navigation_mode_text",
    "position_error", "dir_error", "payout", "lat_chute", "long_chute"
]

_header_written_for_date = None  # global tracker

def log_to_csv(data_row):
    global _header_written_for_date
    waktu = dt.datetime.now()
    today_str = f"{waktu.day}-{waktu.month}-{waktu.year}"
    filename = f"DP Experimental RECORD {today_str}.csv"

    if _header_written_for_date != today_str:
        need_header = (not os.path.isfile(filename)) or (os.path.getsize(filename) == 0)
        _header_written_for_date = today_str
    else:
        need_header = False

    row_dict = dict(zip(CSV_COLUMNS, [waktu.strftime("%H:%M:%S")] + data_row))

    with open(filename, mode='a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_COLUMNS)
        if need_header:
            writer.writeheader()
        writer.writerow(row_dict)


########## mengisi class table dengan instruksi pyqt5#############
#----------------------------------------------------------------#
heading_tug = 15
latitude_tug = 1.153154
longitude_tug = 103.895214

heading_tug2 = 270
latitude_tug2 = 1.154024
longitude_tug2 = 103.896222

global_points = body_to_latlon(val_latitude , val_longitude, heading_magneto, barge_relative_points)        
global_tug_points = body_to_latlon(latitude_tug , longitude_tug, heading_tug, tug_relative_points)
global_tug2_points = body_to_latlon(latitude_tug2 , longitude_tug2, heading_tug2, tug2_relative_points)

import subprocess


class UpdateWorker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    

    def __init__(self, msg):
        super().__init__()
        self.msg = msg

    def run(self):
        """Runs in a background thread — never blocks the GUI."""
        try:
            subprocess.run(["python", "request API.py", self.msg], check=True)
            self.finished.emit()
        except subprocess.CalledProcessError as e:
            self.error.emit(f"Script failed with code {e.returncode}")
        except Exception as e:
            self.error.emit(str(e))




class table(QObject):    
    updateFinished = pyqtSignal()
    
    def __init__(self, parent = None):
        super().__init__(parent)
        self.app = QApplication(sys.argv)
        self.engine = QQmlApplicationEngine(self)
        # Load sonar data
        self.depth_data = load_depth_points_from_isobath(isobath_file)
        print("✅ Titik sonar terload:", len(self.depth_data))

        polygons = load_polygons()

        self.engine.rootContext().setContextProperty("allPolygons", polygons)
        self.engine.rootContext().setContextProperty("backend", self)    
        self.engine.load(QUrl("dps.qml"))
        sys.exit(self.app.exec_())

    @pyqtSlot(result='QVariantList')
    def getCurrentArray(self):
        current_data = []
        for i in range(len(lat_seacurrent)):
            current_data.append({
                "lat": lat_seacurrent[i],
                "lon": long_seacurrent[i],
                "dir": dir_seacurrent[i]
            })
        return current_data



    @pyqtSlot(result='QVariantList')
    def getWindArray(self):
        wind_data = []
        for i in range(len(lat_wind)):
            wind_data.append({
                "lat": lat_wind[i],
                "lon": long_wind[i],
                "dir": dir_wind[i]
            })
        return wind_data



    @pyqtSlot(str)
    def update_data(self, msg):
        self._worker = UpdateWorker(msg)
        self._worker.finished.connect(self.on_update_finished)
        self._worker.error.connect(self.on_update_error)
        self._worker.start()

    

    

    def on_update_finished(self):

        global lat_seacurrent
        global long_seacurrent
        global dir_seacurrent
        global speed_seacurrent
        global current_dir
        global current_speed

        
        global lat_wind
        global long_wind
        global dir_wind

        csv_file = "sea_current_now.csv"
        try:
            lat_seacurrent = []
            long_seacurrent = []
            dir_seacurrent = []
            speed_seacurrent = []

            with open(csv_file, newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    lat_seacurrent.append(float(row["latitude"]))
                    long_seacurrent.append(float(row["longitude"]))
                    dir_seacurrent.append(float(row["direction"]))
                    speed_seacurrent.append(float(row["sea_current_speed"]))

            current_dir, current_speed = find_speed_seacurrent(
                val_latitude,
                val_longitude
            )
        except:
            lat_seacurrent = []
            long_seacurrent = []
            dir_seacurrent = 0
            speed_seacurrent = 0
        

        


        print("update_data.py finished — safe to update UI here")
        print (f"Current direction: {current_dir}, Current speed: {current_speed}")
        self.updateFinished.emit()
    

    @pyqtSlot(result=float)
    def current_dir(self):
        return float(current_dir)
    
    @pyqtSlot(result=float)
    def current_speed(self):
        return float(current_speed)

    def on_update_error(self, msg):
        print(f"update_data.py failed: {msg}")


    @pyqtSlot(str, result='QVariantList')
    def get_barge_point(self, name):
        return list(map(float, global_points.get(name, [0, 0])))
    
    
    @pyqtSlot(str, result='QVariantList')
    def get_tug_point(self, name):
        return list(map(float, global_tug_points.get(name, [0, 0])))
    
    @pyqtSlot(str, result='QVariantList')
    def get_tug2_point(self, name):
        return list(map(float, global_tug2_points.get(name, [0, 0])))

    
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
    def rpm1(self):  return round(rpm1,1)
    
    @pyqtSlot(result=float)
    def rpm2(self):  return round(rpm2, 1)
    
    @pyqtSlot(result=float)
    def rpm3(self):  return round(rpm3,1)
    
    @pyqtSlot(result=float)
    def rpm4(self):  return round(rpm4,1)
    
    
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
    def steering1(self):  return round(steering1_sensor,0)

    @pyqtSlot(result=float)
    def steering2(self):  return steering2_sensor

    @pyqtSlot(result=float)
    def steering3(self):  return steering3_sensor

    @pyqtSlot(result=float)
    def steering4(self):  return round(steering4_sensor,0)

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

    @pyqtSlot(result = 'QVariantList')
    def k_propeller(self): return k_propeller


    @pyqtSlot(result = 'QVariantList')
    def tau_propeller(self): return tau_propeller


    @pyqtSlot(result=str)
    def est(self):  return str(est)

    @pyqtSlot(result=str)
    def steer_dir(self):  return str(steer_dir)
    
    @pyqtSlot(str)
    def heading_method_setting(self, method):
        global heading_method
        heading_method = method
        #print(heading_method)

    @pyqtSlot(str)
    def identification1(self, file):

        global k_propeller
        global tau_propeller
        global calib_param

        x = []
        y = []
        with open(file, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                x.append(float(row["x"]))
                y.append(float(row["y"]))

        x = np.array(x)
        y = np.array(y)

        K, tau = identification(x, y)

        print("K raw   :", K, type(K))
        print("tau raw :", tau, type(tau))

        # paksa menjadi float Python
        k_propeller[0] = float(K)
        tau_propeller[0] = float(tau)

        print(f"K   = {k_propeller}")
        print(f"tau = {tau_propeller}")

        calib_param["k_propeller"] = k_propeller
        calib_param["tau_propeller"] = tau_propeller

        with open("calib_param.json", "w") as f:
            json.dump(calib_param, f, indent=4)

    



    @pyqtSlot(int)
    def change_dir(self, cmd):
        change_dir_json(cmd)

    
        


    @pyqtSlot(str)
    def identification2(self, file):
        global k_propeller
        global tau_propeller
        global calib_param

        x = []
        y = []
        with open(file, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                x.append(float(row["x"]))
                y.append(float(row["y"]))

        x = np.array(x)
        y = np.array(y)

        K, tau = identification(x, y)

        print("K raw   :", K, type(K))
        print("tau raw :", tau, type(tau))

        # paksa menjadi float Python
        k_propeller[1] = float(K)
        tau_propeller[1] = float(tau)

        print(f"K   = {k_propeller}")
        print(f"tau = {tau_propeller}")

        calib_param["k_propeller"] = k_propeller
        calib_param["tau_propeller"] = tau_propeller

        with open("calib_param.json", "w") as f:
            json.dump(calib_param, f, indent=4)

    

    @pyqtSlot(str)
    def identification3(self, file):
        global k_propeller
        global tau_propeller
        global calib_param

        x = []
        y = []
        with open(file, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                x.append(float(row["x"]))
                y.append(float(row["y"]))

        x = np.array(x)
        y = np.array(y)

        K, tau = identification(x, y)

        print("K raw   :", K, type(K))
        print("tau raw :", tau, type(tau))

        # paksa menjadi float Python
        k_propeller[2] = float(K)
        tau_propeller[2] = float(tau)

        print(f"K   = {k_propeller}")
        print(f"tau = {tau_propeller}")

        calib_param["k_propeller"] = k_propeller
        calib_param["tau_propeller"] = tau_propeller

        with open("calib_param.json", "w") as f:
            json.dump(calib_param, f, indent=4)
        
    
    @pyqtSlot(str)
    def identification4(self, file):
        global k_propeller
        global tau_propeller
        global calib_param

        x = []
        y = []
        with open(file, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                x.append(float(row["x"]))
                y.append(float(row["y"]))

        x = np.array(x)
        y = np.array(y)

        K, tau = identification(x, y)

        print("K raw   :", K, type(K))
        print("tau raw :", tau, type(tau))

        # paksa menjadi float Python
        k_propeller[3] = float(K)
        tau_propeller[3] = float(tau)

        print(f"K   = {k_propeller}")
        print(f"tau = {tau_propeller}")

        calib_param["k_propeller"] = k_propeller
        calib_param["tau_propeller"] = tau_propeller

        with open("calib_param.json", "w") as f:
            json.dump(calib_param, f, indent=4)
    
    
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
                
    
    @pyqtSlot(float, float, result=float)
    def estimate_depth(self, lat, lon):
        global est
        
        nearest = find_two_nearest_points(lat, lon, self.depth_data)
        
        if nearest is None:
            #print("❌ Tidak ada titik sonar valid.")
            return -1.0  # ➤ kode khusus untuk 'no data'

        est = round(idw_from_two_points(lat, lon, nearest[0], nearest[1]) ,2)
        #print(f"✅ Kedalaman estimasi: {est} m")
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

    @pyqtSlot(result=str)
    def steer1(self):return str(steer1)

    @pyqtSlot(result=str)
    def steer2(self):return str(steer2)

    @pyqtSlot(result=str)
    def steer3(self):return str(steer3)

    @pyqtSlot(result=str)
    def steer4(self):return str(steer4)
    

    @pyqtSlot(str)
    def fsm_scheme(self, value):
        global fsm_scheme
        fsm_scheme = value
    

    
    
    
    @pyqtSlot('QString')
    def thrusterMode(self, value):
        global thruster_mode        
        thruster_mode =str(value)
        #print(thruster_mode)
        
    '''
    @pyqtSlot('QString')
    def user_control(self, value):
        global user_control
        user_control = value
        print(user_control)
    '''
    

    

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



    @pyqtSlot('int')
    def steering1_set(self, value):
        global steering1_set
        global calib_param
        steering1_set = value
        calib_param["steering1_offset"] =  int(steering1_set - steering1_raw)
        print(int(steering1_set - steering1_sensor))
        with open("calib_param.json", "w") as f:
            json.dump(calib_param, f, indent=4)

    @pyqtSlot('int')
    def steering2_set(self, value):
        global steering2_set
        global calib_param
        steering2_set = value
        calib_param["steering2_offset"] =  int(steering2_set - steering2_raw)
        with open("calib_param.json", "w") as f:
            json.dump(calib_param, f, indent=4)


    @pyqtSlot('int')
    def steering3_set(self, value):
        global steering3_set
        global calib_param
        steering3_set = value
        calib_param["steering3_offset"] =  int(steering3_set - steering3_raw)
        with open("calib_param.json", "w") as f:
            json.dump(calib_param, f, indent=4)

    @pyqtSlot('int')
    def steering4_set(self, value):
        global steering4_set
        global calib_param
        steering4_set = value
        calib_param["steering4_offset"] =  int(steering4_set - steering4_raw)
        with open("calib_param.json", "w") as f:
            json.dump(calib_param, f, indent=4)


    @pyqtSlot(str, str, str, str)
    def steering_min(self, val1, val2, val3, val4):
        global steering_raw_min

        data_baru = [val1, val2, val3, val4]

        for i, val in enumerate(data_baru):
            if val != "":
                steering_raw_min[i] = int(val)

        print("steering_raw_min", steering_raw_min)
        
        calib_param["steering_raw_min"] =  steering_raw_min
        with open("calib_param.json", "w") as f:
            json.dump(calib_param, f, indent=4)

    
    @pyqtSlot(str, str, str, str)
    def steering_max(self, val1, val2, val3, val4):
        global steering_raw_max

        data_baru = [val1, val2, val3, val4]

        for i, val in enumerate(data_baru):
            if val != "":
                steering_raw_max[i] = int(val)

        print("steering_raw_max", steering_raw_max)
        calib_param["steering_raw_max"] =  steering_raw_max
        with open("calib_param.json", "w") as f:
            json.dump(calib_param, f, indent=4)
    

#----------------------------------------------------------------#
    @pyqtSlot(str)
    def tick(self, value):
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
        global time
        
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
        global global_tug_points
        global global_tug2_points

        global latitude_tug
        global longitude_tug

        global latitude_tug2
        global longitude_tug2

        global heading_tug
        global heading_tug2
        global lat_chute, backend
        global steering1_offset, steering2_offset, steering3_offset, steering4_offset, steering1_sensor, steering2_sensor, steering3_sensor, steering4_sensor
        global calib_param
        global steer1, steer2, steer3, steer4, steer1_prev, steer2_prev, steer3_prev, steer4_prev 
        global steer1_error,steer2_error,steer3_error,steer4_error
        global steer1_error_prev,steer2_error_prev,steer3_error_prev,steer4_error_prev
        global steer_dir

        global central_status_prev, central_status

        with open("position.json", "r") as file:
            data = json.load(file)

        latitude_tug = float(data["tug1"]["latitude"])
        longitude_tug = float(data["tug1"]["longitude"])
        heading_tug = float(data["tug1"]["heading"])

        latitude_tug2 = float(data["tug2"]["latitude"])
        longitude_tug2 = float(data["tug2"]["longitude"])
        heading_tug2 = float(data["tug2"]["heading"])
        
        global_points = body_to_latlon(val_latitude , val_longitude, heading_magneto, barge_relative_points)        
        global_tug_points = body_to_latlon(latitude_tug , longitude_tug, heading_tug, tug_relative_points)
        global_tug2_points = body_to_latlon(latitude_tug2, longitude_tug2, heading_tug2, tug2_relative_points)

        lat_chute, long_chute = global_points["chute"]
        front_gps_time = time.time() - front_gps_time_prev
        if (front_gps_time < 5):
            front_gps_color = "green"
            
        else :
            front_gps_color = "red"
        

        with open("calib_param.json", "r") as f:
            calib_param = json.load(f)

        steering1_offset = int(calib_param["steering1_offset"])
        steering2_offset = int(calib_param["steering2_offset"])
        steering3_offset = int(calib_param["steering3_offset"])
        steering4_offset = int(calib_param["steering4_offset"])

        #map_angle_with_offset(nilai raw, nilai min, nilai max, target min, target max, offset)
        steering1_sensor =  map_angle_with_offset((steering1_raw),steering_raw_min[0], steering_raw_max[0], 0, 360, steering1_offset) 
        steering2_sensor =  map_angle_with_offset((steering2_raw),steering_raw_min[1], steering_raw_max[1], 0, 360, steering2_offset)
        steering3_sensor =  map_angle_with_offset((steering3_raw),steering_raw_min[2], steering_raw_max[2], 0, 360, steering3_offset) 
        steering4_sensor =  map_angle_with_offset((steering4_raw),steering_raw_min[3], steering_raw_max[3], 0, 360, steering4_offset)  



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

    
        
        control_prop = str(str("ṅ : ")+str(n_dot)+str("\nė : ")+str(e_dot)+str("\nψ_dot : ") + str(psi_dot)
                        +str("\nẋ : ")+str(x_dot)+ str("\nẏ : ")+str(y_dot) + str("\nn_error : ")+str(n_error)
                        + str("\ne_error : ")+str(e_error)+ str("\nx_error : ")+str(x_error)+ str("\ny_error : ")+str(y_error))


        
        if (central_status == "central"):
            steer1_error = shortest_psi(steering1_sensor, str1_target_buffer)
            if (abs(steer1_error) > 5):
                if (steer1_error > 0):
                    steer1 = "Kanan"
                else:
                    steer1 = "Kiri"
            else:
                steer1 = "Tahan"


            steer2_error = shortest_psi(steering2_sensor, str2_target_buffer)
            if (abs(steer2_error) > 5):
                if (steer2_error > 0):
                    steer2 = "Kanan"
                else:
                    steer2 = "Kiri"
            else:
                steer2 = "Tahan"

            steer3_error = shortest_psi(steering3_sensor, str3_target_buffer)
            if (abs(steer3_error) > 5):
                if (steer3_error > 0):
                    steer3 = "Kanan"
                else:
                    steer3 = "Kiri"
            else:
                steer3 = "Tahan"

            steer4_error = shortest_psi(steering4_sensor, str4_target_buffer)
            if (abs(steer4_error) > 5):
                if (steer4_error > 0):
                    steer4 = "Kanan"
                else:
                    steer4 = "Kiri"
            else:
                steer4 = "Tahan"

            

        if (steer1 != steer1_prev):
            client.publish("Steering_1", str(dir_check(steer1, steer_dir[0])))

        if (steer2 != steer2_prev):
            client.publish("Steering_2", str(dir_check(steer2, steer_dir[1])))
        
        if (steer3 != steer3_prev):
            client.publish("Steering_3", str(dir_check(steer3, steer_dir[2])))
        
        if (steer4 != steer4_prev):
            client.publish("Steering_4", str(dir_check(steer4, steer_dir[3])))

        steer1_prev = steer1
        steer2_prev = steer2
        steer3_prev = steer3
        steer4_prev = steer4

        if (central_status_prev != central_status):
            if (central_status == "local"):
                steer1 = "Tahan"
                steer2 = "Tahan"
                steer3 = "Tahan"
                steer4 = "Tahan"

        central_status_prev = central_status


        
        
        

        mqtt_message_time = time.time() - mqtt_message_time_prev
        
        if (mqtt_message_time > 1):  
            
            heading_speed =(0.8 * heading_speed) + (0.2 *shortest_psi(heading,heading_prev)/0.2)
            
            str1_target = str1_target_buffer
            str2_target = str2_target_buffer
            str3_target = str3_target_buffer
            str4_target = str4_target_buffer
            
            ###################### Miniatur DPS #######################################

            client.publish("steer1_command", str(str1_target))
            client.publish("steer2_command", str(str2_target))
            client.publish("steer3_command", str(str3_target))
            client.publish("steer4_command", str(str4_target))

            client.publish("steering1_calibrated", str(steering1_sensor))
            client.publish("steering2_calibrated", str(steering2_sensor))
            client.publish("steering3_calibrated", str(steering3_sensor))
            client.publish("steering4_calibrated", str(steering4_sensor))


            #client.publish("user_control", str(user_control))
            client.publish("yaw_barge", str(heading_magneto))
            mqtt_message_time_prev = time.time()


        csv_message_time = time.time() - csv_message_time_prev

        if (csv_message_time > 2):
            data_row = [
                val_latitude, val_longitude,
                round(propeller_speed1, 0), round(propeller_speed2, 0), round(propeller_speed3, 0), round(propeller_speed4, 0),
                round(str1_target, 0), round(str2_target, 0), round(str3_target, 0), round(str4_target, 0),
                heading, heading_target, navigation_mode_text,
                position_error, dir_error, payout, lat_chute, long_chute
            ]
            log_to_csv(data_row)
            date = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            new_barge = {
                "latitude": str(val_latitude),
                "longitude": str(val_longitude),
                "heading": str(heading_magneto),
                "payout": str(payout),
                "received_time": str(date)
            }
            # baca file
            with open("position.json", "r") as f:
                data = json.load(f)

            # replace data barge
            data["barge"] = new_barge

            # simpan kembali
            with open("position.json", "w") as f:
                json.dump(data, f, indent=4)

            with open("calib_param.json", "r") as f:
                calib_param = json.load(f)

            steer_dir = (calib_param["steer_dir"])

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


    if (t == "central_status"):
        global central_status
        central_status = msg
        #print(central_status)
        
        
    if (t == "payout"):
        global payout
        payout = float(msg) 
        

    if (t == "steering1_sensor"):
        global steering1_sensor
        global steering1_raw
        global steering1_offset
        global spc_message_time_prev
        spc_message_time_prev = time.time()
        steering1_raw = (float(msg))
        
        
        

    if (t == "steering2_sensor"):
        global steering2_sensor
        global steering2_raw
        global steering2_offset
        global gyro_message_time_prev
        steering2_raw = float(msg)
        
        gyro_message_time_prev = time.time()

    if (t == "steering3_sensor"):
        global steering3_sensor
        global steering3_raw
        global steering3_offset
        steering3_raw = float(msg)
        

    if (t == "steering4_sensor"):
        global steering4_sensor
        global steering4_raw
        global steering4_offset
        steering4_raw = float(msg)
        

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



    if (t == "lat_nmea"): #GPS/lat or lat_nmea
        global gps_time_prev
        global val_latitude
        gps_time_prev = time.time()
        
        val_latitude = float(msg)
    

    
    if (t == "long_nmea"): #GPS/lat or lat_nmea

        global val_longitude        
        val_longitude = float(msg)

        
        
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

        value = float(msg)
        
        heading_magneto = int(value)

            
            
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

      
    if (t == 'rpm_propeller1'):
        global rpm1
        
        rpm1 = (float(msg) * 60 * (rpm_filter[0])) + (rpm1 * (1 - rpm_filter[0]))
            
    if (t == 'rpm_propeller2'):
        global rpm2
        rpm2 = (float(msg) * 60 * (rpm_filter[1])) + (rpm2 * (1 - rpm_filter[1]))
            
    if (t == 'rpm_propeller3'):
        global rpm3
        rpm3 = (float(msg) * 60 * (rpm_filter[2])) + (rpm3 * (1 - rpm_filter[2]))
            
    if (t == 'rpm_propeller4'):
        global rpm4
        rpm4 = (float(msg) * 60 * (rpm_filter[3])) + (rpm4 * (1 - rpm_filter[3]))
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

    
    
    if(t=='steer1_req'):
        global str1_target_buffer
        if (user_control == "manual"):
            str1_target_buffer = int(msg)
            #print(msg)
    
    if(t=='steer2_req'):
        global str2_target_buffer
        if (user_control == "manual"):
            str2_target_buffer = int(msg)
        
    
    if(t=='steer3_req'):
        global str3_target_buffer
        if (user_control == "manual"):
            str3_target_buffer = int(msg)
        
    if(t=='steer4_req'):
        global str4_target_buffer
        if (user_control == "manual"):
            str4_target_buffer = int(msg)

    if(t=='Steering_1_joystick'):
        global steer1
        steer1 = msg
        


    if(t=='Steering_2_joystick'):
        global steer2
        steer2 = msg
        

    if(t=='Steering_3_joystick'):
        global steer3
        steer3 = msg
        

    if(t=='Steering_4_joystick'):
        global steer4
        steer4 = msg
      
    
        
    




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

    client.subscribe("central_status")
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

    client.subscribe("Steering_1_joystick")
    client.subscribe("Steering_2_joystick")
    client.subscribe("Steering_3_joystick")
    client.subscribe("Steering_4_joystick")


    client.subscribe("SPC1")
    client.subscribe("SPC2")
    client.subscribe("SPC3")
    client.subscribe("SPC4")
    
    client.subscribe("rpm_propeller1")
    client.subscribe("rpm_propeller2")
    client.subscribe("rpm_propeller3")
    client.subscribe("rpm_propeller4")

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
    
    
    client.subscribe("pitch_pontoon")
    client.subscribe("roll_pontoon")
    
    client.subscribe("payout")
    
    client.publish("MainControl", "active")#publish
    client.publish("dummyval", str(0))
    

    main = table()
    
    
#----------------------------------------------------------------#
