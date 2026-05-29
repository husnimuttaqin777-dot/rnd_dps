import numpy as np
import matplotlib.pyplot as plt
import time

# === Fungsi untuk mencari titik potong dengan arah tertentu ===
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

        # Cek arah pancaran sinar: harus searah v_theta
        direction_vec = intersection - np.array(P)
        if np.dot(direction_vec, v_theta) < 0:
            return None

        # Cek apakah titik potong berada dalam segmen AB
        if not (0 <= s <= 1):
            return None

        return intersection
    except np.linalg.LinAlgError:
        return None

# === Data koordinat garis (jalur) ===
x = np.array([108.998837, 108.997869, 108.997261, 108.996855, 108.996634, 108.996303,
              108.995905, 108.995424, 108.995217, 108.994877, 108.993900, 108.993432, 108.993341])

y = np.array([-7.743055, -7.743775, -7.744123, -7.744329, -7.744441, -7.744598,
              -7.744754, -7.744933, -7.744985, -7.745072, -7.745401, -7.745446, -7.745456])


# Hitung perbedaan antar titik
dx = np.diff(x)
dy = np.diff(y)

# Hitung sudut kemiringan (dalam radian) lalu konversi ke derajat
angles_rad = np.arctan2(dy, dx)
angles_deg = np.degrees(angles_rad)

print("Sudut kemiringan antar titik (dalam derajat):")
print(angles_deg)

# === Titik asal dan arah pancaran sinar ===
P = np.array([108.994285, -7.745061])
theta_deg = -80  # arah utara

# === Offset agar titik P jadi (0,0) untuk keperluan plotting ===
x_offset = x - P[0]
y_offset = y - P[1]
P_offset = np.array([0, 0])

# === Inisialisasi plot ===
plt.figure(figsize=(8, 6))
intersection_points = []
lines_with_intersection = []

start_time = time.time()

# === Proses tiap segmen garis ===
num_lines = len(x) - 1
for i in range(num_lines):
    A = np.array([x[i], y[i]])
    B = np.array([x[i + 1], y[i + 1]])
    A_offset = A - P
    B_offset = B - P

    # Gambar garis
    plt.plot([A_offset[0], B_offset[0]], [A_offset[1], B_offset[1]], 'k-', label=f"Garis {i+1}" if i == 0 else "")

    # Cek titik potong
    intersection = find_intersection_theta(A, B, P, theta_deg)
    if intersection is not None:
        intersection_points.append(intersection)
        lines_with_intersection.append(i + 1)
        inter_offset = intersection - P
        plt.plot(inter_offset[0], inter_offset[1], 'ro', label=f"Titik potong Garis {i+1}")
        print(f"Titik potong (Garis {i+1}): {intersection}")

        elapsed_time = time.time() - start_time
        print("Waktu komputasi: {:.6f} detik".format(elapsed_time))

        # === Gambar titik P ===
        plt.plot(0, 0, 'go', label="Titik P")

        # === Gambar arah sinar (dashed line) ===
        v_theta = np.array([np.cos(np.radians(theta_deg)), np.sin(np.radians(theta_deg))])
        ray_end = 0.001 * v_theta  # Panjang sinar
        plt.plot([0, ray_end[0]], [0, ray_end[1]], 'b--', label=f"Arah θ = {theta_deg}°")

        # === Finishing plot ===
        plt.title("Deteksi Titik Potong antara Beam dan Jalur")
        plt.xlabel("Longitude (offset)")
        plt.ylabel("Latitude (offset)")
        plt.grid(True)
        plt.axis('equal')
        plt.legend()
        plt.show()

# === Hasil akhir ===
if intersection_points:
    for idx, point in zip(lines_with_intersection, intersection_points):
        print(f"→ Titik potong dengan arah {theta_deg}° pada Garis {idx}: {point}")
else:
    print(f"Tidak ditemukan titik potong dengan arah {theta_deg}° pada garis manapun.")
