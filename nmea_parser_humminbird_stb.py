"""
Humminbird AS GPS HS - NMEA 0183 Parser (Latitude, Longitude, Heading)
========================================================================
Versi dengan auto-reconnect:
  - Kalau serial port disconnect (device dicabut / error), program akan
    mencoba membuka ulang port setiap 3 detik, tanpa perlu restart proses.
  - Kalau koneksi MQTT terputus, paho-mqtt akan mencoba reconnect otomatis
    dengan delay 3 detik.

Install dulu library-nya kalau belum ada:
    pip install pyserial paho-mqtt

Sesuaikan PORT dan BAUD_RATE di bawah sebelum dijalankan.
"""

import glob
import sys
import time
import threading

import serial
sys.path.insert(0, "./lib")
import paho.mqtt.client as paho

# ============================================================
# KONFIGURASI - SESUAIKAN INI
# ============================================================

RECONNECT_DELAY = 3  # detik, delay reconnect serial & mqtt


def serial_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


print(str(serial_ports()))
PORT = input("write port : ")

BAUD_RATE = 38400
TIMEOUT = 1

broker = "127.0.0.1"
mqtt_port = 1883


def nmea_to_decimal(raw_value: str, direction: str):
    if not raw_value or not direction:
        return None
    degree_len = 2 if direction in ("N", "S") else 3
    degrees = float(raw_value[:degree_len])
    minutes = float(raw_value[degree_len:])
    decimal = degrees + (minutes / 60.0)
    if direction in ("S", "W"):
        decimal = -decimal
    return round(decimal, 6)


def parse_gga(fields: list):
    try:
        raw_lat = fields[2]
        ns = fields[3]
        raw_lon = fields[4]
        ew = fields[5]
        fix_quality = fields[6]
        num_sats = fields[7]

        lat = nmea_to_decimal(raw_lat, ns)
        lon = nmea_to_decimal(raw_lon, ew)

        if lat is None or lon is None:
            return None

        return {
            "latitude": lat,
            "longitude": lon,
            "fix_quality": fix_quality,
            "satellites": num_sats,
        }
    except (IndexError, ValueError):
        return None


def parse_hdg(fields: list):
    try:
        heading = fields[1]
        if not heading:
            return None
        return {"heading": float(heading)}
    except (IndexError, ValueError):
        return None


def parse_sentence(line: str):
    if not line.startswith("$"):
        return None
    line = line.split("*")[0]
    fields = line.split(",")
    sentence_type = fields[0][3:]

    if sentence_type == "GGA":
        result = parse_gga(fields)
        if result:
            return {"type": "position", "data": result}
    elif sentence_type == "HDG":
        result = parse_hdg(fields)
        if result:
            return {"type": "heading", "data": result}
    return None


def gps_calc(client):
    """
    Loop luar: kalau port gagal dibuka / terputus di tengah jalan,
    tunggu RECONNECT_DELAY detik lalu coba buka lagi. Loop ini tidak
    pernah berhenti sendiri kecuali Ctrl+C.
    """
    while True:
        print(f"Membuka {PORT} @ {BAUD_RATE} baud...")
        try:
            ser = serial.Serial(PORT, BAUD_RATE, timeout=TIMEOUT)
        except serial.SerialException as e:
            print(f"Gagal membuka port serial: {e}")
            print(f"Coba lagi dalam {RECONNECT_DELAY} detik...")
            time.sleep(RECONNECT_DELAY)
            continue  # balik ke atas, coba buka lagi

        print("Terhubung. Membaca data... (Ctrl+C untuk berhenti)\n")

        try:
            while True:
                try:
                    raw_line = ser.readline().decode("ascii", errors="ignore").strip()
                except UnicodeDecodeError:
                    continue
                except serial.SerialException as e:
                    # Ini kondisi disconnect (device dicabut, dsb)
                    print(f"\nSerial terputus: {e}")
                    break  # keluar ke loop luar untuk reconnect

                if not raw_line:
                    continue

                parsed = parse_sentence(raw_line)
                if parsed is None:
                    continue

                if parsed["type"] == "position":
                    d = parsed["data"]
                    print(
                        f"[POSISI] Lat: {d['latitude']:.6f}  "
                        f"Lon: {d['longitude']:.6f}  "
                        f"Fix: {d['fix_quality']}  "
                        f"Sat: {d['satellites']}"
                    )
                    client.publish("lat_nmea", str(f"{d['latitude']:.6f}"))
                    client.publish("long_nmea", str(f"{d['longitude']:.6f}"))

                elif parsed["type"] == "heading":
                    d = parsed["data"]
                    print(f"[COMPASS] Heading: {d['heading']:.1f} derajat")
                    client.publish("yaw_actual", str(int(d['heading'])))

        except KeyboardInterrupt:
            print("\nBerhenti oleh user.")
            try:
                ser.close()
            except Exception:
                pass
            return  # keluar total dari gps_calc
        finally:
            try:
                ser.close()
            except Exception:
                pass
            print("Port serial ditutup.")

        # kalau sampai sini artinya loop dalam break karena disconnect,
        # bukan karena Ctrl+C -> tunggu lalu reconnect
        print(f"Menunggu {RECONNECT_DELAY} detik sebelum reconnect...")
        time.sleep(RECONNECT_DELAY)


def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))
    if msg and msg[0] == 'c':
        val = 1
    else:
        val = msg


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT terhubung ke broker.")
    else:
        print(f"MQTT gagal connect, rc={rc}")


def on_disconnect(client, userdata, rc):
    print(f"MQTT terputus (rc={rc}). paho akan reconnect otomatis...")


def connect_mqtt():
    """
    Loop mencoba connect ke broker MQTT tiap RECONNECT_DELAY detik
    sampai berhasil. Setelah berhasil connect, paho-mqtt loop_start()
    + reconnect_delay_set() akan menangani reconnect otomatis kalau
    koneksi putus di tengah jalan.
    """
    client = paho.Client("NMEA_GPS_PC")
    client.on_message = on_message
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    # atur delay reconnect otomatis paho: min 1 detik, max 3 detik
    client.reconnect_delay_set(min_delay=1, max_delay=RECONNECT_DELAY)

    while True:
        try:
            print("Menghubungkan ke broker", broker)
            client.connect(broker, mqtt_port)
            break
        except Exception as e:
            print(f"Gagal connect ke broker MQTT: {e}")
            print(f"Coba lagi dalam {RECONNECT_DELAY} detik...")
            time.sleep(RECONNECT_DELAY)

    client.loop_start()
    return client


if __name__ == "__main__":
    mqtt_client = connect_mqtt()

    t1 = threading.Thread(target=gps_calc, args=(mqtt_client,), daemon=True)
    t1.start()
    t1.join()