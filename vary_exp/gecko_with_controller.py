import numpy as np
import threading
from dynamixel.mt_dxl import DxlAPI
import time
from ds4 import DS4

def refresh_button_state():
    global button_state
    while 1:
        button_state = ds.get_button()

ds = DS4()
ds_threading = threading.Thread(target=refresh_button_state)
ds_threading.start()


target_p = np.loadtxt("target_p.csv", delimiter=",")
target_v = np.loadtxt("target_v.csv", delimiter=",")
target_para = np.loadtxt("target_para.csv", delimiter=",")
target_p[:, 3:9] = -target_p[:, 3:9]
target_v[:, 3:9] = -target_v[:, 3:9]
target_p[:, 4] = -target_p[:, 4]
target_v[:, 4] = -target_v[:, 4]
target_p[:, 10] = -target_p[:, 10]
target_v[:, 10] = -target_v[:, 10]
target_p[:, 5] = -target_p[:, 5]
target_v[:, 5] = -target_v[:, 5]
target_p[:, 11] = -target_p[:, 11]
target_v[:, 11] = -target_v[:, 11]
motor_group = DxlAPI(range(12), '/dev/ttyUSB0')
# position initialize
motor_group.set_operating_mode('p')
motor_group.torque_enable()
motor_group.set_position(target_p[0])

while 1:
    if button_state[1][3] == 1:
        break
    
mode_flag = 1

motor_group.torque_disable()
motor_group.set_operating_mode('t')
motor_group.torque_enable()

p_rec = []
v_rec = []
t_rec = []
calc_torque_rec = []
beta = np.array([[0.02], [0.01], [0.01], [0.02], [0.01], [0.01], [0.02], [0.01], [0.01], [0.02], [0.01], [0.01]])
# a = np.array([[2.0, 1.5, 7.0, 2.0, 1.5, 7.0, 2.0, 1.5, 7.0, 2.0, 1.5, 7.0]]) # cannot detach
a = np.array([[1.6, 1.5, 4.0, 1.6, 1.5, 4.0, 1.6, 1.5, 4.0, 1.6, 1.5, 4.0]])
b = np.array([[0.7, 0.8, 2.0, 0.7, 0.8, 2.0, 0.7, 0.8, 2.0, 0.7, 0.8, 2.0]])
TA = time.time()
while 1:
    if mode_flag == 1: # forward mode
        for i in range(target_p.shape[0]):
            t0 = time.time()
            v_t = target_v[i]
            p_t = target_p[i]
            t_p = motor_group.get_torque()
            v_p = motor_group.get_velocity()  # 1xn
            p_p = motor_group.get_position()  # 1xn
            v_e = np.array([v_p - v_t]).T  # velocity error nx1
            p_e = np.array([p_p - p_t]).T  # position error nx1
            tra_diff = p_e + beta * v_e  # track difference error(t) nx1
            co_diff = a / (1 + b * np.linalg.norm(tra_diff) ** 2)  # gamma(t) 1xn
            ff = tra_diff / co_diff.T  # force F(t) nx1
            # p_gain = np.dot(ff, p_e.T)  # nxn
            # d_gain = np.dot(ff, v_e.T)  # nxn
            # p_gain = ff * p_e  # nx1
            # d_gain = ff * v_e  # nx1
            p_gain = np.array([[0.010, 0.02, 0.01, 0.010, 0.02, 0.01, 0.010, 0.02, 0.01, 0.010, 0.02, 0.01]]).T
            d_gain = np.array([[0.010, 0.02, 0.01, 0.010, 0.02, 0.01, 0.010, 0.02, 0.01, 0.010, 0.02, 0.01]]).T
            # calc_torque = (-ff - np.dot(p_gain, p_e) - np.dot(d_gain, v_e)).T[0]  # (nx1).T[0]
            calc_torque = (-ff - p_gain * p_e - d_gain * v_e).T[0]

            motor_group.set_torque(calc_torque.tolist())
            v_rec.append(v_p)
            p_rec.append(p_p)
            t_rec.append(t_p)
            calc_torque_rec.append(calc_torque)
            t1 = time.time()
#            if (0.01-(t1-t0)) > 0:
#                time.sleep(0.01-(t1-t0))
#            print("Total time: %d, time for one period: %f" % (j, t1-t0))
    if mode_flag == 2:
        for i in range(10):
            t0 = time.time()
            v_t = np.array([0.0 for i in range(12)])
            p_t = target_p[0]
            t_p = motor_group.get_torque()
            v_p = motor_group.get_velocity()  # 1xn
            p_p = motor_group.get_position()  # 1xn
            v_e = np.array([v_p - v_t]).T  # velocity error nx1
            p_e = np.array([p_p - p_t]).T  # position error nx1
            tra_diff = p_e + beta * v_e  # track difference error(t) nx1
            co_diff = a / (1 + b * np.linalg.norm(tra_diff) ** 2)  # gamma(t) 1xn
            ff = tra_diff / co_diff.T  # force F(t) nx1
            # p_gain = np.dot(ff, p_e.T)  # nxn
            # d_gain = np.dot(ff, v_e.T)  # nxn
            # p_gain = ff * p_e  # nx1
            # d_gain = ff * v_e  # nx1
            p_gain = np.array([[0.010, 0.02, 0.01, 0.010, 0.02, 0.01, 0.010, 0.02, 0.01, 0.010, 0.02, 0.01]]).T
            d_gain = np.array([[0.010, 0.02, 0.01, 0.010, 0.02, 0.01, 0.010, 0.02, 0.01, 0.010, 0.02, 0.01]]).T
            # calc_torque = (-ff - np.dot(p_gain, p_e) - np.dot(d_gain, v_e)).T[0]  # (nx1).T[0]
            calc_torque = (-ff*target_para[i] - p_gain * p_e - d_gain * v_e).T[0]

            motor_group.set_torque(calc_torque.tolist())
            v_rec.append(v_p)
            p_rec.append(p_p)
            t_rec.append(t_p)
            calc_torque_rec.append(calc_torque)
            t1 = time.time()
    if mode_flag == 1 and button_state[1][1] == 1:
        mode_flag = 2
    if mode_flag == 2 and button_state[1][3] == 1:
        mode_flag = 1
    if button_state[1][2] == 1:
        break

motor_group.torque_disable()
motor_group.portHandler.closePort()

TB = time.time()
p_rec = np.array(p_rec)
v_rec = np.array(v_rec)
calc_torque_rec = np.array(calc_torque_rec)
t_rec = np.array(t_rec)
print(TB-TA)

np.savetxt('p_rec.csv', p_rec, delimiter=',')
np.savetxt('t_rec.csv', t_rec, delimiter=',')
np.savetxt('calc_torque_rec.csv', calc_torque_rec, delimiter=',')
