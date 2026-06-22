'''
format publish

{
    "latitude": -6.921345,
    "longitude": 107.607812,
    "heading": 185.4
}


'''
import paho.mqtt.client as paho
import time
import json
import datetime


# ----------------------------------------------------------------
# MQTT CONFIG
# ----------------------------------------------------------------
broker = "broker.avisha.id"
port = 1883

username = "dps_syergie_mqtt"
password = "syergie"

topic_test = ""

# ----------------------------------------------------------------
# CALLBACK CONNECT
# ----------------------------------------------------------------
def on_connect(client, userdata, flags, rc):

    if rc == 0:

        print("Connected to broker")
        client.subscribe("dps_syergie_mqtt/sensor")
        client.subscribe("dps_syergie_mqtt/tug1")
        client.subscribe("dps_syergie_mqtt/tug2")
        #client.subscribe("dps_syergie_mqtt/barge")
       

    else:

        print("Failed connect, code =", rc)


# ----------------------------------------------------------------
# CALLBACK MESSAGE
# ----------------------------------------------------------------
def on_message(client, userdata, message):

    global topic_test

    msg = message.payload.decode("utf-8")

    topic = message.topic

    if (topic == "dps_syergie_mqtt/sensor"):
        print("------------------")
        print("Topic   :", topic)
        print("Message :", msg)

        topic_test = msg
        
    if topic.startswith("dps_syergie_mqtt/"):

        vehicle = topic.split("/")[-1]   # tug1 / tug2 / barge

        try:

            data = json.loads(msg)

            save_data = {
                "latitude": data["latitude"],
                "longitude": data["longitude"],
                "heading": data["heading"],
                "received_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            try:
                with open("position.json", "r") as file:
                    position = json.load(file)
            except:
                position = {}

            position[vehicle] = save_data

            with open("position.json", "w") as file:
                json.dump(position, file, indent=4)

            print(f"Saved {vehicle}")

        except Exception as e:
            print("JSON Error :", e)


# ----------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------
if __name__ == "__main__":

    client = paho.Client(client_id="PC_1")

    client.username_pw_set(
        username,
        password
    )

    client.on_connect = on_connect
    client.on_message = on_message

    print("Connecting to :", broker)

    client.connect(
        broker,
        port,
        60
    )

    client.loop_start()

    try:

        while True:
            
            with open("position.json", "r") as f:
                position = json.load(f)

            print(position["barge"])
            payload = json.dumps(position["barge"])

            client.publish("dps_syergie_mqtt/barge", payload)
            time.sleep(1)

    except KeyboardInterrupt:
        print("Disconnect")
        client.loop_stop()
        client.disconnect()