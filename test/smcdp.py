import numpy as np
import math
import matplotlib.pyplot as plt

# Parameter Kapal dan Lingkungan
phi = math.pi
mass = 1000  # Massa kapal (kg)
Iz = 2000    # Momen inersia kapal
X_udot = -22665
Y_vdot = -275927
X_u = -1000
Y_v = -1500
N_r = 50

# Posisi Kapal dan Waypoint
x_current = 0
y_current = 0
yaw_current = 0  # dalam radian
x_waypoint = 10
y_waypoint = -10
yaw_waypoint = 0  # dalam radian

# Kecepatan Kapal
x_dot = 0
y_dot = 0
yaw_dot = 0

# Matriks Sliding Mode Control
R = np.array([[8000, 0, 0], [0, 8000, 0], [0, 0, 8000]])  # Gaya dorong
E = np.array([[20, 0, 0], [0, 20, 0], [0, 0, 20]])         # Matrix kontrol

# Matriks Lyapunov
lyapunov_gain_matrix = np.array([[0.32, 0, 0], [0, 0.32, 0], [0, 0, 0.16]])

# Fungsi Transformasi Rotasi (J)
def J(psi):
    return np.array([[math.cos(psi), math.sin(psi), 0],
                     [-math.sin(psi), math.cos(psi), 0],
                     [0, 0, 1]])

# Fungsi Penghitungan Error
def calculate_errors(x_current, y_current, yaw_current, x_waypoint, y_waypoint, yaw_waypoint):
    x_error = x_current - x_waypoint
    y_error = y_current - y_waypoint
    psi_error = yaw_current - yaw_waypoint
    return x_error, y_error, psi_error

# Fungsi Sliding Mode Control (SMC)
def sliding_mode_control(x_error, y_error, psi_error, x_dot, y_dot, yaw_dot):
    # Penghitung Gaya dan Momen (sistem dinamis kapal)
    control_signal = np.array([[x_error], [y_error], [psi_error]])  # Signal kontrol
    
    # Sliding surface (termasuk kontrol switching)
    sliding_surface = np.dot(lyapunov_gain_matrix, control_signal)  # Menghitung permukaan sliding
    
    # Komponen kontrol sliding mode
    switching_control = -np.sign(sliding_surface) * np.abs(sliding_surface)  # Kontrol switching
    
    # Menghasilkan sinyal kontrol yang akan menggerakkan thruster
    return switching_control

# Fungsi Penghitung Thrust (Sederhana)
def calculate_thrust(switching_control):
    thrust = switching_control  # Gunakan switching control untuk menghitung thrust
    return thrust

# Fungsi Utama untuk Simulasi
def run_simulation():
    global x_current, y_current, yaw_current
    time_steps = 100  # 100 iterasi untuk simulasi
    x_positions = []
    y_positions = []
    yaw_positions = []

    # Iterasi simulasi
    for t in range(time_steps):  
        # Hitung error posisi dan arah
        x_error, y_error, psi_error = calculate_errors(x_current, y_current, yaw_current, x_waypoint, y_waypoint, yaw_waypoint)
        
        # Terapkan Sliding Mode Control
        switching_control = sliding_mode_control(x_error, y_error, psi_error, x_dot, y_dot, yaw_dot)
        
        # Hitung thrust berdasarkan kontrol switching
        thrust = calculate_thrust(switching_control)
        
        # Perbarui posisi dan arah kapal
        x_current -= thrust[0][0] * 0.1  # Update posisi x (contoh pergerakan berdasarkan thrust)
        y_current -= thrust[1][0] * 0.1  # Update posisi y
        yaw_current -= thrust[2][0] * 0.1  # Update yaw (arah kapal)
        
        # Simpan posisi kapal untuk plotting
        x_positions.append(x_current)
        y_positions.append(y_current)
        yaw_positions.append(yaw_current)
        
        # Cetak status (opsional)
        if t % 10 == 0:
            print(f"Time: {t}, Position: ({x_current:.2f}, {y_current:.2f}), Yaw: {yaw_current:.2f}, Thrust: {thrust.T}")
    
    # Plot posisi kapal selama simulasi
    plt.figure(figsize=(10, 6))
    plt.plot(x_positions, y_positions, label="Trajectory")
    plt.scatter(x_waypoint, y_waypoint, color='red', label="Waypoint")
    plt.title("Ship Trajectory with Sliding Mode Control")
    plt.xlabel("X Position (m)")
    plt.ylabel("Y Position (m)")
    plt.legend()
    plt.grid(True)
    plt.show()

# Mulai simulasi
run_simulation()
