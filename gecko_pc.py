import numpy as np
from mt_dxl import DxlAPI
import time

target_p = np.loadtxt("target_p.csv", delimiter=",")
target_v = np.loadtxt("target_v.csv", delimiter=",")
target_p[:, 1:7] = -target_p[:, 1:7]
target_v[:, 1:7] = -target_v[:, 1:7]
motor_group = DxlAPI(range(12), 'COM3')
# position initialize
motor_group.set_operating_mode('p')
motor_group.torque_enable()
for j in range(3):
    for i, item in enumerate(target_p):
        motor_group.set_position(item)
        time.sleep(0.005)
        if i == 0 and j == 0:
            time.sleep(5)
motor_group.torque_disable()
motor_group.portHandler.closePort()
