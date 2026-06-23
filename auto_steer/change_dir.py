import numpy as np

steer_dir = (["CW","CW","CCW","CCW"])


def dir_check(command, direction):
    if (direction == "CCW"):
        if (command == "Kanan"):
            return "Kiri"
        if (command == "Kiri"):
            return "Kanan"
    else:
        return command



print(dir_check("Kanan", steer_dir[0]))
