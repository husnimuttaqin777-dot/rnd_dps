import numpy as np
import matplotlib.pyplot as plt
import time
from math import sqrt

elapsed_time = time.time()
elapsed_time_prev = time.time()

distance = 0

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


def meter_conversion(lat1, long1, lat2, long2):
    delta_lat = (lat1 - lat2)*111000
    delta_lon = (long1 - long2)*111000
    distance = sqrt(pow(delta_lat, 2) +  pow(delta_lon, 2))
    return distance

# === DATA KOORDINAT GARIS ===
x = np.array([108.998837, 108.997869, 108.997261, 108.996855, 108.996634, 108.996303,
              108.995905, 108.995424, 108.995217, 108.994877, 108.993900, 108.993432, 108.993341])

y = np.array([-7.743055, -7.743775, -7.744123, -7.744329, -7.744441, -7.744598,
              -7.744754, -7.744933, -7.744985, -7.745072, -7.745401, -7.745446, -7.745456])

# === TITIK ASAL RAY DAN ARAHNYA ===
P = np.array([108.994285, -7.745061])
#P = np.array([108.994285,    -7.74538235])

heading = -80
theta_deg = 360 - (heading + 90)  # ke atas


# OFFSET semua titik relatif terhadap P agar bisa diplot dengan jelas
x_offset = x - P[0]
y_offset = y - P[1]
P_offset = np.array([0, 0])

# === PLOT ===
plt.figure(figsize=(8, 6))
intersection_points = []
lines_with_intersection = []


elapsed_time_prev = time.time()


num_lines = len(x) - 1
for i in range(num_lines):
    A = np.array([x[i], y[i]])
    B = np.array([x[i + 1], y[i + 1]])
    A_offset = A - P
    B_offset = B - P

    plt.plot([A_offset[0], B_offset[0]], [A_offset[1], B_offset[1]], 'k-', label=f"Garis {i+1}" if i == 0 else "")

    intersection = find_intersection_theta(A, B, P, theta_deg - 90)
    if intersection is not None:
        intersection_points.append(intersection)
        lines_with_intersection.append(i + 1)
        inter_offset = intersection - P
        plt.plot(inter_offset[0], inter_offset[1], 'ro', label=f"Titik potong Garis {i+1}")
        print(f"Titik potong (Garis {i+1}):", intersection)
        print("kanan")
        print(intersection[1], intersection[0])
        print(P[1], P[0])
        distance = meter_conversion(intersection[1], intersection[0], P[1], P[0])
        
    
    intersection = find_intersection_theta(A, B, P, theta_deg + 90)
    if intersection is not None:
        intersection_points.append(intersection)
        lines_with_intersection.append(i + 1)
        inter_offset = intersection - P
        plt.plot(inter_offset[0], inter_offset[1], 'ro', label=f"Titik potong Garis {i+1}")
        print(f"Titik potong (Garis {i+1}):", intersection)
        print("kiri")
        
    
        distance = meter_conversion(float(intersection[1]), float(intersection[0]), float(P[1]), float(P[0]))
    

    elapsed_time = time.time() - elapsed_time_prev

print("waktu komputasi : ", elapsed_time)
print("jarak", float(distance))
# Titik P
plt.plot(0, 0, 'go', label="Titik P")

# Arah theta (garis putus-putus biru)
v_theta =  np.array([np.cos(np.radians(theta_deg - 180)), np.sin(np.radians(theta_deg - 180))])
ray_end = 0 + 0 + 0.001 * v_theta  # Panjang ray = 0.001 derajat
plt.plot([0, ray_end[0]], [0, ray_end[1]], 'b--', label=f"Arah θ = {theta_deg}°")

plt.title("Deteksi Titik Potong Beam dengan Jalur")
plt.xlabel("Longitude (offset)")
plt.ylabel("Latitude (offset)")
plt.grid(True)
plt.axis('equal')
plt.legend()
plt.show()

# Cetak hasil
if intersection_points:
    for idx, point in zip(lines_with_intersection, intersection_points):
        print(f"→ Titik potong dengan arah {theta_deg}° pada Garis {idx}: {point}")
