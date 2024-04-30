# from position_solver import PositionSolver
# import numpy as np
# import cv2
# po=PositionSolver()
# points_3D = np.array([[-1, 1, 0],
#                       [1, 1, 0],
#                       [-1,-1, 0],
#                       [1,-1, 0]], dtype=np.float64)


# points_2D= np.empty([0,2],dtype=np.float64)
# points_new=np.array([1,2],dtype=np.float64)
# points_2D=np.vstack((points_2D,points_new))
# points_2D=np.vstack((points_2D,points_new))
# # points_2D=np.append(points_2D,[points_new],axis=0)
# print(points_3D)

# fx = 610.32366943
# fy = 610.5026245
# cx = 313.3859558
# cy = 237.2507269
# K = np.array([[fx, 0, cx],
#               [0, fy, cy],
#               [0, 0, 1]], dtype=np.float64)

# distCoeffs =None
# R, t=po.my_pnp(points_3D,points_2D,K,distCoeffs)

# print(t)

# print(t[2])


# #####################################################寻找两个圆的交点#############################
# import numpy as np
# import matplotlib.pyplot as plt

# def calculate_circle_intersections(center1, center2, radius):
#     d = np.linalg.norm(np.array(center2) - np.array(center1))

#     if d > 2 * radius:
#         return None  # 两个圆不相交
#     else:
#         a = (radius ** 2 - radius ** 2 + d ** 2) / (2 * d)
#         h = np.sqrt(radius ** 2 - a ** 2)

#         x2 = center1[0] + a * (center2[0] - center1[0]) / d
#         y2 = center1[1] + a * (center2[1] - center1[1]) / d

#         intersection1 = (x2 + h * (center2[1] - center1[1]) / d, y2 - h * (center2[0] - center1[0]) / d)
#         intersection2 = (x2 - h * (center2[1] - center1[1]) / d, y2 + h * (center2[0] - center1[0]) / d)

#         return intersection1, intersection2


# # 初始化画布
# radius = 10
# fig, ax = plt.subplots()
# ax.set_xlim(-50, 50)
# ax.set_ylim(-50, 50)
# ax.set_aspect('equal', adjustable='box')
# ax.grid(True)

# circle1 = plt.Circle((0, 0), radius, fill=False, color='r')
# circle2 = plt.Circle((0, 0), radius, fill=False, color='b')
# ax.add_patch(circle1)
# ax.add_patch(circle2)

# intersections, = ax.plot([], [], 'ro')

# # 主程序
# while True:
#     # 生成随机的圆心1和圆心2位置在圆心坐标为（0, 0）的半径为r的圆上
#     angle1 = np.random.rand() * 2 * np.pi  # 随机生成角度
#     angle2 = np.random.rand() * 2 * np.pi  # 随机生成角度

#     center1 = [radius * np.cos(angle1), radius * np.sin(angle1)]
#     center2 = [radius * np.cos(angle2), radius * np.sin(angle2)]

#     print(center1, center2)
#     intersections_data = calculate_circle_intersections(center1, center2, radius)

#     if intersections_data is not None:
#         x_data, y_data = zip(*intersections_data)
#         intersections.set_data(x_data, y_data)

#     # 更新圆的位置
#     circle1.center = center1
#     circle2.center = center2

#     # 更新画布
#     plt.draw()
#     plt.pause(0.1)



# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.optimize import minimize

# # 假设你有一组数据点 
# data_points =[[-28, 1400], [-41, 1439], [-45, 1447], [-64, 1487], [-69, 1508], [-56, 1484], [-48, 1469], [-15, 1426], [-5, 1390], [30, 1379], [39, 1382], [69, 1413], [62, 1404], [29, 1364], [21, 1361], [-6, 1372], [-13, 1380], [-38, 1424], [-45, 1431], [-71, 1489]]

# # 定义圆的方程
# def circle_equation(params, x, y, r):
#     xc, yc = params
#     return (x - xc)**2 + (y - yc)**2 - r**2

# # 定义损失函数，即残差的平方和
# def residual(params, x, y, r):
#     xc, yc = params
#     return np.sum(circle_equation([xc, yc], x, y, r)**2)

# # 初始化圆心的初始值
# initial_guess = [0, 0]  # 假设初始值为圆心在原点

# # 固定圆的半径为 300
# fixed_radius = 300

# # 从数据点中提取 x 和 y 坐标
# x_data = [point[0] for point in data_points]
# y_data = [point[1] for point in data_points]

# # 最小化损失函数，只优化圆心的位置参数
# result = minimize(residual, initial_guess, args=(x_data, y_data, fixed_radius))

# # 获取拟合后的圆心坐标
# fitted_circle_center = result.x
# fitted_xc, fitted_yc = fitted_circle_center

# print("拟合圆心坐标：", fitted_xc, fitted_yc)
# print("固定圆半径为：", fixed_radius)

# # 绘制数据点
# x_data_plot = np.array(x_data)
# y_data_plot = np.array(y_data)
# plt.scatter(x_data_plot, y_data_plot, label='Data Points')

# # 绘制拟合的圆
# circle = plt.Circle((fitted_xc, fitted_yc), fixed_radius, color='r', fill=False, label='Fitted Circle')
# plt.gca().add_patch(circle)

# # 设置图例和标签
# plt.legend()
# plt.xlabel('X')
# plt.ylabel('Y')
# plt.title('Fitted Circle and Data Points')
# plt.axis('equal')  # 确保 x 和 y 的比例相等
# plt.grid(True)
# plt.show()

import numpy as np
import matplotlib.pyplot as plt

# 角速度
angular_velocity = 3  # rad/s

# 时间间隔
dt = 0.5  # s

# 状态转移矩阵 A
A = np.array([[1, -angular_velocity * dt],
              [angular_velocity * dt, 1]])

# 观测矩阵 H
H = np.array([[0, 1]])

# 过程噪声协方差矩阵 Q
Q = np.array([[0.001, 0],
              [0, 0.001]])

# 测量噪声协方差矩阵 R
R = np.array([[0.1]])

# 初始状态
x = np.array([[np.pi/4],   # 初始位置与 y 轴夹角，假设为 pi/4
              [0]])        # 初始速度设为 0

# 初始状态协方差矩阵 P
P = np.eye(2)  # 协方差矩阵，假设为单位矩阵

# 观测值列表
measurement_list = []

# 预测值列表
prediction_list = []

# 定义卡尔曼滤波函数
def kalman_filter(x, P, y):
    # 预测步骤
    x_pred = np.dot(A, x)
    P_pred = np.dot(np.dot(A, P), A.T) + Q

    # 更新步骤
    K = np.dot(np.dot(P_pred, H.T), np.linalg.inv(np.dot(np.dot(H, P_pred), H.T) + R))
    x = x_pred + np.dot(K, (y - np.dot(H, x_pred)))
    P = P_pred - np.dot(np.dot(K, H), P_pred)
    
    return x, P

# 绘制射线函数
def plot_ray(angle, length, label):
    x = length * np.cos(angle)
    y = length * np.sin(angle)
    plt.plot([0, x], [0, y], label=label)


# 用卡尔曼滤波预测10个时间步
for i in range(100):
    # 生成观测值，假设为 pi/3
    y = np.array([[np.pi/3]])
    
    # 记录观测值
    measurement_list.append(y[0, 0])
    
    # 卡尔曼滤波
    x, P = kalman_filter(x, P, y)
    
    # 记录预测值
    prediction_list.append(x[0, 0])

# 生成时间序列
time_steps = np.arange(0, 100) * dt

# 绘制观测值和预测值
plt.plot(time_steps, measurement_list, label='Measurement', marker='o')
plt.plot(time_steps, prediction_list, label='Prediction', marker='x')

plt.xlabel('Time')
plt.ylabel('Angle with Y-axis')
plt.title('Kalman Filter Prediction vs Measurement')
plt.legend()
plt.grid(True)
plt.show()




# # 第1步:基于k-1时刻的后验估计值X_posterior建模预测k时刻的系统状态先验估计值X_prior
# # 此时模型控制输入U=0
# X_prior = np.dot(self.A, self.X_posterior)

# # print(self.X_posterior)

# # 把k时刻先验预测值赋给两个状态分量的先验预测值 speed_prior_est = X_prior[1,0];position_prior_est=X_prior[0,0]
# # 再利用append函数把每次循环迭代后的分量值拼接成一个完整的数组
# self.speed_prior_est.append(X_prior[1,0])
# self.position_prior_est.append(X_prior[0,0])

# # 第2步:基于k-1时刻的误差ek-1的协方差矩阵P_posterior和过程噪声w的协方差矩阵Q 预测k时刻的误差的协方差矩阵的先验估计值 P_prior
# P_prior_1 = np.dot(self.A, self.P_posterior)
# P_prior = np.dot(P_prior_1, self.A.T) + self.Q

# # --------------------进行状态更新-----------------------------
# # 第3步:计算k时刻的卡尔曼增益K
# k1 = np.dot(P_prior, self.H.T)
# k2 = np.dot(self.H, k1) + self.R
# #k3 = np.dot(np.dot(H, P_prior), H.T) + R  k2和k3是两种写法，都可以
# K = np.dot(k1, np.linalg.inv(k2))

# # 第4步:利用卡尔曼增益K 进行校正更新状态，得到k时刻的后验状态估计值 X_posterior
# X_posterior_1 = Z_measure -np.dot(self.H, X_prior)
# self.X_posterior = X_prior + np.dot(K, X_posterior_1)

# # 把k时刻后验预测值赋给两个状态分量的后验预测值 speed_posterior_est = X_posterior[1,0];position_posterior_est = X_posterior[0,0]
# self.speed_posterior_est.append(self.X_posterior[1,0])
# self.position_posterior_est.append(self.X_posterior[0,0])

# # step5:更新k时刻的误差的协方差矩阵 为估计k+1时刻的最优值做准备
# P_posterior_1 = np.eye(2) - np.dot(K, self.H)
# self.P_posterior = np.dot(P_posterior_1, P_prior) 
# self.X_true=self.X_posterior