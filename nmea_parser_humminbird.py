"""
Humminbird AS GPS HS - NMEA 0183 Parser (Latitude, Longitude, Heading)
========================================================================
Baca data serial dari converter RS232/TTL, parsing sentence:
  - $GPGGA -> latitude & longitude
  - $GPHDG  -> heading kompas

Install dulu library-nya kalau belum ada:
    pip install pyserial

Sesuaikan PORT dan BAUD_RATE di bawah sebelum dijalankan.
"""

import serial
import time

import threading
import sys

sys.path.insert(0, "./lib")
import paho.mqtt.client as paho
# ============================================================
# KONFIGURASI - SESUAIKAN INI
# ============================================================

def serial_ports():
    
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
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



#PORT = "COM3"        # Windows: "COM3", "COM4", dst.
                      # Linux/Mac: "/dev/ttyUSB0" atau "/dev/tty.usbserial-xxxx"
BAUD_RATE = 38400     # sesuaikan dengan converter Anda (4800 atau 38400)
TIMEOUT = 1           # detik

broker = "127.0.0.1"
port = 1883

def nmea_to_decimal(raw_value: str, direction: str) -> float:
    """
    Konversi format NMEA ddmm.mmmm (lat) / dddmm.mmmm (lon) ke decimal degrees.
    Contoh lat: 0653.88981  -> 06 derajat, 53.88981 menit
    Contoh lon: 10737.80097 -> 107 derajat, 37.80097 menit
    """
    if not raw_value or not direction:
        return None

    # Lat pakai 2 digit derajat, lon pakai 3 digit derajat
    degree_len = 2 if direction in ("N", "S") else 3

    degrees = float(raw_value[:degree_len])
    minutes = float(raw_value[degree_len:])
    decimal = degrees + (minutes / 60.0)

    if direction in ("S", "W"):
        decimal = -decimal

    return round(decimal, 6)


def parse_gga(fields: list) -> dict:
    """
    $GPGGA,time,lat,N/S,lon,E/W,fix,sats,hdop,alt,M,...
    """
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


def parse_hdg(fields: list) -> dict:
    """
    $GPHDG,heading,deviation,dev_dir,variation,var_dir
    """
    try:
        heading = fields[1]
        if not heading:
            return None
        return {"heading": float(heading)}
    except (IndexError, ValueError):
        return None


def parse_sentence(line: str) -> dict:
    """Deteksi tipe sentence lalu panggil parser yang sesuai."""
    if not line.startswith("$"):
        return None

    # Buang checksum (bagian setelah *) sebelum split
    line = line.split("*")[0]
    fields = line.split(",")

    sentence_type = fields[0][3:]  # buang '$GP' / talker ID, ambil 3 huruf tipe

    if sentence_type == "GGA":
        result = parse_gga(fields)
        if result:
            return {"type": "position", "data": result}

    elif sentence_type == "HDG":
        result = parse_hdg(fields)
        if result:
            return {"type": "heading", "data": result}

    return None


def gps_calc(num):
    print(f"Membuka {PORT} @ {BAUD_RATE} baud...")

    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=TIMEOUT)
    except serial.SerialException as e:
        print(f"Gagal membuka port serial: {e}")
        return

    print("Terhubung. Membaca data... (Ctrl+C untuk berhenti)\n")

    last_position = None
    last_heading = None

    try:
        while True:
            try:
                raw_line = ser.readline().decode("ascii", errors="ignore").strip()
            except UnicodeDecodeError:
                continue

            if not raw_line:
                continue

            parsed = parse_sentence(raw_line)
            if parsed is None:
                continue

            if parsed["type"] == "position":
                last_position = parsed["data"]
                print(
                    f"[POSISI] Lat: {last_position['latitude']:.6f}  "
                    f"Lon: {last_position['longitude']:.6f}  "
                    f"Fix: {last_position['fix_quality']}  "
                    f"Sat: {last_position['satellites']}"
                )
                client.publish("lat_nmea", str(f"{last_position['latitude']:.6f}"))
                client.publish("long_nmea", str(f"{last_position['longitude']:.6f}"))
                
            elif parsed["type"] == "heading":
                last_heading = parsed["data"]
                print(f"[COMPASS] Heading: {last_heading['heading']:.1f} derajat")
                client.publish("yaw_actual", str(int(last_heading['heading'])))

    except KeyboardInterrupt:
        print("\nBerhenti oleh user.")
    finally:
        ser.close()
        print("Port serial ditutup.")
        
        
def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))
    t = str(message.topic)

    if(msg[0] == 'c'):
        val =  1
    else:
        val = (msg)

if __name__ == "__main__":
    client= paho.Client("NMEA_GPS_PC")
    client.on_message=on_message

    print("connecting to broker ",broker)
    client.connect(broker,port)#connect
    print(broker," connected")
    
    client.loop_start()
    print("Subscribing")
    
    t1 = threading.Thread(target=gps_calc, args=(10,))
    t1.start()