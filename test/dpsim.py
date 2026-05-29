# dynamic_positioning_system.py

import time
import math
from random import uniform

class SensorData:
    def __init__(self, position_x, position_y, heading, wind_speed, wind_direction, current_speed, current_direction):
        self.position_x = position_x
        self.position_y = position_y
        self.heading = heading
        self.wind_speed = wind_speed
        self.wind_direction = wind_direction
        self.current_speed = current_speed
        self.current_direction = current_direction

    def __str__(self):
        return (f"Position: ({self.position_x:.2f}, {self.position_y:.2f}), "
                f"Heading: {self.heading:.2f} deg, "
                f"Wind: {self.wind_speed:.2f} m/s at {self.wind_direction:.2f} deg, "
                f"Current: {self.current_speed:.2f} m/s at {self.current_direction:.2f} deg")

class ActuatorCommands:
    def __init__(self, thruster_forces=None, rudder_angle=0.0):
        if thruster_forces is None:
            self.thruster_forces = [0.0] * 3  # Assuming 3 thrusters for simplicity (surge, sway, yaw)
        else:
            self.thruster_forces = thruster_forces
        self.rudder_angle = rudder_angle

    def __str__(self):
        return f"Thruster Forces: {self.thruster_forces}, Rudder Angle: {self.rudder_angle:.2f} deg"

class DynamicPositioningSystem:
    def __init__(self, target_x, target_y, target_heading, dt=0.1):
        self.target_x = target_x
        self.target_y = target_y
        self.target_heading = target_heading
        self.dt = dt  # Time step for simulation
        self.current_state = SensorData(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        self.actuator_commands = ActuatorCommands()
        self.integral_error_x = 0.0
        self.integral_error_y = 0.0
        self.integral_error_heading = 0.0

        # PID control gains (to be tuned)
        self.Kp_x = 1.0
        self.Ki_x = 0.1
        self.Kd_x = 0.5

        self.Kp_y = 1.0
        self.Ki_y = 0.1
        self.Kd_y = 0.5

        self.Kp_heading = 2.0
        self.Ki_heading = 0.2
        self.Kd_heading = 1.0

        # Vessel parameters (simplified)
        self.mass = 30.0
        self.inertia_z = 50.0
        self.damping_surge = 5.0
        self.damping_sway = 10.0
        self.damping_yaw = 20.0

        # Thruster configuration (simplified - forces in surge, sway, yaw)
        self.thruster_allocator = [[1.0, 0.0, 0.0],  # Thruster 1 (Surge)
                                  [0.0, 1.0, 0.0],  # Thruster 2 (Sway)
                                  [0.0, 0.0, 1.0]]  # Thruster 3 (Yaw moment)

        self.max_thrust = 100.0

    def update_sensors(self):
        # Simulate sensor readings with some noise
        self.current_state.position_x += self.dt * (self.actuator_commands.thruster_forces[0] / self.mass - self.damping_surge / self.mass * self.current_state.position_x + uniform(-0.1, 0.1))
        self.current_state.position_y += self.dt * (self.actuator_commands.thruster_forces[1] / self.mass - self.damping_sway / self.mass * self.current_state.position_y + uniform(-0.1, 0.1))
        self.current_state.heading += self.dt * (self.actuator_commands.thruster_forces[2] / self.inertia_z - self.damping_yaw / self.inertia_z * self.current_state.heading + uniform(-0.01, 0.01))
        self.current_state.heading = math.fmod(self.current_state.heading + math.pi, 2 * math.pi) - math.pi # Normalize to [-pi, pi]

        # Simulate environmental disturbances (simplified)
        self.current_state.wind_speed = uniform(0.0, 5.0)
        self.current_state.wind_direction = uniform(-math.pi, math.pi)
        self.current_state.current_speed = uniform(0.0, 1.0)
        self.current_state.current_direction = uniform(-math.pi, math.pi)

    def calculate_control_forces(self):
        # Calculate errors
        error_x = self.target_x - self.current_state.position_x
        error_y = self.target_y - self.current_state.position_y
        error_heading = self.target_heading - self.current_state.heading
        error_heading = math.fmod(error_heading + math.pi, 2 * math.pi) - math.pi # Normalize error

        # Integrate errors
        self.integral_error_x += error_x * self.dt
        self.integral_error_y += error_y * self.dt
        self.integral_error_heading += error_heading * self.dt

        # PID control for X position (Surge)
        force_x = (self.Kp_x * error_x +
                   self.Ki_x * self.integral_error_x +
                   self.Kd_x * (error_x - self.last_error_x) / self.dt if hasattr(self, 'last_error_x') else 0.0)
        self.last_error_x = error_x

        # PID control for Y position (Sway)
        force_y = (self.Kp_y * error_y +
                   self.Ki_y * self.integral_error_y +
                   self.Kd_y * (error_y - self.last_error_y) / self.dt if hasattr(self, 'last_error_y') else 0.0)
        self.last_error_y = error_y

        # PID control for Heading (Yaw moment)
        moment_z = (self.Kp_heading * error_heading +
                    self.Ki_heading * self.integral_error_heading +
                    self.Kd_heading * (error_heading - self.last_error_heading) / self.dt if hasattr(self, 'last_error_heading') else 0.0)
        self.last_error_heading = error_heading

        # Simple mapping of control forces to actuator commands (to be improved with thrust allocation)
        self.actuator_commands.thruster_forces = [force_x, force_y, moment_z]

        # Limit thruster forces
        for i in range(len(self.actuator_commands.thruster_forces)):
            self.actuator_commands.thruster_forces[i] = max(-self.max_thrust, min(self.max_thrust, self.actuator_commands.thruster_forces[i]))

    def step(self):
        self.update_sensors()
        self.calculate_control_forces()
        print(f"Time: {time.time():.2f}")
        print(f"Sensor Data: {self.current_state}")
        print(f"Actuator Commands: {self.actuator_commands}")
        print(f"Target: Position({self.target_x:.2f}, {self.target_y:.2f}), Heading({math.degrees(self.target_heading):.2f} deg)")
        print("-" * 30)
        time.sleep(self.dt)

    def set_target(self, target_x, target_y, target_heading):
        self.target_x = target_x
        self.target_y = target_y
        self.target_heading = target_heading
        self.integral_error_x = 0.0
        self.integral_error_y = 0.0
        self.integral_error_heading = 0.0

if __name__ == "__main__":
    # Define target position and heading
    target_x = 10.0
    target_y = 5.0
    target_heading_rad = math.radians(45.0)

    # Create a DP system instance
    dp_system = DynamicPositioningSystem(target_x, target_y, target_heading_rad, dt=0.5)

    # Simulate the DP system for a while
    simulation_duration = 10000000
    start_time = time.time()
    while time.time() - start_time < simulation_duration:
        dp_system.step()

    # Change target
    print("\nChanging Target...\n")
    dp_system.set_target(-5.0, 12.0, math.radians(-30.0))
    start_time = time.time()
    while time.time() - start_time < simulation_duration:
        dp_system.step()