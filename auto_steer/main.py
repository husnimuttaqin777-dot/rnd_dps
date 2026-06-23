import numpy as np

steer_dir = (["CW","CW","CCW","CCW"])
def shortest_psi(psi_ref, psi_d):
    psi_temp = (psi_ref-psi_d)%360
    psi_shortest = (psi_temp + 360) *-1 %360 
    if (psi_shortest > 180):
        psi_shortest = psi_shortest - 360
    return psi_shortest   

def steering_direction(error, direction, deadband=5):
    if abs(error) <= deadband:
        return "S"
    cmd = np.sign(error)
    if direction == "CW":
        cmd *= -1

    return "L" if cmd > 0 else "R"

error = (shortest_psi(10,0))

print(steering_direction(error, steer_dir[0]))