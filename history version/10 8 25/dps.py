######  PROGRAM MEMANGGIL WINDOWS PYQT5 ##########################

####### memanggil library PyQt5 ##################################
#----------------------------------------------------------------#
from PyQt5.QtCore import * 
from PyQt5.QtGui import * 
from PyQt5.QtQml import * 
from PyQt5.QtWidgets import *
from PyQt5.QtQuick import *  
import sys
import time
import datetime as dt
import numpy as np
from math import sqrt

intersection_points = []
lines_with_intersection = []

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


#import threading
#import multiprocessing
import math
from math import sin, cos, sqrt, atan2, radians, atan
#----------------------------------------------------------------#
from PyQt5.QtPositioning import QGeoCoordinate
from collections import defaultdict

import paho.mqtt.client as paho
import numpy as np
import csv
import threading
import PyCVQML
import json

#################Joystick
import pygame
pygame.init()

from math import sqrt


def geo_to_dict(coord):
    return {
        "latitude": coord.latitude(),
        "longitude": coord.longitude()
    }

def load_depth_points_from_isobath(file_path="isobath.csv"):
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

    with open("isobath.csv", newline='') as csvfile:
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





rpl1_lat = [-7.743054, -7.743341, -7.743599, -7.743935, -7.744127, -7.744533, -7.744788, -7.745312, -7.745313, -7.7453136, -7.7453158, -7.745431, -7.745431]
rpl1_long = [108.998836, 108.998279, 108.997778, 108.997194, 108.996812, 108.995823, 108.995203, 108.993881, 108.993879, 108.9938775, 108.9938747, 108.9938639, 108.9931222]
names = ["L1 WP1", "L1 WP2", "L1 WP3", "L1 WP4", "L1 WP5", "L1 WP6", "L1 WP7", "L1 WP8", "L1 WP9", "L1 WP10", "L1 WP11", "L1 WP12", "L1 WP13"]

colors = ["red", "orange", "navy", "navy", "navy", "navy", "orange", "orange", "red", "red", "red", "red", "red"]

rpl2_lat = [-7.743055, -7.743775, -7.744123, -7.744329, -7.744441, -7.744598, -7.744754, -7.744933, -7.744985, -7.745072, -7.745401, -7.745446, -7.745456]
rpl2_long = [108.998837, 108.997869, 108.997261, 108.996855, 108.996634, 108.996303, 108.995905, 108.995424, 108.995217, 108.994877, 108.993900, 108.993432, 108.993341]
names2 = ["L2 WP1", "L2 WP2", "L2 WP3", "L2 WP4", "L2 WP5", "L2 WP6", "L2 WP7", "L2 WP8", "L2 WP9", "L2 WP10", "L2 WP11", "L2 WP12", "L2 WP13"]
colors2 = ["red", "navy", "navy", "navy", "navy", "navy", "navy", "navy", "navy", "orange", "red", "red", "red"]


points = [
    {"latitude": lat, "longitude": lon, "name": name, "color": color}
    for lat, lon, name, color in zip(rpl1_lat, rpl1_long, names, colors)
]

points2 = [
    {"latitude": lat, "longitude": lon, "name": name, "color": color}
    for lat, lon, name, color in zip(rpl2_lat, rpl2_long, names2, colors2)
]


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


latitude_integer = -7
latitude_fractional = -0.745447

longitude_integer = 108
longitude_fractional = 0.993432



val_latitude =  -7.745447 #centre
filtered_val_latitude = val_latitude#centre
val_longitude = 108.993432   #centre
filtered_val_longitude = filtered_val_latitude  #centre

latitude_prev = val_latitude
longitude_prev = val_longitude

latitude_target = -0.33026899613145305
longitude_target = 104.60042691242732

speed_measurement_time = 0
speed_measurement_time_prev = 0

latitude = ""
longitude = ""

heading = 0
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





gps_type = 0


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


central_status = ""

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
'''



xg = 0.5 #posisi x center of gravity
yg = 0.4 #posisi y center of gravity
m = 27 #massa kapal
r = 0 #posisi arah surge / kecepatan sudut (psi_dot)
Iz = 0 #momen inersia akibat percepatan sumbu y

x_u = 0.9
y_v = 0.6
n_r = 0.3

x_udot = 0.9
y_vdot = 0.6
y_rdot = 0.7
n_vdot = 0.3
n_rdot = 0.4

v = float(y_dot)
u = float(x_dot)

#gaya akibat massa
M = np.array([[m, 0, -m*yg], [0, m, m*xg], [-m*yg, m*xg, Iz]])
+ np.array([[-x_udot,0,0],[0,-y_vdot,-y_rdot],[0,-n_vdot,-n_rdot]])
print(M)

#gaya akibat coriolis
C = np.array([ [0, 0, -m * (xg*r + float(y_dot))],
               [0, 0, -m * (yg*r + float(x_dot))],
               [-m * (xg*r + float(y_dot)),-m * (yg*r + float(x_dot)), 0]]) + np.array([[0,0,-y_vdot*float(y_dot) - ((y_rdot+n_vdot)/2)*r],
            [0,0,x_udot*float(x_dot)],
            [-y_vdot*float(y_dot) - ((y_rdot+n_vdot)/2)*r,x_udot*float(x_dot),0]])

print("C: ")
print(C)


 #gaya akibat drag
D = np.array([[x_u,0,0],
    [0,y_v,0],
    [0,0,n_r]]) + np.array([[x_u*abs(u),0,0],
    [0,y_v*abs(v),0],
    [0,0,n_r*abs(r)]])

print(D)


'''


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


#dari thesis teguh
'''
m = np.array([[mass, 0, -mass*yg], [0, mass, mass*xg], [-mass*yg, mass*xg, Iz]])
+ np.array([[-x_udot,0,0],[0,-y_vdot,-y_rdot],[0,-n_vdot,-n_rdot]])
print(m)
'''
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



control_prop = ""
waktu = dt.datetime.now()
filename = str("DP Experimental RECORD " ) + str(current_time.day)+str("-")+str(current_time.month)+str("-")+str(current_time.year) + str(".csv")
with open(filename, 'a') as csvfile:
    csvwriter = csv.writer(csvfile)
    rows = [ [str("date"),str("val latitude"), str("val longitude"), str("propeller speed1"), str("propeller speed2"), str("propeller speed3"), str("propeller speed4"), str("str1 target"), str("str2 target"), str("str3 target"), str("str4 target"), str("heading")
              ,str("heading target"),str("mode") ]]
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



########## mengisi class table dengan instruksi pyqt5#############
#----------------------------------------------------------------#
class table(QObject):    
    def __init__(self, parent = None):
        super().__init__(parent)
        self.app = QApplication(sys.argv)
        self.engine = QQmlApplicationEngine(self)
        # Load sonar data
        self.depth_data = load_depth_points_from_isobath("isobath.csv")
        print("✅ Titik sonar terload:", len(self.depth_data))

        polygons = load_polygons()

        self.engine.rootContext().setContextProperty("allPolygons", polygons)
        self.engine.rootContext().setContextProperty("backend", self)    
        self.engine.load(QUrl("dps.qml"))
        sys.exit(self.app.exec_())

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
    
    @pyqtSlot(float)
    def estimate_rpl(self, line):
        global y_est
        global rpl_long_calc
        global rpl_lat_calc
        
        global rpl_lat
        global rpl_long
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
        #print(f"📍 Estimasi kedalaman di: ({lat}, {lon})")
        nearest = find_two_nearest_points(lat, lon, self.depth_data)
        
        if nearest is None:
            #print("❌ Tidak ada titik sonar valid.")
            return -1.0  # ➤ kode khusus untuk 'no data'

        est = round(idw_from_two_points(lat, lon, nearest[0], nearest[1]) ,2)
        #print(f"✅ Kedalaman estimasi: {est} m")
        return est

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


    '''
    @pyqtSlot(result=int)
    def heading_target(self):return heading_target
    '''

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
                          str(val_longitude),]]                
                csvwriter.writerows(rows)


    @pyqtSlot(int, int,float)
    def fsm_gain(self, row, coloum, val):
        global x_gain
        global y_gain
        global yaw_negative_gain
        global yaw_positive_gain
        
        print(row, coloum, val)
        if (coloum == 0):
            x_gain[0][row] = float(val)
            print("x_gain : ", x_gain)

        if (coloum == 1):
            y_gain[0][row] = float(val)
            print("y_gain :", y_gain)

        if (coloum == 2):
            yaw_positive_gain[0][row] = float(val)
            print("yaw_positive_gain :",yaw_positive_gain)

        if (coloum == 3):
            yaw_negative_gain[0][row] = float(val)
            print("yaw_negative_gain:",yaw_negative_gain)

        

        
        # Buat dictionary
        fsm_gain = {
            "x_gain": x_gain,
            "y_gain": y_gain,
            "yaw_positive_gain": yaw_positive_gain,
            "yaw_negative_gain": yaw_negative_gain
        }

        # Simpan ke file JSON
        with open("fsm_gain.json", 'w') as f:
            json.dump(fsm_gain, f, indent=4)  # indent biar rapi


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

        #print(steering1_sensor)



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
        x_dot = round(float(v[0]),1)
        y_dot = round(float(v[1]),1)


        error_body_fixed = np.linalg.inv(j_theta) @ np.array([[n_error],[e_error],[psi_error]])
        x_error = abs(round(float(error_body_fixed[0]),1))
        y_error = abs(round(float(error_body_fixed[1]),1))
        
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

        # Menyimpan ke dalam file JSON
        file_path = 'state_space.json'
        with open(file_path, 'w') as f:
            json.dump(state_space, f)
        

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
        propeller_speed1_buffer = constrain(propeller_speed1_buffer, 0, 100)
        propeller_speed2_buffer = constrain(propeller_speed2_buffer, 0, 100)
        propeller_speed3_buffer = constrain(propeller_speed3_buffer, 0, 100)
        propeller_speed4_buffer = constrain(propeller_speed4_buffer, 0, 100)
        '''

        #codingan otomatis
        
        
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
                '''
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
                        
                    
                '''
                    
                
                
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


        
        control_prop = str(str("ṅ : ")+str(n_dot)+str("\nė : ")+str(e_dot)+str("\nψ_dot : ") + str(psi_dot)
                        +str("\nẋ : ")+str(x_dot)+ str("\nẏ : ")+str(y_dot) + str("\nn_error : ")+str(n_error)
                        + str("\ne_error : ")+str(e_error)+ str("\nx_error : ")+str(x_error)+ str("\ny_error : ")+str(y_error))


        mqtt_message_time = time.time() - mqtt_message_time_prev
        
        if (mqtt_message_time > 0.2):  
            
            heading_speed =(0.8 * heading_speed) + (0.2 *shortest_psi(heading,heading_prev)/0.2)
            
            str1_target = str1_target_buffer
            str2_target = str2_target_buffer
            str3_target = str3_target_buffer
            str4_target = str4_target_buffer
            
            ###################### Miniatur DPS #######################################
            #print(propeller_speed1_buffer)
            client.publish("propeller1", str(propeller_speed1_buffer))
            

            client.publish("propeller2", str(propeller_speed2_buffer))
            

            client.publish("propeller3", str(propeller_speed3_buffer))
            

            client.publish("propeller4", str(propeller_speed4_buffer))
            
            

            client.publish("steer1_command", str(str1_target))
            client.publish("steer2_command", str(str2_target))
            client.publish("steer3_command", str(str3_target))
            client.publish("steer4_command", str(str4_target))

            client.publish("user_control", str(user_control))
            
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
                              str(heading), str(heading_target), str(navigation_mode_text), str(position_error), str(dir_error)]]
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

    if (t == "steering1_sensor"):
        global steering1_sensor
        global spc_message_time_prev
        spc_message_time_prev = time.time()
        steering1_sensor = float(msg)
        #print(steering1_sensor)
        

    if (t == "steering2_sensor"):
        global steering2_sensor
        steering2_sensor = float(msg)

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
 
    if (t == "yaw_actual"):
        global heading
        try:
            value = float(msg)
            heading = int(value)  # default jika tidak masuk range manapun

            if 212 < value < 273:
                heading = map_value(value, 212, 273, 90, 0)
            elif 106 < value < 212:
                heading = map_value(value, 106, 212, 180, 90)
            elif 17 < value < 106:
                heading = map_value(value, 17, 106, 270, 180)
            elif 0 <= value <= 17:
                heading = map_value(value, 0, 17, 290, 270)
            elif 273 < value < 360:
                heading = map_value(value, 273, 360, 360, 290)

            heading = int(heading)

        except (TypeError, ValueError):
            print(f"Invalid heading value: {msg}")
            heading = 0  # atau nilai default lain sesuai kebutuhan
        '''
        global heading
        try:
            heading = int(msg)
            
            if (float(msg) > 212 and float(msg) < 273):
                heading = map_value(float(msg), 212, 273, 90,0)
                
            if (float(msg) > 106 and float(msg) < 212):
                heading = map_value(float(msg), 106, 212, 180, 90)
                
            if (float(msg) > 17 and float(msg) < 106):
                heading = map_value(float(msg), 17, 106, 270, 180)
               
            if (float(msg) > 0 and float(msg) < 17):
                heading = map_value(float(msg), 0, 17, 290, 270)
            
            if (float(msg) > 273 and float(msg) < 360):
                heading = map_value(float(msg), 273, 360, 360, 290)
            
        except:
            pass
        #print(heading)
        '''

    if (t == "winddirect"):
        global Wdirect
        Wdirect = map_angle_with_offset((float(msg)),0, 360, 0, 360, 0) 

    if (t == "windspeed"):
        global Wspeed
        Wspeed = round(float(msg)/10,1)

    if (t == "roll_pontoon"):
        global pitch
        global gyro_message_time_prev

        pitch = float(msg)


        gyro_message_time_prev = time.time()

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


    if(t=='Set_Speed1'):
        global propeller_speed1_buffer
        if (joystick_mode == 2):
            propeller_speed1_buffer = int(msg)
            #print(propeller_speed1_buffer)

    if(t=='Set_Speed2'):
        global propeller_speed2_buffer
        if (joystick_mode == 2):
            propeller_speed2_buffer = int(msg)

    if(t=='Set_Speed3'):
        global propeller_speed3_buffer
        if (joystick_mode == 2):
            propeller_speed3_buffer = int(msg)

    if(t=='Set_Speed4'):
        global propeller_speed4_buffer
        if (joystick_mode == 2):
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
        
    




def pygame_run(num):
    global drive_mode
    global drive_mode_count
    global heading_target
    global heading_target_status


    global analog1_x
    global analog1_y
    global analog1_x_prev
    global analog1_y_prev

    global analog2_x
    global analog2_y
    global analog2_x_prev
    global analog2_y_prev
    
    global hat
    global hat_prev
    
    global up_color
    global down_color
    global left_color
    global right_color
    
    global button1_color
    global button2_color
    global button3_color
    global button4_color
    
    
    global button_L1_color
    global button_L2_color
    global button_R1_color
    global button_R2_color
    
    global analog1_color
    global analog2_color
    global navigation
    global control_direction_send

    global analog1_angle
    global control_direction
    global control_direction_send1
    global control_direction_send2
    global control_direction_send3
    global control_direction_send4
    global propeller_speed
    global speed_button
    global propeller_mode


    global propeller_switch

    global propeller_speed1_buffer 
    global propeller_speed2_buffer 
    global propeller_speed3_buffer 
    global propeller_speed4_buffer 

    global navigation_mode

    global str1_target_buffer
    global str2_target_buffer
    global str3_target_buffer
    global str4_target_buffer

    global navigation_mode_text

    global analog_lock
    global control_style

    global power
    global power_set

    
    global select1
    global select2
    global select3
    global select4

    global sway_dir

    global joystick1_status

    global joystick_mode
    global fsm_scheme
    

    clock = pygame.time.Clock()
    joysticks = {}
    done = False
    
    while not done:

        # Event processing step.
        # Possible joystick events: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
        # JOYBUTTONUP, JOYHATMOTION, JOYDEVICEADDED, JOYDEVICEREMOVED
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True  # Flag that we are done so we exit this loop.

            if event.type == pygame.JOYBUTTONDOWN and joystick_mode == 1:
                #print("Joystick button pressed.")
                status_button = "pressed"
                joy_button_status = status_button
                joy_button_event = event.button
                print(status_button, joy_button_event)
                
                if (joy_button_event == 0):
                    button1_color = "#d84860"
                    speed_button = 1
                    print("up")
                    
                    
                if (joy_button_event == 1):
                    button2_color = "#d84860"
                    drive_mode_count = drive_mode_count - 1
                    if drive_mode_count == -2:
                        drive_mode_count = 0

                    
                    
                if (joy_button_event == 2):
                    button3_color = "#d84860"
                    speed_button = -1
                   
                    
                if (joy_button_event == 3):
                    button4_color = "#d84860"
                    drive_mode_count = drive_mode_count + 1
                    
                    if drive_mode_count ==2:
                        drive_mode_count = 0
         
                
                if (joy_button_event == 4):
                    button_L1_color = "#d84860"
                    
                    select4 = not(select4)
                    if (select4 == True):
                        propeller_mode = 0
                    if (select4 == False) :
                        propeller_mode = 4
                        select1 = True
                        select3 = True
                        select2 = True

                if (joy_button_event == 5):
                    button_R1_color = "#d84860"

                    select1 = not(select1)
                    if (select1 == True):
                        propeller_mode = 0
                    if (select1 == False) :
                        propeller_mode = 1
                        select4 = True
                        select3 = True
                        select2 = True
                    
                    
                if (joy_button_event == 6):
                    button_L2_color = "#d84860"

                    select3 = not(select3)
                    if (select3 == True):
                        propeller_mode = 0
                    if (select3 == False) :
                        propeller_mode = 3
                        select4 = True
                        select1 = True
                        select2 = True
                    
                
                if (joy_button_event == 7):
                    button_R2_color = "#d84860"
                    
                    select2 = not(select2)
                    if (select2 == True):
                        propeller_mode = 0
                    if (select2 == False) :
                        propeller_mode = 2
                        select4 = True
                        select3 = True
                        select1 = True
                    
                    

                if (joy_button_event == 8):
                    navigation_mode = navigation_mode + 1
                    
                    #rpl_lat = rpl_lat[1:]
                    #rpl_long = rpl_long[1:]
                    #navigation_mode_text = "free"
                    if (navigation_mode == 0):
                        navigation_mode_text = "forward"
                        str1_target_buffer = -90
                        str2_target_buffer = -90
                        str3_target_buffer = 0
                        str4_target_buffer = 0
                    
                    if (navigation_mode == 1):
                        navigation_mode_text = "sway"
                        str1_target_buffer = -90
                        str2_target_buffer = -90
                        str3_target_buffer = 90
                        str4_target_buffer = 90
                        

                    if (navigation_mode == 2):
                        navigation_mode = 0
                        navigation_mode_text = "forward"
                        

                if (joy_button_event == 9):
                    print("starts")
                    if (propeller_switch == 0):
                        propeller_switch = 1
                        break

                    if (propeller_switch == 1):
                        propeller_switch = 0
                        break
                    
                    
                if (joy_button_event == 10):
                    
                    #print(propeller_switch, propeller_mode)
                    if (propeller_switch == 1 and propeller_mode == 0):
                        if (control_style == "individual"):
                            control_style = "central"
                            #print(control_style)
                            break
                        
                        if (control_style == "central"):
                            control_style = "individual"
                            #print(control_style)
                            break
                        
                    
                if (joy_button_event == 11):
                    analog2_color = "#d84860"
                    power = 0
                    propeller_speed1_buffer = 0
                    propeller_speed2_buffer = 0
                    propeller_speed3_buffer = 0
                    propeller_speed4_buffer = 0

                if event.button == 0:
                    joystick = joysticks[event.instance_id]
                
            if event.type == pygame.JOYBUTTONUP and joystick_mode == 1:
                #print("Joystick button released.")
                joy_button_status = status_button
                joy_button_event = event.button
                
                if (joy_button_event == 0):
                    button1_color = "#122e55"
                    speed_button = 0
                    
                if (joy_button_event == 1):
                    button2_color = "#122e55"
                    
                if (joy_button_event == 2):
                    button3_color = "#122e55"
                    print("zeroing")
                    speed_button = 0
                    
                if (joy_button_event == 3):
                    button4_color = "#122e55"
                    
                if (joy_button_event == 4):
                    button_L1_color = "#122e55"
                    
                if (joy_button_event == 5):
                    button_R1_color = "#122e55"
                    
                    
                if (joy_button_event == 6):
                    button_L2_color = "#122e55"
                
                if (joy_button_event == 7):
                    button_R2_color = "#122e55"
                   
                if (joy_button_event == 10):
                    analog1_color = "#122e55"
                    
                if (joy_button_event == 11):
                    analog2_color = "#122e55"

                
                
            #print(drive_mode_count)
            if (drive_mode_count == -1 and joystick_mode == 1 ):
                drive_mode = "line route"

            if (drive_mode_count == 0 and joystick_mode == 1):
                drive_mode = "no route"

            if (drive_mode_count == 1 and joystick_mode == 1):
                drive_mode = "station keeping" 

            # Handle hotplugging
            if event.type == pygame.JOYDEVICEADDED:
                # This event will be generated when the program starts for every
                # joystick, filling up the list without needing to create them manually.
                joy = pygame.joystick.Joystick(event.device_index)
                joysticks[joy.get_instance_id()] = joy
                print("Joystick {} connected".format(joy.get_instance_id()))
                joystick1_status = "on"
                

            if event.type == pygame.JOYDEVICEREMOVED:
                del joysticks[event.instance_id]
                print("Joystick {} disconnected".format(event.instance_id))
                joystick1_status = "off"

       
            
        # For each joystick:
        for joystick in joysticks.values():
                
            jid = joystick.get_instance_id()
            name = joystick.get_name()
            guid = joystick.get_guid()
            power_level = joystick.get_power_level()
            axes = joystick.get_numaxes()
            

            for i in range(axes):
                axis = joystick.get_axis(i)
                if i == 0 :
                    analog1_x = axis
                if i == 1 :
                    analog1_y = axis
                if i == 2 :
                    analog2_y = axis
                if i == 3 :
                    analog2_x = axis
                    #print(axis)
                
                a =+ 1
            
            
            
            buttons = joystick.get_numbuttons()
            

            for i in range(buttons):
                button = joystick.get_button(i)
                
            hats = joystick.get_numhats()
            
            
            
            for i in range(hats):
                hat = joystick.get_hat(i)
            
        if (hat != hat_prev and joystick_mode == 1):    
            #print(hat[1])
            if (hat[0] == -1):
                left_color = "#d84860"
                right_color = "#122e55"
                heading_target_status = -1
                if(navigation_mode_text == "sway"):
                    sway_dir = "left"
                
                
                
            if (hat[0] == 0):
                left_color = "#122e55"
                right_color = "#122e55"
                heading_target_status = 0
                
                
            if (hat[0] == 1):
                left_color = "#122e55"
                right_color = "#d84860"
                heading_target_status = 1
                if(navigation_mode_text == "sway"):
                    sway_dir = "right"
                
                
  
            if (hat[1] == -1):
                down_color = "#d84860"
                up_color = "#122e55"
                power_set = -1
                
            if (hat[1] == 0):
                down_color = "#122e55"
                up_color = "#122e55"
                power_set = 0
                
                
            if (hat[1] == 1):
                down_color = "#122e55"
                up_color = "#d84860"
                power_set = 1
                
        hat_prev = hat
        
        
        
        


        if (abs(analog1_x) > 0.002 or abs(analog1_y > 0.002)):
            analog1_angle = degree_conversion(analog1_y, analog1_x)
            if (length_conversion(analog1_y, analog1_x) > 0.2):
                control_direction = analog1_angle    
            if (analog1_angle > 0):
                
                control_direction = 180-analog1_angle 
                
                 
            if (analog1_angle < 0):

                control_direction = -1*(analog1_angle + 180)
                
                
                
        if (analog1_angle == 180):
            control_direction = 0
        if (analog1_angle == 0):
            control_direction = 180

        if (control_direction < 0):
            control_direction_send = 50 #180 - control_direction 

        if (control_direction > 0):
            control_direction_send = 100#control_direction
        
        #print(round(analog1_angle,1),round(control_direction_send,1))
                
            
        
        #propeller_speed = length_conversion(analog1_x, analog1_y)
        #
        #print(analog1_x, analog1_y, control_direction)
        #print(control_direction)
        
        analog1_x_prev = analog1_x
        analog1_y_prev = analog1_y
        analog2_x_prev = analog2_x
        analog2_y_prev = analog2_y

        clock.tick(30)



########## memanggil class table di mainloop######################
#----------------------------------------------------------------#    
if __name__ == "__main__":
    PyCVQML.registerTypes()
    
    t1 = threading.Thread(target=pygame_run, args=(10,))
    t1.start()
    
    ##Mosquitto Mqtt Configuration
    client= paho.Client("DPS_GUI")
    client.on_message=on_message

    print("connecting to broker ",broker)
    client.connect(broker,port)#connect
    print(broker," connected")
    
    client.loop_start()
    print("Subscribing")


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


    client.subscribe("speed_nmea")
    client.subscribe("yaw")
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
    
        
    client.publish("MainControl", "active")#publish
    client.publish("dummyval", str(0))
    

    

    main = table()
    
    
#----------------------------------------------------------------#