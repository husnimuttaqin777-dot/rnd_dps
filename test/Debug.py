#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import math
import utm
from math import sin, cos, sqrt, atan2, radians
import random  

from math import pow
phi = math.pi
from PyQt5.QtCore import QUrl, QObject, pyqtSignal, pyqtSlot, QTimer, pyqtProperty
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQuick import QQuickView
from PyQt5.QtQml import QQmlApplicationEngine
import threading 



import time
import paho.mqtt.client as paho
#broker="123.45.0.10"
broker="127.0.0.1"
port = 1883

pubdelay = 2 #delay publish to all wind and engine box
counter = 0




S1 = 0
S2 = 0
S3 = 0
S4 = 0
EC1 = 0
EC2 = 0
EC3 = 0
EC4 = 0
str1 = 0
str2 = 0
str3 = 0
str4 = 0
bt1 = 0
bt2 = 0
bt3 = 0
bt4 = 0
msn1 = 0
msn2 = 0
msn3 = 0
msn4 = 0
tmp1 = 0
tmp2 = 0
tmp3 = 0
tmp4 = 0
SP1 = 0
SP2 = 0
SP3 = 0
SP4 = 0


target_lat =0
target_long = 0
error_long =0
error_lat = 0
x_ship = 185
y_ship = 100
distance = 0

Wspeed=0
Wdirect=0

val_latitude = -0.5932511  #centre
filtered_val_latitude = -0.5932511  #centre
val_longitude = 123.8159180  #centre
filtered_val_longitude = 123.8159180  #centre
#val_latitude = -0.5932511  #centre
#val_longtitude = 123.8159180  #centre



Lat_G = -0.5942511
Lon_G = 123.8169180
heading = 0


get_lat_GUI = 0
get_lon_GUI = 0
get_lat_GUI1 = 0
get_lon_GUI1 = 0
get_lat_GUI_last = 0
get_lon_GUI_last = 0
counter_distance_mea = 0
dst_bw_line = 0

station_keeping_state = 0

delta_lat = 0
delta_lat = 0

heading_Grep = 0
distance_Grap=0
heading_G = 0

def reMap(value, maxInput, minInput, maxOutput, minOutput):

	value = maxInput if value > maxInput else value
	value = minInput if value < minInput else value

	inputSpan = maxInput - minInput
	outputSpan = maxOutput - minOutput

	scaledThrust = float(value - minInput) / float(inputSpan)


	return minOutput + (scaledThrust * outputSpan)

class MQTTValue(QObject):   
	def __init__(self):
		super(MQTTValue,self).__init__()


	@pyqtSlot(result=float)
	def Set_Speed1(self):  return S1
		
	
	@pyqtSlot(result=float)
	def Set_Speed2(self):  return S2

	@pyqtSlot(result=float)
	def Set_Speed3(self):  return S3

	@pyqtSlot(result=float)
	def Set_Speed4(self):  return S4



	@pyqtSlot(result=float)
	def engineconect1(self):  return EC1

	@pyqtSlot(result=float)
	def engineconect2(self):  return EC2

	@pyqtSlot(result=float)
	def engineconect3(self):  return EC3

	@pyqtSlot(result=float)
	def engineconect4(self):  return EC4


	@pyqtSlot(result=float)
	def steering1(self):  return str1

	@pyqtSlot(result=float)
	def steering2(self):  return str2

	@pyqtSlot(result=float)
	def steering3(self):  return str3

	@pyqtSlot(result=float)
	def steering4(self):  return str4


	@pyqtSlot(result=float)
	def bat1(self):  return bt1

	@pyqtSlot(result=float)
	def bat2(self):  return bt2

	@pyqtSlot(result=float)
	def bat3(self):  return bt3

	@pyqtSlot(result=float)
	def bat4(self):  return bt4




	@pyqtSlot(result=float)
	def mesin1(self):  return msn1

	@pyqtSlot(result=float)
	def mesin2(self):  return msn2

	@pyqtSlot(result=float)
	def mesin3(self):  return msn3

	@pyqtSlot(result=float)
	def mesin4(self):  return msn4





	@pyqtSlot(result=float)
	def temp1(self):  return tmp1

	@pyqtSlot(result=float)
	def temp2(self):  return tmp2

	@pyqtSlot(result=float)
	def temp3(self):  return tmp3

	@pyqtSlot(result=float)
	def temp4(self):  return tmp4






	@pyqtSlot(result=float)
	def spc1(self):  return SP1

	@pyqtSlot(result=float)
	def spc2(self):  return SP2

	@pyqtSlot(result=float)
	def spc3(self):  return SP3

	@pyqtSlot(result=float)
	def spc4(self):  return SP4




	@pyqtSlot(result=float)
	def lat(self):  return val_latitude

	@pyqtSlot(result=float)
	def long(self):  return val_longitude

	@pyqtSlot(result=float)
	def headingship(self):  return heading

	@pyqtSlot(result=float)
	def winddirect(self):  return Wdirect

	@pyqtSlot(result=float)
	def windspeed(self):  return Wspeed




	@pyqtSlot(result=float)
	def ship_x(self):  return x_ship

	@pyqtSlot(result=float)
	def ship_y(self):  return y_ship

	@pyqtSlot(result=float)
	def lat_target(self):  return target_lat

	@pyqtSlot(result=float)
	def long_target(self):  return target_long

	@pyqtSlot(result=float)
	def long_error(self):  return error_long

	@pyqtSlot(result=float)
	def lat_error(self):  return error_lat
	

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
        
	@pyqtSlot(result=int)
	def distance_bw_line(self):return distance 

	@pyqtSlot(result=int)
	def distance_G(self):return distance_Grap 
	
	@pyqtSlot(result=float)
	def graphnel_latitude(self):return  Lat_G 

	@pyqtSlot(result=float)
	def graphnel_longitude(self):return Lon_G 		

	@pyqtSlot(result=float)
	def heading_G(self):return heading_Grep
	
	
def on_message(client, userdata, message):
		msg = str(message.payload.decode("utf-8"))
		t = str(message.topic)

		if(msg[0] == 'c'):
			val =  1
		else:
			val = float(msg)

		if (t == "Set_Speed1"):
			global S1
			S1 = float(msg)

		if (t == "Set_Speed2"):
			global S2
			S2 = float(msg)


		if (t == "Set_Speed3"):
			global S3
			S3 = float(msg)


		if (t == "Set_Speed4"):
			global S4
			S4 = float(msg)


		if (t == "engineconect1"):
			global EC1
			EC1 = val

		if (t == "engineconect2"):
			global EC2
			EC2 = val

		if (t == "engineconect3"):
			global EC3
			EC3 = val

		if (t == "engineconect4"):
			global EC4
			EC4 = val



		if (t == "steering1"):
			global str1
			str1 = float(msg)

		if (t == "steering2"):
			global str2
			str2 = float(msg)

		if (t == "steering3"):
			global str3
			str3 = float(msg)

		if (t == "steering4"):
			global str4
			str4 = float(msg)



		if (t == "bat1"):
			global bt1
			bt1 = float(msg)

		if (t == "bat2"):
			global bt2
			bt2 = float(msg)

		if (t == "bat3"):
			global bt3
			bt3 = float(msg)

		if (t == "bat4"):
			global bt4
			bt4 = float(msg)

		if (t == "mesin1"):
			global msn1
			msn1 = float(msg)

		if (t == "mesin2"):
			global msn2
			msn2 = float(msg)

		if (t == "mesin3"):
			global msn3
			msn3 = float(msg)

		if (t == "mesin4"):
			global msn4
			msn4 = float(msg)


		if (t == "temp1"):
			global tmp1
			tmp1 = float(msg)

		if (t == "temp2"):
			global tmp2
			tmp2 = float(msg)

		if (t == "temp3"):
			global tmp3
			tmp3 = float(msg)

		if (t == "temp4"):
			global tmp4
			tmp4 = float(msg)


		if (t == "spc1"):
			global SP1
			SP1 = val

		if (t == "spc2"):
			global SP2
			SP2 = val

		if (t == "spc3"):
			global SP3
			SP3 = val

		if (t == "spc4"):
			global SP4
			SP4 = val

		if (t == "station_keeping"):
			global station_keeping_state
			station_keeping_state = val



		if (t == "GPS/lat"):
			global val_latitude
			val_latitude = float(msg)


		if (t == "GPS/long"):
			global val_longitude
			val_longitude = float(msg)


		#if (t == "graphnel_latitude"):
			#global Lat_G
			#Lat_G = float(msg)


		#if (t == "graphnel_longitude"):
			#global Lon_G
			#Lon_G = float(msg)

			
		global target_lat
		global target_long
		global error_lat
		global error_long
		global x_ship
		global y_ship
		
		
		if station_keeping_state == 1:
			target_lat = target_lat
			target_long = target_long
		elif station_keeping_state == 0:
			target_lat = val_latitude
			target_long = val_longitude
		
		error_lat = round(((target_lat - val_latitude) * 111000),2)
		error_long = round(((target_long - val_longitude) * 111000),2)
		#print(str(x_ship) +str(" ") + str(y_ship))
		
		#PILIH SALAH SATU
		#x_ship = round(float((0.0778*error_long) + 155.5) , 2) # 311 x 183
		x_ship = round(float((0.0618*error_long) + 123.5) , 2) # 247 x 134
		#PILIH SALAH SATU
		#pc husni 247 x 134
		if x_ship > 247 :
			x_ship = 247
		if x_ship < 0 :
			x_ship = 0
		
		'''
		# 311 x 183
		if x_ship > 311 :
			x_ship = 311
		if x_ship < 0 :
			x_ship = 0
		'''
		#PILIH SALAH SATU
		#y_ship = round(float((-0.045*error_lat) + 91) , 2)# 311 x 183
		y_ship = round(float((-0.0336*error_lat) + 67) , 2)# 247 x 134
		
		
		#PILIH SALAH SATU
		#pc husni 247 x 134
		if y_ship > 134 :
			y_ship = 134
		if y_ship < 0 :
			y_ship = 0
		'''
		# 311 x 183
		if y_ship > 182 :
			y_ship = 182
		if y_ship < 0 :
			y_ship = 0
		'''

                
            
		if (t == "headingship"):
			global heading
			global heading_Grep
			heading = float(msg)
			
			heading_Grep = heading
			#print(heading_Grep)
		
		
		if (t == "winddirect"):
			global Wdirect
			Wdirect = float(msg)

		if (t == "windspeed"):
			global Wspeed
			Wspeed = float(msg)


		if (t == "distance_G"):
			global distance_Grap
			global Lat_G
			global Lon_G
			
			distance_Grap = float(msg) / 111000
		Lat_G = float(val_latitude - (distance_Grap * math.cos(heading* math.pi/180)))
		Lon_G = float(val_longitude - (distance_Grap * math.sin(heading* math.pi/180)))
		#print(str(Lat_G) +str(" ") + str(Lon_G) + str(" ") + str(distance_Grap))





if __name__ == "__main__":

	##Mosquitto Mqtt Configuration			
	client= paho.Client("GUI")
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

	client.subscribe("bat1")
	client.subscribe("bat2")
	client.subscribe("bat3")
	client.subscribe("bat4")

	client.subscribe("mesin1")
	client.subscribe("mesin2")
	client.subscribe("mesin3")
	client.subscribe("mesin4")

	client.subscribe("temp1")
	client.subscribe("temp2")
	client.subscribe("temp3")
	client.subscribe("temp4")

	client.subscribe("spc1")
	client.subscribe("spc2")
	client.subscribe("spc3")
	client.subscribe("spc4")

	client.subscribe("GPS/lat")	
	client.subscribe("GPS/long")
	client.subscribe("headingship")	
	client.subscribe("winddirect")
	client.subscribe("windspeed")
	
	client.subscribe("ship_x")	
	client.subscribe("ship_y")
	client.subscribe("lat_target")	
	client.subscribe("long_target")
	client.subscribe("long_error")
	client.subscribe("lat_error")	
	client.subscribe("station_keeping")
	client.subscribe("distance_G")	
	client.subscribe("graphnel_latitude")
	client.subscribe("graphnel_longitude")		
	client.subscribe("heading_G")		
		
	client.publish("MainControl", "active")#publish

	## QT5 GUI
	print("Graphical User Interface ")
	app = QGuiApplication(sys.argv)

	view = QQuickView()
	view.setSource(QUrl('main.qml'))

	mqttvalue = MQTTValue()


	timer = QTimer()
	timer.start(10) ##Update screen every 10 miliseconds

	context = view.rootContext()
	context.setContextProperty("mqttvalue", mqttvalue)

	root = view.rootObject()
	timer.timeout.connect(root.updateValue) ##Call function update in GUI QML

	engine = QQmlApplicationEngine(app) 
	engine.quit.connect(app.quit) ## Quit Button Respon
		
	view.show()




	sys.exit(app.exec_())



