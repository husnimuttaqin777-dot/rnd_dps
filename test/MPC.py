####### memanggil library PyQt5 ##################################
#----------------------------------------------------------------#
from PyQt5.QtCore import * 
from PyQt5.QtGui import * 
from PyQt5.QtQml import * 
from PyQt5.QtWidgets import *
from PyQt5.QtQuick import *  
import sys
import cvxpy as cp
from scipy.linalg import expm
import math
#----------------------------------------------------------------#

import numpy as np
from filterpy.kalman import KalmanFilter
import json



# Fungsi untuk membalik konversi koordinat ke dalam delta_x dan delta_y
def inverse_coordinate_conv(delta_lat, delta_lon):
    # Konversi perubahan dalam latitude dan longitude kembali ke dalam meter (dalam x dan y)
    delta_x = delta_lat * 111000  # Faktor konversi dari derajat ke meter (untuk latitude)
    delta_y = delta_lon * 111000  # Faktor konversi dari derajat ke meter (untuk longitude)
    return delta_x, delta_y
'''
# Misalkan kita sudah memiliki perubahan dalam koordinat (delta_lat, delta_lon)
delta_lat = 0.001  # Contoh perubahan latitude dalam derajat
delta_lon = 0.001  # Contoh perubahan longitude dalam derajat

# Balikkan perubahan koordinat menjadi delta_x dan delta_y
delta_x, delta_y = inverse_coordinate_conv(delta_lat, delta_lon)

# Masukkan ke dalam variabel y sesuai format yang diinginkan
y = [[delta_x], [delta_y]]

print(f"Delta X: {delta_x}, Delta Y: {delta_y}")
print(f"y: {y}")
'''

def shortest_psi(psi_ref, psi_d):
    psi_temp = (psi_ref-psi_d)%360
    psi_shortest = (psi_temp + 360) *-1 %360 
    if (psi_shortest > 180):
        psi_shortest = psi_shortest - 360
    return psi_shortest

start_lat = -6.215861
start_lon = 107.803706

latitude = -6.215861
latitude_dot = 0.00001
longitude = 107.803706
longitude_dot = 0.00001
yaw = 0


delta_lat = 0
delta_lon = 0
sp_lat = -6.215861
sp_lon = 107.803706
sp_yaw = 0

delta_x = 0.00001
delta_y = 0.0000
theta_dot = 1

x_dot = 0
y_dot = 0
eta = np.array([[x_dot], [y_dot], [yaw]])
V = np.array([[latitude_dot], [longitude_dot], [yaw]]) 

x_target = 0
y_target = 0


heading_error = 0

steering1 = 0
steering2 = 0
steering3 = 0
steering4 = 0

gas_throttle1 = 0
gas_throttle2 = 0
gas_throttle3 = 0
gas_throttle4 = 0




file_path = "state_space.json"

with open(file_path, 'r') as f:
    state_space = json.load(f)

# Mengambil matriks dari JSON dan mengkonversinya ke dalam format numpy array
A = np.array(state_space["A_discrete"])
B = np.array(state_space["B_discrete"])
C = np.array(state_space["C_discrete"])
D = np.array(state_space["D_discrete"])


print("Discrete state space : ")
print("A")
print(str(A))

print("B")
print(B)

print("C")
print(C)


print("D")
print(D)


# Matriks T untuk 4 baling-baling
T = np.array([[1, 0, 1, 0, 1, 0, 1, 0],   # Menambah kolom untuk F_x4
              [0, 1, 0, 1, 0, 1, 0, 1],   # Menambah kolom untuk F_y4
              [-0.25, 1, -0.25, -1, 0.25, -1, 0.25, 1]])  # Menyesuaikan gaya kontrol
#-ly1 lx1 -fy2 -fx2 fy3 -fx3 fy4 fx4

T_transpose = T.T
W = np.eye(8)
W_inv = np.linalg.inv(W)
TWT_inv = np.linalg.inv(T @ W_inv @ T_transpose)
T_pseudo_inverse = W_inv @ T_transpose @ TWT_inv
tau_control = np.array([0, 0, 10])

#State variable
N = 10  # Prediction horizon
#Q =  10000
Q = np.diag([10000, 10000, 10000])  # Penalty for output error (adjusted for 3 outputs)
R = np.diag([1, 1, 1])  # Penalty for control effort (adjusted for 3 inputs)
delta_u_penalty = np.diag([10, 10, 10])  # Penalti perubahan kontrol (adjusted for 3 inputs)
u_min, u_max = -50, 50  # Batas kontrol



x0 = np.array([[0], [0], [yaw], [0], [0], [0]])   # Status awal
print("x0 =", x0)
predicted_states = []
applied_inputs = []
time_steps = []
y = np.array([[0], [0.0], [0]])
y_ref = np.array([0, 0, 10]).reshape(-1, 1)

while True:
    
    j_theta = np.array([[np.cos(yaw * float(np.pi/180)), -np.sin(yaw * float(np.pi/180)), 0],
            [np.sin(yaw * float(np.pi/180)), np.cos(yaw* float(np.pi/180)), 0],
            [0, 0, 1]])
                
    try:
        n_error = round(meter_conversion(latitude, 0, float(sp_lat), 0))
        e_error = round(meter_conversion(longitude, 0, float(sp_lon), 0))
    except:
        n_error = 0
        e_error = 0
            

    #error_body_fixed = np.linalg.inv(j_theta) @ np.array([[n_error],[e_error],[yaw]])
    error_body_fixed = j_theta.T @ np.array([[n_error], [e_error], [yaw]])  # Gunakan .T

    x_error = (round(float(error_body_fixed[0]),1))
    y_error = (round(float(error_body_fixed[1]),1))
        
        
    x0[0:2] = 0 
    
    #y_ref = np.array([x_error, y_error, sp_yaw]).reshape(-1, 1)
        
    y_ref = np.array([0, 0, 10]).reshape(-1, 1)
    #y = np.array([delta_x], [delta_y])
    
    
    x = cp.Variable((A.shape[0], N + 1))  # State variables
    u = cp.Variable((B.shape[1], N))  # Control inputs


    cost = 0
    constraints = []

    for k in range(N):
        cost += cp.quad_form(C @ x[:, k] - y_ref.flatten(), Q)  # Penalti error (gunakan y_ref yang sudah direshape)
        cost += cp.quad_form(u[:, k], R)  # Penalti kontrol
        if k > 0:
            cost += cp.quad_form(u[:, k] - u[:, k - 1], delta_u_penalty)  # Penalti perubahan kontrol
        constraints += [x[:, k + 1] == A @ x[:, k] + B @ u[:, k]]
        constraints += [u_min <= u[:, k], u[:, k] <= u_max]

    # Status awal
    constraints += [x[:, 0] == x0.flatten()]

    # Problem MPC
    try:
        problem = cp.Problem(cp.Minimize(cost), constraints)
        problem.solve()
    except:
        print("solver not found")
        pass
    
    # ===== Ambil Kontrol Optimal =====
    if problem.status != 'optimal':
        print(f"Solver failed at step. Status: {problem.status}")
            
    try:
        u_optimal = u.value[:, 0]
    except:
        pass
    # ===== Simulasikan Sistem =====
    x0 = A @ x0 + B @ u_optimal.reshape(-1, 1)
    y = C @ x0
    
    
    tau_control = u_optimal
    f = T_pseudo_inverse @ tau_control
    print("==========")
    print("y_ref: ",np.round(y,decimals = 2))
    print("y: ",np.round(y,decimals = 2))
    
    try:
        steering1 = math.atan2(float(f[1]),float(f[0])) * 180/math.pi
    except:
        steering1 = 90        
    gas_throttle1 = math.sqrt(float(f[1])**2 + float(f[0])**2)

    try:
        steering2 = math.atan2(float(f[7]),float(f[6])) * 180/math.pi
    except:
        steering2 = 90
    gas_throttle2 = math.sqrt(float(f[7])**2 + float(f[6])**2)
        

    try:
        steering3 = math.atan2(float(f[3]),float(f[2])) * 180/math.pi
    except:
        steering3 = 90
    gas_throttle3 = math.sqrt(float(f[3])**2 + float(f[2])**2)

    try:
        steering4 = math.atan2(float(f[5]),float(f[4])) * 180/math.pi
    except:
        steering4 = 90
    gas_throttle4 = math.sqrt(float(f[5])**2 + float(f[4])**2)

    
    