import numpy as np, math
from numpy.linalg import lstsq

# Pasangkan data: [heading_true_deg, heading_measured_deg]
data = np.array([
    [0, 252],
    [90, 186],
    [180, 87],
    [270, -33],
   
])
heading_true = data[:,0]
heading_meas = data[:,1]

# Unwrap di domain radian supaya tidak ganggu discontinuity 360->0
meas_rad = np.deg2rad(heading_meas)
true_rad = np.deg2rad(heading_true)
meas_unwrap = np.unwrap(meas_rad)
true_unwrap = np.unwrap(true_rad)

# Fit quadratic: true_unwrap = a*y^2 + b*y + c  (y in radians)
Y = meas_unwrap
A = np.vstack([Y**2, Y, np.ones_like(Y)]).T
coeffs_rad, *_ = lstsq(A, true_unwrap, rcond=None)
a_rad, b_rad, c_rad = coeffs_rad

# Convert to degree-domain coefficients for direct use on degrees:
factor = 180.0/math.pi
A_deg = a_rad * (math.pi/180.0)**2 * factor
B_deg = b_rad * (math.pi/180.0) * factor
C_deg = c_rad * factor

print("A_deg, B_deg, C_deg =", A_deg, B_deg, C_deg)

# fungsi bantu: terapkan dan normalisasi
def apply_quad_deg(y_deg):
    h = A_deg * y_deg*y_deg + B_deg * y_deg + C_deg
    h = (h % 360.0 + 360.0) % 360.0
    return h

# Tampilkan hasil uji
for t, y in zip(heading_true, heading_meas):
    f = apply_quad_deg(y)
    err = ((f - t + 180) % 360) - 180
    print(f"True {t:3.0f}°, Meas {y:7.2f}° -> Fitted {f:7.2f}°, err {err:6.2f}°")
