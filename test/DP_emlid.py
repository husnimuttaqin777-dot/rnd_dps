#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import sys
import csv
import datetime as dt

import math
from math import sin, cos, sqrt, atan2, radians
import random  

from math import pow
phi = math.pi
from PyQt5.QtCore import QUrl, QObject, pyqtSignal, pyqtSlot, QTimer, pyqtProperty
from PyQt5.QtGui import QGuiApplication, QIcon
from PyQt5.QtQuick import QQuickView
from PyQt5.QtQml import QQmlApplicationEngine
import threading 

'''
from PyQt5.QtWidgets import QApplication, QCheckBox, QGridLayout, QGroupBox
from PyQt5.QtWidgets import QMenu, QPushButton, QRadioButton, QVBoxLayout, QWidget, QSlider
'''

import paho.mqtt.client as paho
import utm
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


SP1 = 0
SP2 = 0
SP3 = 0
SP4 = 0

rpm1 = 0
rpm2 = 0
rpm3 = 0
rpm4 = 0

target_lat =0
target_long = 0
error_long =0
error_lat = 0

distance = 0

Wspeed=0
Wdirect=0

val_latitude = -0.33026899613145305   #centre
filtered_val_latitude = -0.33026899613145305  #centre
val_longitude = 104.60042691242732  #centre
filtered_val_longitude = 104.60042691242732  #centre

latitude_prev = -0.33026899613145305
longitude_prev = 104.60042691242732

speed_measurement_time = 0
speed_measurement_time_prev = 0
#val_latitude = -0.5932511  #centre
#val_longtitude = 123.8159180  #centre



Lat_G = -0.5942511
Lon_G = 123.8169180
heading = 0
heading_error = 0
heading_target = 0

get_lat_GUI = 0
get_lon_GUI = 0
get_lat_GUI1 = 0
get_lon_GUI1 = 0
get_lat_GUI_last = 0
get_lon_GUI_last = 0
counter_distance_mea = 0
dst_bw_line = 0

station_keeping_state = 0
autopilot_state = 0


delta_lat = 0
delta_lat = 0

heading_Grep = 0
distance_Grap=0
distance_Grap_m = 0
heading_G = 0


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
dir_error = 0

control_style = ""

filtered_psi_error = 0
x_error_body_fixed = 0
y_error_body_fixed = 0

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

spc_indicator_color = "red"

speed_ship = 0


gps_time = 0
gps_time_prev = 0

gps_status_color = "red"

track_time = 0
track_time_prev = 0

flow_lpm = 0
flow_lpm2 = 0

class MQTTValue(QQuickView):
    #print(thruster1_speed_target) 
    def __init__(self):
        super(MQTTValue,self).__init__()
        self.setSource(QUrl('main.qml'))
   

    @pyqtSlot(result=float)
    def Set_Speed1(self):  return thruster1_command
            
    @pyqtSlot(result=float)
    def Set_Speed2(self):  return thruster2_command

    @pyqtSlot(result=float)
    def Set_Speed3(self):  return thruster3_command

    @pyqtSlot(result=float)
    def Set_Speed4(self):  return thruster4_command

    @pyqtSlot(result=float)
    def engineconect1(self):  return EC1

    @pyqtSlot(result=float)
    def engineconect2(self):  return EC2

    @pyqtSlot(result=float)
    def engineconect3(self):  return EC3

    @pyqtSlot(result=float)
    def engineconect4(self):  return EC4
    
    @pyqtSlot(result=float)
    def rpm1(self): return rpm1
    
    @pyqtSlot(result=float)
    def rpm2(self): return rpm2
    
    @pyqtSlot(result=float)
    def rpm3(self): return rpm3
    
    @pyqtSlot(result=float)
    def rpm4(self): return rpm4

    @pyqtSlot(result=float)
    def steering1(self):  return str1

    @pyqtSlot(result=float)
    def steering2(self):  return str2

    @pyqtSlot(result=float)
    def steering3(self):  return str3

    @pyqtSlot(result=float)
    def steering4(self):  return str4
    
    
    
    @pyqtSlot(result=float)
    def steering1_target(self):  return str1_target

    @pyqtSlot(result=float)
    def steering2_target(self):  return str2_target

    @pyqtSlot(result=float)
    def steering3_target(self):  return str3_target

    @pyqtSlot(result=float)
    def steering4_target(self):  return str4_target


    @pyqtSlot(result=float)
    def mesin1(self):  return msn1

    @pyqtSlot(result=float)
    def mesin2(self):  return msn2

    @pyqtSlot(result=float)
    def mesin3(self):  return msn3

    @pyqtSlot(result=float)
    def mesin4(self):  return msn4

    @pyqtSlot(result=float)
    def spc1(self):  return thruster1_command

    @pyqtSlot(result=float)
    def spc2(self):  return thruster2_command

    @pyqtSlot(result=float)
    def spc3(self):  return thruster3_command

    @pyqtSlot(result=float)
    def spc4(self):  return thruster4_command

    @pyqtSlot(result=float)
    def lat(self):  return round(val_latitude,8)

    @pyqtSlot(result=float)
    def long(self):  return round(val_longitude,8)

    @pyqtSlot(result=float)
    def headingship(self):  return heading

    @pyqtSlot(result=float)
    def winddirect(self):  return Wdirect

    @pyqtSlot(result=float)
    def windspeed(self):  return Wspeed

    @pyqtSlot(result = float)
    def position_error(self): return round(position_error,0)
    
    @pyqtSlot(result = float)
    def dir_error(self): return round(dir_error,0)

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
    
    
    @pyqtSlot(result = int)
    def heading_error(self): return heading_error
    
    
    @pyqtSlot(result=str)
    def spc_indicator_color(self): return spc_indicator_color
    
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
    def get_lat1 (self, lat_GUI1):
        global get_lat_GUI1
        get_lat_GUI1 = float(lat_GUI1)
        print("Lat 1= ", get_lat_GUI1)

    @pyqtSlot(float)
    def get_lon1 (self, lon_GUI1):
        global get_lon_GUI1
        global delta_lat
        global delta_lon
        global distance
        get_lon_GUI1 = float(lon_GUI1)
        delta_lat = (get_lat_GUI - get_lat_GUI1)*111000
        delta_lon = (get_lon_GUI - get_lon_GUI1)*111000
        distance = sqrt(pow(delta_lat, 2) +  pow(delta_lon, 2))
        print("Lon 1= ", get_lon_GUI1)
        print("delta lat= ", delta_lat)
        print("delta lon= ", delta_lon)
        print("distance= ", distance)
        
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
    
        
    @pyqtSlot(result=int)
    def distance_bw_line(self):return distance 

    #@pyqtSlot(result=int)
    #def distance_G(self):return distance_Grap 
    
    @pyqtSlot(result=float)
    def graphnel_latitude(self):return  Lat_G 

    @pyqtSlot(result=float)
    def graphnel_longitude(self):return Lon_G 

    @pyqtSlot(result=float)
    def heading_G(self):return heading_Grep
    
    @pyqtSlot(result=float)
    def flow_lpm(self):return float(flow_lpm)
    
    @pyqtSlot(result=float)
    def flow_lpm2(self):return float(flow_lpm2)
    
    
    @pyqtSlot(result = float)
    def speed_ship(self):return round(speed_ship,2)
    
    
    @pyqtSlot(result=str)
    def gps_status_color(self):return gps_status_color
    
    @pyqtSlot('QString')
    def setMinVal(self, value):
        global min_thruster
        datatext =str(value)
        if (datatext == ""):
            datatext = 0           
        #print (datatext)
    
    @pyqtSlot('QString')
    def setMaxVal(self, value):
        global max_thruster      
        datatext = str(value)
        if (datatext == ""):
            datatext = 0
        max_thruster = float(datatext)
        #print (datatext)
    
    
    @pyqtSlot('QString')
    def thrusterMode(self, value):
        global thruster_mode        
        thruster_mode =str(value)
        #print(thruster_mode)
        
        
    @pyqtSlot('QString')
    def setAggresivity(self, value):
        global aggresivity_coefficient      
        datatext =str(value)
        if (datatext == ""):
            datatext = 0           
        #print (datatext)
        aggresivity_coefficient = float(datatext)
        
    @pyqtSlot('QString')
    def station_keeping(self, value):
        global station_keeping_state      
        station_keeping_state = (value)
    
    @pyqtSlot('QString')
    def autopilot(self, value):
        global autopilot_state
        autopilot_state = value
        #print(autopilot_state)
        
    @pyqtSlot(int)
    def heading_target(self, value):
        global heading_target
        heading_target = value
        #print (heading_target)
        
    @pyqtSlot(str)
    def control_style(self, value):
        global control_style
        control_style = value
        #print(control_style)
        
        
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
                          str(val_longitude)]]                
                csvwriter.writerows(rows)

            
            
def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))
    t = str(message.topic)

    if(msg[0] == 'c'):
        val =  1
    else:
        val = (msg)

    if (t == "Set_Speed1"):
        global S1
        S1 = float(msg)
        #print(S1)

    if (t == "Set_Speed2"):
        global S2
        S2 = float(msg)

    if (t == "Set_Speed3"):
        global S3
        S3 = float(msg)

    if (t == "Set_Speed4"):
        global S4
        S4 = float(msg)

    if (t == "steering1"):
        global str1
        global spc_message_time_prev
        
        str1 = float(msg)
        spc_message_time_prev = time.time()

    if (t == "steering2"):
        global str2
        str2 = float(msg)

    if (t == "steering3"):
        global str3
        str3 = float(msg)

    if (t == "steering4"):
        global str4
        str4 = float(msg)

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
        global val_latitude
        global gps_time_prev
        gps_time_prev = time.time()
        val_latitude = float(msg)
        #print(msg)


    if (t == "long_nmea"):
        global val_longitude
        val_longitude = float(msg)

            
    if (t == "yaw_actual"):
        global heading
        global heading_Grep
        heading = float(msg)
        heading_Grep = heading
        #print(heading)
    
    if (t== "speed_nmea"):
        global speed_ship
        speed_ship = float (msg)
    
    
    if (t == "winddirect"):
        global Wdirect
        Wdirect = (float(msg) + heading) % 360

    if (t == "windspeed"):
        global Wspeed
        Wspeed = float(msg)
            
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
        rpm1 = float(msg)
    
    if (t == 'flow_lpm'):
        global flow_lpm
        flow_lpm = float(msg)
        
    if (t == 'flow_lpm2'):
        global flow_lpm2
        flow_lpm2 = float(msg)

#save csv
def timerEvent():
    global time
    global message_time
    global message_time_prev
    global mqtt_transmit_time
    global mqtt_transmit_time_prev
    global day
    global day_prev
    global EC1
    global EC1_time
    global EC2
    global EC2_time
    global EC3
    global EC3_time
    global EC4
    global EC4_time
    global aggresivity_time
    global aggresivity_time_prev
    global thruster_max
    global thruster_min
    global Lat_G
    global Lon_G
    global payout
    global water_depth
    global target_lat
    global target_long
    global error_lat
    global error_long
    global thruster1_command
    global thruster2_command
    global thruster3_command
    global thruster4_command
    global position_error
    global dir_error
    global heading_error
    global filtered_psi_error
    global x_error_body_fixed
    global y_error_body_fixed
    global psi_input
    global utm_lat_lon_wp
    global x
    global y
    global utm_lat_lon
    global psi
    
    global str1_target
    global str2_target
    global str3_target
    global str4_target
    global psi_error
    global spc_message_time
    global spc_message_time_prev
    global spc_indicator_color
    
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
    
    gps_time = time.time() - gps_time_prev
    if (gps_time > 4):
        gps_status_color = "red"
    else:
        gps_status_color = "green"
                           
    
    spc_message_time = time.time() - spc_message_time_prev
    
    if(spc_message_time > 4):
        spc_indicator_color = "red"
    
    else:
        spc_indicator_color = "green"
    
    
    speed_measurement_time = time.time() - speed_measurement_time_prev
    if (speed_measurement_time > 3):
        #try:
        #speed_ship = ((math.sqrt(math.pow((val_latitude - latitude_prev) * 111000, 2) + math.pow((val_longitude - longitude_prev) * 111000, 2))/3*2))

        #except:
        #speed_ship = 0
    
        
        latitude_prev = val_latitude
        longitude_prev = val_longitude
        #print(speed_ship)        
        speed_measurement_time_prev = time.time()
    utm_lat_lon = utm.from_latlon(val_latitude, val_longitude)
    x = utm_lat_lon[1]
    y = utm_lat_lon[0]
    psi = float(((heading)*math.pi/180))
    
    
    
    utm_lat_lon_wp = utm.from_latlon(target_lat, target_long)
    x_input = utm_lat_lon_wp[1]#, nyoba
    y_input = utm_lat_lon_wp[0]#,
                
    psi_input = float(heading_target)
    
    
    if (station_keeping_state == "true"):
        target_lat = target_lat
        target_long = target_long
        
    elif (station_keeping_state == "false"):
        target_lat = val_latitude
        target_long = val_longitude
        
    error_lat = round(((target_lat - val_latitude) * 111000),2)
    error_long = round(((target_long - val_longitude) * 111000),2)
    position_error = round(math.sqrt(math.pow(error_lat, 2) + math.pow(error_long,2)),2)
    try:
        if (target_long > val_longitude):
            dir_error = 1 * math.acos(error_lat/abs(position_error)) * 180/math.pi
        else:
            dir_error = -1 * math.acos(error_lat/abs(position_error)) * 180/math.pi
    except:
        dir_error = 0
   
    heading_error = int(heading_target) - int(heading)

    if ((math.pow(payout , 2) - math.pow(water_depth,2)) > 0):
        distance_Grap_m =  math.sqrt((math.pow(payout , 2) - math.pow(water_depth,2)))
    else:
        distance_Grap_m = 0
    if (distance_Grap_m < 0.000000001):
        distance_Grap_m = 0.000000001
        
    distance_Grap = distance_Grap_m/ 111000
    Lat_G = float(val_latitude - (distance_Grap * math.cos(heading* math.pi/180)))
    Lon_G = float(val_longitude - (distance_Grap * math.sin(heading* math.pi/180)))
    ######### THRUSTER ALLOCATION ###########
    
    if (control_style == "station keeping"):
        x_error =  x - float(x_input) 
        y_error =  y - float(y_input) 
        psi_error =  psi*180/phi - float(psi_input)
        filtered_psi_error = (0.5 * filtered_psi_error) + (0.5 * psi_error)
        x_error_body_fixed = x_error*math.cos(psi) + y_error*math.sin(psi)
        y_error_body_fixed = -x_error*math.sin(psi) + y_error*math.cos(psi)
        #print(round(x_error_body_fixed,1), round(y_error_body_fixed,1), filtered_psi_error)
        
        if (filtered_psi_error > y_error_body_fixed and filtered_psi_error > x_error_body_fixed):
            if filtered_psi_error > 8:
                str1_target = 0
                str2_target = 270
                str3_target = 90
                str4_target = 270
                
                """
                    rpm1 = 0
                    rpm2 = 30
                    rpm3 = 70
                    rpm4 = 70
                    azimuth_in1 = 0
                    azimuth_in2 = 270
                    azimuth_in3 = 90
                    azimuth_in4 = 270
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)

                """
                
            if filtered_psi_error < -8:
                str1_target = 0
                str2_target = 270
                str3_target = 90
                str4_target = 90
                
                """
                    rpm1 = 0
                    rpm2 = 70
                    rpm3 = 30
                    rpm4 = 70
                    azimuth_in1 = 0
                    azimuth_in2 = 270
                    azimuth_in3 = 90
                    azimuth_in4 = 90
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)
                """
                
            if filtered_psi_error > 5 and filtered_psi_error < 8 :
                str1_target = 0
                str2_target = 270
                str3_target = 90
                str4_target = 270
                """
                    rpm1 = 0
                    rpm2 = 50
                    rpm3 = 30
                    rpm4 = 50
                    azimuth_in1 = 0
                    azimuth_in2 = 270
                    azimuth_in3 = 90
                    azimuth_in4 = 270
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)
                """
                
            if filtered_psi_error < -5 and filtered_psi_error > -8:
                str1_target = 0
                str2_target = 270
                str3_target = 90
                str4_target = 90
                """
                    rpm1 = 0
                    rpm2 = 50
                    rpm3 = 30
                    rpm4 = 50
                    azimuth_in1 = 0
                    azimuth_in2 = 270
                    azimuth_in3 = 90
                    azimuth_in4 = 90
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)
                """
                
            if filtered_psi_error > -3 and filtered_psi_error < 3:
                str1_target = 0
                str2_target = 0
                str3_target = 0
                str4_target = 0
                """
                    rpm1 = 0
                    rpm2 = 0
                    rpm3 = 40
                    rpm4 = 0
                    azimuth_in1 = 0
                    azimuth_in2 = 0
                    azimuth_in3 = 0
                    azimuth_in4 = 0
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)
                """
                
        if  (y_error_body_fixed > filtered_psi_error and y_error_body_fixed > x_error_body_fixed):
                
            if y_error_body_fixed > 8:
                str1_target = 0
                str2_target = 270
                str3_target = 0
                str4_target = 270
                """
                    rpm1 = 0
                    rpm2 = 70
                    rpm3 = 30
                    rpm4 = 70
                    azimuth_in1 = 0
                    azimuth_in2 = 270
                    azimuth_in3 = 0
                    azimuth_in4 = 270
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)
                """
                
            if y_error_body_fixed < -8:
                str1_target = 0
                str2_target = 0
                str3_target = 90
                str4_target = 90
                """
                    rpm1 = 0
                    rpm2 = 40
                    rpm3 = 70
                    rpm4 = 70
                    azimuth_in1 = 0
                    azimuth_in2 = 0
                    azimuth_in3 = 90
                    azimuth_in4 = 90
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)
                """
                
            if y_error_body_fixed > 5 and y_error_body_fixed < 8:
                str1_target = 0
                str2_target = 270
                str3_target = 0
                str4_target = 270
                """
                    rpm1 = 0
                    rpm2 = 50
                    rpm3 = 30
                    rpm4 = 50
                    azimuth_in1 = 0
                    azimuth_in2 = 270
                    azimuth_in3 = 0
                    azimuth_in4 = 270
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)
                """
                
            if y_error_body_fixed < -5 and y_error_body_fixed > -8:
                str1_target = 0
                str2_target = 0
                str3_target = 90
                str4_target = 90
                """ 
                     rpm1 = 0
                    rpm2 = 30
                    rpm3 = 50
                    rpm4 = 50
                    azimuth_in1 = 0
                    azimuth_in2 = 0
                    azimuth_in3 = 90
                    azimuth_in4 = 90
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)
                """
            if y_error_body_fixed > -5 and y_error_body_fixed < 5:
                str1_target = 0
                str2_target = 0
                str3_target = 90
                str4_target = 90
                """
                    rpm1 = 0
                    rpm2 = 40
                    rpm3 = 0
                    rpm4 = 0
                    azimuth_in1 = 0
                    azimuth_in2 = 0
                    azimuth_in3 = 90
                    azimuth_in4 = 90
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)

                """    
        if  (x_error_body_fixed > filtered_psi_error and x_error_body_fixed > y_error_body_fixed):
                
            if x_error_body_fixed > 8:
                str1_target = 0
                str2_target = 180
                str3_target = 180
                str4_target = 180
                """
                    rpm1 = 0
                    rpm2 = 70
                    rpm3 = 70
                    rpm4 = 40
                    azimuth_in1 = 0
                    azimuth_in2 = 180
                    azimuth_in3 = 180
                    azimuth_in4 = 180
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)

                """
            if x_error_body_fixed < -8:
                str1_target = 0
                str2_target = 0
                str3_target = 0
                str4_target = 0
                """
                    rpm1 = 0
                    rpm2 = 70
                    rpm3 = 70
                    rpm4 = 40
                    azimuth_in1 = 0
                    azimuth_in2 = 0
                    azimuth_in3 = 0
                    azimuth_in4 = 0
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)                
                """
            if x_error_body_fixed > 5 and x_error_body_fixed < 8:
                str1_target = 0
                str2_target = 180
                str3_target = 180
                str4_target = 180
                """
                    rpm1 = 0
                    rpm2 = 55
                    rpm3 = 55
                    rpm4 = 30
                    azimuth_in1 = 0
                    azimuth_in2 = 180
                    azimuth_in3 = 180
                    azimuth_in4 = 180
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)

                """
            if x_error_body_fixed < -5 and x_error_body_fixed > -8 :
                str1_target = 0
                str2_target = 0
                str3_target = 0
                str4_target = 0
                
                """
                    rpm1 = 0
                    rpm2 = 55
                    rpm3 = 55
                    rpm4 = 30
                    azimuth_in1 = 0
                    azimuth_in2 = 0
                    azimuth_in3 = 0
                    azimuth_in4 = 0
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)                
                """
            if x_error_body_fixed > -3 and x_error_body_fixed < 3:
                str1_target = 0
                str2_target = 0
                str3_target = 0
                str4_target = 0
                
                """
                    rpm1 = 0
                    rpm2 = 35
                    rpm3 = 0
                    rpm4 = 0
                    azimuth_in1 = 0
                    azimuth_in2 = 0
                    azimuth_in3 = 0
                    azimuth_in4 = 0
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)
                """
    if (control_style == "sway keeping"):
        x_error =  0
        y_error =  y - float(y_input)
        psi_error =  psi*180/phi - float(psi_input)
        filtered_psi_error = (0.5 * filtered_psi_error) + (0.5 * psi_error)
        x_error_body_fixed = x_error*math.cos(psi) + x_error*math.sin(psi)
        y_error_body_fixed = -y_error*math.sin(psi) + y_error*math.cos(psi)
        if  (filtered_psi_error > y_error_body_fixed):
            if filtered_psi_error > 8:
                str1_target = 0
                str2_target = 270
                str3_target = 90
                str4_target = 270
                
                """
                    rpm1 = 0
                    rpm2 = 30
                    rpm3 = 70
                    rpm4 = 70
                    azimuth_in1 = 0
                    azimuth_in2 = 270
                    azimuth_in3 = 90
                    azimuth_in4 = 270
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)
                """
                
            if filtered_psi_error < -8:
                str1_target = 0
                str2_target = 270
                str3_target = 90
                str4_target = 90
                """
                    rpm1 = 0
                    rpm2 = 70
                    rpm3 = 30
                    rpm4 = 70
                    azimuth_in1 = 0
                    azimuth_in2 = 270
                    azimuth_in3 = 90
                    azimuth_in4 = 90
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)
                """
            if filtered_psi_error > 5 and filtered_psi_error < 8:
                str1_target = 0
                str2_target = 270
                str3_target = 90
                str4_target = 270
                """
                    rpm1 = 0
                    rpm2 = 50
                    rpm3 = 30
                    rpm4 = 50
                    azimuth_in1 = 0
                    azimuth_in2 = 270
                    azimuth_in3 = 90
                    azimuth_in4 = 270
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)
                """
            if filtered_psi_error < -5 and filtered_psi_error > -8:
                str1_target = 60
                str2_target = 40
                str3_target = 20
                str4_target = 10

                """
                    rpm1 = 0
                    rpm2 = 55
                    rpm3 = 55
                    rpm4 = 30
                    azimuth_in1 = 0
                    azimuth_in2 = 0
                    azimuth_in3 = 0
                    azimuth_in4 = 0
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)
                """
            if filtered_psi_error > -3 and filtered_psi_error < 3:
                str1_target = 0
                str2_target = 0
                str3_target = 0
                str4_target = 0

                """
                    rpm1 = 0
                    rpm2 = 0
                    rpm3 = 40
                    rpm4 = 0
                    azimuth_in1 = 0
                    azimuth_in2 = 0
                    azimuth_in3 = 0
                    azimuth_in4 = 0
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)
                """
        if  (y_error_body_fixed > filtered_psi_error):
                
            if filtered_psi_error > 8:
                str1_target = 0
                str2_target = 270
                str3_target = 0
                str4_target = 270
                """
                   rpm1 = 0
                    rpm2 = 70
                    rpm3 = 30
                    rpm4 = 70
                    azimuth_in1 = 0
                    azimuth_in2 = 270
                    azimuth_in3 = 0
                    azimuth_in4 = 270
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)
                """
            if filtered_psi_error < -8:
                str1_target = 0
                str2_target = 40
                str3_target = 70
                str4_target = 70
                """
                    rpm1 = 0
                    rpm2 = 40
                    rpm3 = 70
                    rpm4 = 70
                    azimuth_in1 = 0
                    azimuth_in2 = 0
                    azimuth_in3 = 90
                    azimuth_in4 = 90
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                """
            if filtered_psi_error > 5 and filtered_psi_error < 8:
                str1_target = 0
                str2_target = 270
                str3_target = 0
                str4_target = 270
                """
                    rpm1 = 0
                    rpm2 = 50
                    rpm3 = 30
                    rpm4 = 50
                    azimuth_in1 = 0
                    azimuth_in2 = 270
                    azimuth_in3 = 0
                    azimuth_in4 = 270
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)
                """
            if filtered_psi_error < -5 and filtered_psi_error > -8:
                str1_target = 0
                str2_target = 0
                str3_target = 90
                str4_target = 90
                """
                    rpm1 = 0
                    rpm2 = 30
                    rpm3 = 50
                    rpm4 = 50
                    azimuth_in1 = 0
                    azimuth_in2 = 0
                    azimuth_in3 = 90
                    azimuth_in4 = 90
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)
                """
            if filtered_psi_error > -5 and filtered_psi_error < 5:
                str1_target = 0
                str2_target = 0
                str3_target = 90
                str4_target = 90

            """
                    rpm1 = 0
                    rpm2 = 40
                    rpm3 = 0
                    rpm4 = 0
                    azimuth_in1 = 0
                    azimuth_in2 = 0
                    azimuth_in3 = 90
                    azimuth_in4 = 90
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)
            """
    if (control_style == "heading keeping"):
        x_error =  0
        y_error = 0
        psi_error =  psi*180/phi - float(psi_input)
        filtered_psi_error = (0.5 * filtered_psi_error) + (0.5 * psi_error)
        x_error_body_fixed = x_error*math.cos(-psi*phi/180) + x_error*math.sin(-psi*phi/180)
        y_error_body_fixed = -y_error*math.sin(-psi*phi/180) + y_error*math.cos(-psi*phi/180)
        #print(filtered_psi_error)
        if filtered_psi_error > 8:
            str1_target = 0
            str2_target = 270
            str3_target = 90
            str4_target = 270
            """
                    rpm1 = 0
                    rpm2 = 30
                    rpm3 = 70
                    rpm4 = 70
                    azimuth_in1 = 0
                    azimuth_in2 = 270
                    azimuth_in3 = 90
                    azimuth_in4 = 270
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)
            """            
        if filtered_psi_error < -8:
            str1_target = 0
            str2_target = 270
            str3_target = 90
            str4_target = 90
            """
                    rpm1 = 0
                    rpm2 = 70
                    rpm3 = 30
                    rpm4 = 70
                    azimuth_in1 = 0
                    azimuth_in2 = 270
                    azimuth_in3 = 90
                    azimuth_in4 = 90
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)
            """            
        if filtered_psi_error > 5 and filtered_psi_error < 8:
            str1_target = 0
            str2_target = 270
            str3_target = 90
            str4_target = 270
            """
                    rpm1 = 0
                    rpm2 = 50
                    rpm3 = 30
                    rpm4 = 50
                    azimuth_in1 = 0
                    azimuth_in2 = 270
                    azimuth_in3 = 90
                    azimuth_in4 = 270
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)
            """
        if filtered_psi_error < -5 and filtered_psi_error > -8:
            str1_target = 0
            str2_target = 0
            str3_target = 0
            str4_target = 0

            """
                    rpm1 = 0
                    rpm2 = 55
                    rpm3 = 55
                    rpm4 = 30
                    azimuth_in1 = 0
                    azimuth_in2 = 0
                    azimuth_in3 = 0
                    azimuth_in4 = 0
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)

            """
        if filtered_psi_error > -3 and filtered_psi_error < 3:
            str1_target = 0
            str2_target = 0
            str3_target = 0
            str4_target = 0

            """
                    rpm1 = 0
                    rpm2 = 0
                    rpm3 = 40
                    rpm4 = 0
                    azimuth_in1 = 0
                    azimuth_in2 = 0
                    azimuth_in3 = 0
                    azimuth_in4 = 0
                    client.publish("Set_Speed4", rpm4)
                    client.publish("Set_Azimuth4", azimuth_in4)
                    client.publish("Set_Speed3", rpm3)
                    client.publish("Set_Azimuth3", azimuth_in3)
                    client.publish("Set_Speed2", rpm2)
                    client.publish("Set_Azimuth2", azimuth_in2)
            """
    
    
    
    ########## mode manual or automatic
    if (thruster_mode == "manual"):
        thruster1_command = S1
        thruster2_command = S2
        thruster3_command = S3
        thruster4_command = S4
        
        
    if (thruster_mode == "auto"):
       pass 
        
       
        
    mqtt_transmit_time = time.time() - mqtt_transmit_time_prev
    if (mqtt_transmit_time > 1):
        #print("transmit data")
        client.publish("thruster1_command", str(thruster1_command))
        client.publish("thruster2_command", str(thruster2_command))
        client.publish("thruster3_command", str(thruster3_command))
        client.publish("thruster4_command", str(thruster4_command))
        
        mqtt_transmit_time_prev = time.time()
        
    #####spc status
    EC1_time = time.time() - EC1_time_prev
    if EC1_time < 3:
        EC1 = 1
    else :
        EC1 = 0
           
    EC2_time = time.time() - EC2_time_prev
    if EC2_time < 3:
        EC2 = 1
    else :
        EC2 = 0
    
    EC3_time = time.time() - EC3_time_prev
    if EC3_time < 3:
        EC3 = 1
    else :
        EC3 = 0
    
    EC4_time = time.time() - EC4_time_prev
    if EC4_time < 3:
        EC4 = 1
    else :
        EC4 = 0
    
    
    message_time = time.time() - message_time_prev
    current_time = dt.datetime.now()
    day = current_time.day
    
    if (day != day_prev):
        fields = ['time', 'lat', 'long', 'wind speed','wind direct', 'heading','ship speed', 'dp speed 1','dp speed 2','dp speed 3','dp speed 4','flow engine']
        filename = str("DPS RECORD " ) + str(current_time.day)+str("-")+str(current_time.month)+str("-")+str(current_time.year) + str(".csv")    
        with open(filename, 'a') as csvfile:
            # creating a csv writer object
            csvwriter = csv.writer(csvfile)
            # writing the fields
            csvwriter.writerow(fields)
   
    day_prev = day
    if message_time > 5:
        print("data saved")
        message_time_prev = time.time()
        waktu = dt.datetime.now()
        filename = str("DPS RECORD " ) + str(current_time.day)+str("-")+str(current_time.month)+str("-")+str(current_time.year) + str(".csv")
        with open(filename, 'a') as csvfile:
                csvwriter = csv.writer(csvfile)
                rows = [ [str(str(waktu.hour) + str(":") + str(waktu.minute)+ str(":") + str(waktu.second)),str(val_latitude),
                          str(val_longitude),str(Wspeed),str(Wdirect),str(heading),str(speed_ship), str(S1),str(S2),str(S3),str(S4),str(flow_lpm) ]]
                csvwriter.writerows(rows)

if __name__ == "__main__":

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

    client.subscribe("mesin1")
    client.subscribe("mesin2")
    client.subscribe("mesin3")
    client.subscribe("mesin4")

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
    client.subscribe("speed_nmea")
    client.subscribe("yaw")
    client.subscribe("yaw_actual")
    client.subscribe("winddirect")
    client.subscribe("windspeed")
    
    client.subscribe("ship_x")
    client.subscribe("ship_y")
    client.subscribe("lat_target")
    client.subscribe("long_target")
    client.subscribe("long_error")
    client.subscribe("lat_error")
    client.subscribe("distance_G")
    client.subscribe("graphnel_latitude")
    client.subscribe("graphnel_longitude")
    client.subscribe("heading_G")
    client.subscribe("flow_lpm")
    client.subscribe("flow_lpm2")
    
        
    client.publish("MainControl", "active")#publish
    client.publish("dummyval", str(0))

    ## QT5 GUI
    print("Graphical User Interface ")
    app = QGuiApplication(sys.argv)

    view = QQuickView()
    app.setWindowIcon(QIcon("syergielogofix.png"))
    view.setTitle("SYERGIE DPS SOFTWARE")
    view.setGeometry(0, 0, 1500, 800)
    view.setSource(QUrl('main.qml'))

    mqttvalue = MQTTValue()
    w = MQTTValue()

    timer = QTimer()
    timer.timeout.connect(timerEvent)
    timer.start(10) ##Update screen every 10 miliseconds

    context = view.rootContext()
    context.setContextProperty("mqttvalue", mqttvalue)

    root = view.rootObject()
    timer.timeout.connect(root.updateValue) ##Call function update in GUI QML

    engine = QQmlApplicationEngine(app) 
    engine.quit.connect(app.quit) ## Quit Button Respon
        
    view.show()

    sys.exit(app.exec_())
    
    
    
