import numpy as np
import matplotlib.pyplot as plt

# Parameter motor DC
R = 1  # Resistansi (ohm)
L = 0.5  # Induktansi (H)
K_e = 0.01  # Konstanta back-EMF (V/rpm)
K_t = 0.01  # Konstanta torsi (Nm/A)
J = 0.01  # Momen inersia rotor (kg.m^2)
B = 0.1  # Koefisien gesekan (Nms)
V_max = 12  # Tegangan maksimum motor (volt)

# Kecepatan yang diinginkan (desired speed)
omega_desired = 100  # rpm

# Waktu simulasi
t_final = 10  # Detik
dt = 0.01  # Interval waktu (detik)
time = np.arange(0, t_final, dt)

# Variabel status motor
omega = 0  # Kecepatan motor awal (rpm)
i = 0  # Arus motor awal (A)
V = 0  # Tegangan input motor

# Fungsi Sliding Mode Control (SMC)
def sliding_mode_control(omega_actual, omega_desired, K):
    # Error kecepatan
    s = omega_desired - omega_actual
    
    # Kontrol Switching
    u = -K * np.sign(s)
    
    return u

# Fungsi sistem motor DC
def motor_dynamics(omega, i, V):
    # Persamaan sistem motor DC
    d_omega = (K_t * i - B * omega) / J  # Persamaan mekanik
    di = (V - R * i - K_e * omega) / L  # Persamaan listrik
    
    return d_omega, di

# Simulasi motor DC dengan SMC
omega_vals = []  # Menyimpan nilai kecepatan motor
i_vals = []  # Menyimpan nilai arus motor

for t in time:
    # Terapkan kontrol SMC
    V = sliding_mode_control(omega, omega_desired, K=-10000)
    
    # Simulasikan dinamika motor DC
    d_omega, di = motor_dynamics(omega, i, V)
    
    # Update status motor
    omega += d_omega * dt
    i += di * dt
    
    # Simpan hasil
    omega_vals.append(omega)
    i_vals.append(i)

# Plot hasil simulasi
plt.figure(figsize=(12, 6))

# Plot Kecepatan Motor (omega)
plt.subplot(2, 1, 1)
plt.plot(time, omega_vals, label='Kecepatan Motor (rpm)', color='blue')
plt.axhline(y=omega_desired, color='r', linestyle='--', label='Kecepatan yang Diinginkan')
plt.title('Simulasi Sliding Mode Control pada Motor DC')
plt.xlabel('Waktu (detik)')
plt.ylabel('Kecepatan (rpm)')
plt.legend()
plt.grid()

# Plot Arus Motor (i)
plt.subplot(2, 1, 2)
plt.plot(time, i_vals, label='Arus Motor (A)', color='green')
plt.title('Arus Motor DC')
plt.xlabel('Waktu (detik)')
plt.ylabel('Arus (A)')
plt.grid()

plt.tight_layout()
plt.show()
