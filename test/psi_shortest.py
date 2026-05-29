psi_ref = float(input("insert compass value : "))
psi_d = float(input("insert setpoint value : "))
psi_temp = (psi_ref-psi_d)%360
psi_shortest = (psi_temp + 360) *-1 %360 
if (psi_shortest > 180):
    psi_shortest = psi_shortest - 360
    
print(psi_shortest)