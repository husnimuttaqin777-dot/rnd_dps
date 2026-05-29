import json
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("test")  # Ganti dengan topik MQTT yang sesuai

def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    try:
        data = json.loads(payload)
        print("Received JSON data:", data)
        
        # Lakukan sesuatu dengan data JSON yang diterima
        # Contoh: Akses latitude dan longitude
        for item in data:
            latitude = item.get("latitude")
            longitude = item.get("longitude")
            print(f"Latitude: {latitude}, Longitude: {longitude}")

    except json.JSONDecodeError as e:
        print("Failed to decode JSON:", e)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Ganti dengan detail broker MQTT yang sesuai
broker_address = "127.0.0.1"
port = 1883
client.connect(broker_address, port, 60)

# Loop utama untuk terus mendengarkan pesan MQTT
client.loop_forever()
