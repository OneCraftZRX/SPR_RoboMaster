import numpy as np
import math
import cv2
import math
import time
import multiprocessing
from threading import Thread
import matplotlib.pyplot as plt


#进行数据平滑的滤波
class KalmanFilter_low:
   
    def __init__(self):

        # plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
        # plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
        
        # 状态转移矩阵，上一时刻的状态转移到当前时刻
        self.A = np.array([[1,100],[0,1]])
        
        # 过程噪声w协方差矩阵Q，P(w)~N(0,Q)，噪声来自真实世界中的不确定性，Q越小越相信观测值，平滑效果越好，需要的时间越长
        self.Q = np.array([[0.0001,0],[0,0.0001]])
        
        #测量噪声协方差矩阵R，P(v)~N(0,R)，噪声来自测量过程的误差,R越大，更相信模型的值，平滑动效果越好，但需要的时间越长，＜0.1时(过小)，可能导致无法收敛
        self.R = np.array([[0.5,0],[0,0.5]])
        
        # 传输矩阵/状态观测矩阵H
        self.H = np.array([[1,0],[0,1]])
        
        # 控制输入矩阵B
        self.B = None
        
        # 初始位置和速度,x设置成0,v设置成1
        X0 = np.array([[0],[1]])
        
        # 状态估计协方差矩阵P初始化
        P =np.array([[1,0],[0,1]])
        
           
        #---------------------初始化-----------------------------
        #真实值初始化 再写一遍np.array是为了保证它的类型是数组array
        self.X_true = np.array(X0)
        #后验估计值Xk的初始化
        self.X_posterior = np.array(X0)
        #第k次误差的协方差矩阵的初始化
        self.P_posterior = np.array(P)
    
        #创建状态变量的真实值的矩阵 状态变量1：速度 状态变量2：位置
        self.speed_true = []
        self.position_true = []
    
        #创建测量值矩阵
        self.speed_measure = []
        self.position_measure = []
    
        #创建状态变量的先验估计值
        self.speed_prior_est = []
        self.position_prior_est = []
    
        #创建状态变量的后验估计值
        self.speed_posterior_est = []
        self.position_posterior_est = []
        
        self.x1=1
        self.x2=0
    
    
    # def start(self):#启动卡尔曼计算线程
    #     #start the thread to read data
    #     t = Thread(target=self.filter, name="filter", args=()) 
    #     #t=multiprocessing.Process(target=self.filter,name="kalmanfilter_x",args=())
    #     t.daemon=True
    #     t.start()
        
    #     return self
        
    def filter(self,new_data):
        #print("X观测",new_data)
        #print("进入卡尔曼计算线程")

        # 过程噪声w协方差矩阵Q，P(w)~N(0,Q)，噪声来自真实世界中的不确定性，Q越小越相信观测值，平滑效果越好，需要的时间越长
        self.Q = np.array([[0.0005,0],[0,0.0005]])
        
        #测量噪声协方差矩阵R，P(v)~N(0,R)，噪声来自测量过程的误差,R越大，更相信模型的值，平滑动效果越好，但需要的时间越长，＜0.1时(过小)，可能导致无法收敛
        self.R = np.array([[0.5,0],[0,0.5]])

        # 真实值X_true 得到当前时刻的状态;之前我一直在想它怎么完成从Xk-1到Xk的更新，实际上在代码里面直接做迭代就行了，这里是不涉及数组下标的！！！
        #dot函数用于矩阵乘法，对于二维数组，它计算的是矩阵乘积
        self.X_true = np.dot(self.A, self.X_true)

        # 速度的真实值是speed_true 使用append函数可以把每一次循环中产生的拼接在一起，形成一个新的数组speed_true

        self.speed_true.append(self.X_true[1,0])
        self.position_true.append(self.X_true[0,0])
        #print(speed_true)


        # # --------------------生成观测值-----------------------------
        # # 生成过程噪声
        # R_sigma = np.array([[math.sqrt(self.R[0,0]),self.R[0,1]],[self.R[1,0],math.sqrt(self.R[1,1])]])
        # #v = np.array([[gaussian_distribution_generator(R_sigma[0,0])],[gaussian_distribution_generator(R_sigma[1,1])]])

        # 生成观测值Z_measure 取H为单位阵
        X_measure=np.array([[new_data],[0]],dtype=np.float64)
        Z_measure = np.dot(self.H, X_measure)
        
        self.speed_measure.append(Z_measure[1,0])
        #print(speed_measure)
        self.position_measure.append(Z_measure[0,0])

        # --------------------进行先验估计-----------------------------
        # 开始时间更新
        # 第1步:基于k-1时刻的后验估计值X_posterior建模预测k时刻的系统状态先验估计值X_prior
        # 此时模型控制输入U=0
        X_prior = np.dot(self.A, self.X_posterior)
        
        # print("X先验估计",X_prior)
        

        # 第2步:基于k-1时刻的误差ek-1的协方差矩阵P_posterior和过程噪声w的协方差矩阵Q 预测k时刻的误差的协方差矩阵的先验估计值 P_prior
        P_prior_1 = np.dot(self.A, self.P_posterior)
        P_prior = np.dot(P_prior_1, self.A.T) + self.Q

        #print("P先验估计",P_prior)

        # --------------------进行状态更新-----------------------------
        # 第3步:计算k时刻的卡尔曼增益K
        k1 = np.dot(P_prior, self.H.T)
        k2 = np.dot(self.H, k1) + self.R
        #k3 = np.dot(np.dot(H, P_prior), H.T) + R  k2和k3是两种写法，都可以
        K = np.dot(k1, np.linalg.inv(k2))

        #print("卡尔曼增益",K)

        # 第4步:利用卡尔曼增益K 进行校正更新状态，得到k时刻的后验状态估计值 X_posterior
        X_posterior_1 = Z_measure -np.dot(self.H, X_prior)
        self.X_posterior = X_prior + np.dot(K, X_posterior_1)

        print("X后验估计",self.X_posterior)
        
        # 把k时刻后验预测值赋给两个状态分量的后验预测值 speed_posterior_est = X_posterior[1,0];position_posterior_est = X_posterior[0,0]
        self.speed_posterior_est.append(self.X_posterior[1,0])
        self.position_posterior_est.append(self.X_posterior[0,0])

        # step5:更新k时刻的误差的协方差矩阵 为估计k+1时刻的最优值做准备
        P_posterior_1 = np.eye(2) - np.dot(K, self.H)
        self.P_posterior = np.dot(P_posterior_1, P_prior) 
        self.X_true=self.X_posterior
        
    
        X_posterior_temp= np.dot(self.A, self.X_posterior)
        
        return X_posterior_temp[0,0]
   

# def sin_function(t):
#     amplitude = 5  # 振幅
#     frequency = 0.1  # 频率
#     return amplitude * np.sin(2 * np.pi * frequency * t)

# # 创建KalmanFilter_low对象
# kf = KalmanFilter_low()


# # 定义时间步长
# time_steps = 100
# # 生成模拟数据，使用正弦函数
# true_positions = np.zeros(time_steps)
# measurements = np.zeros(time_steps)

# for i in range(time_steps):
#     true_positions[i] = sin_function(i)
#     #measurement_noise = np.random.multivariate_normal([0, 0], kf.R)
#     measurements[i] = true_positions[i] 

# # 运行卡尔曼滤波器并记录估计值
# filtered_positions = []
# for measurement in measurements:
#     print("测量值",measurement)
#     time1=time.time()
#     filtered_position = kf.filter(measurement)
#     print("预测值",filtered_position)
#     filtered_positions.append(filtered_position)
#     time2=time.time()
#     print("时间",time2-time1)

# # 绘制图表
# plt.figure(figsize=(12, 6))
# #plt.plot(true_positions, label='real_data', marker='o')
# plt.plot(measurements, label='measure_data', linestyle='-', marker='x')
# plt.plot(filtered_positions, label='result_of_filter', linestyle='-', marker='s')
# plt.xlabel('setps')
# plt.ylabel('position')
# plt.title('result of kalman filter')
# plt.legend()
# plt.show()




# #进行数据平滑的滤波
# class KalmanFilter_low_y:
   
#     def __init__(self):

#         plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
#         plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
        
#         #定义状态过程噪声协方差矩阵Q和测量过程噪声协方差矩阵R的值，数据不同，值也不同
#         self.Q_value=0.0001
#         self.R_value=0.5
        
#         # 状态转移矩阵，上一时刻的状态转移到当前时刻
#         self.A = np.array([[1,1],[0,1]])
        
#         # 过程噪声w协方差矩阵Q，P(w)~N(0,Q)，噪声来自真实世界中的不确定性，Q越小越相信观测值，平滑效果越好，需要的时间越长
#         self.Q = np.array([[self.Q_value,0],[0,self.Q_value]])
        
#         #测量噪声协方差矩阵R，P(v)~N(0,R)，噪声来自测量过程的误差,R越大，更相信模型的值，平滑动效果越好，但需要的时间越长，＜0.1时(过小)，可能导致无法收敛
#         self.R = np.array([[self.R_value,0],[0,self.R_value]])
        
#         # 传输矩阵/状态观测矩阵H
#         self.H = np.array([[1,0],[0,1]])
        
#         # 控制输入矩阵B
#         self.B = None
        
#         # 初始位置和速度,x设置成0,v设置成1
#         X0 = np.array([[0],[1]])
        
#         # 状态估计协方差矩阵P初始化
#         P =np.array([[1,0],[0,1]])
        
           
#         #---------------------初始化-----------------------------
#         #真实值初始化 再写一遍np.array是为了保证它的类型是数组array
#         self.X_true = np.array(X0)
#         #后验估计值Xk的初始化
#         self.X_posterior = np.array(X0)
#         #第k次误差的协方差矩阵的初始化
#         self.P_posterior = np.array(P)
    
#         #创建状态变量的真实值的矩阵 状态变量1：速度 状态变量2：位置
#         self.speed_true = []
#         self.position_true = []
    
#         #创建测量值矩阵
#         self.speed_measure = []
#         self.position_measure = []
    
#         #创建状态变量的先验估计值
#         self.speed_prior_est = []
#         self.position_prior_est = []
    
#         #创建状态变量的后验估计值
#         self.speed_posterior_est = []
#         self.position_posterior_est = []
        
#         #滤波函数需要的中间变量,x1是需要滤波的数据，x2是滤波的速度值
#         self.x1=0
#         self.x2=0
    
    
#     def start(self):#启动卡尔曼计算线程
#         #start the thread to read data
#         #t = Thread(target=self.filter, name="filter", args=()) 
#         t=multiprocessing.Process(target=self.filter,name="kalmanfilter_y",args=())
#         t.daemon=True
#         t.start()
        
#         return self
        
#     def filter(self):
#         #print("进入卡尔曼计算线程")

#         #main loop
#         while(True):

#             #从共享队列中读取数据
#             data=share_queue.shared_queue_y.get()
#             print("接收数据",data)
            
#             # 过程噪声w协方差矩阵Q，P(w)~N(0,Q)，噪声来自真实世界中的不确定性，Q越小越相信观测值，平滑效果越好，需要的时间越长
#             self.Q = np.array([[data[0],0],[0,data[0]]])
            
#             #测量噪声协方差矩阵R，P(v)~N(0,R)，噪声来自测量过程的误差,R越大，更相信模型的值，平滑动效果越好，但需要的时间越长，＜0.1时(过小)，可能导致无法收敛
#             self.R = np.array([[data[1],0],[0,data[1]]])

#             # 真实值X_true 得到当前时刻的状态;之前我一直在想它怎么完成从Xk-1到Xk的更新，实际上在代码里面直接做迭代就行了，这里是不涉及数组下标的！！！
#             #dot函数用于矩阵乘法，对于二维数组，它计算的是矩阵乘积
#             self.X_true = np.dot(self.A, self.X_true)

#             # 速度的真实值是speed_true 使用append函数可以把每一次循环中产生的拼接在一起，形成一个新的数组speed_true

#             self.speed_true.append(self.X_true[1,0])
#             self.position_true.append(self.X_true[0,0])
#             #print(speed_true)


#             # # --------------------生成观测值-----------------------------
#             # # 生成过程噪声
#             # R_sigma = np.array([[math.sqrt(self.R[0,0]),self.R[0,1]],[self.R[1,0],math.sqrt(self.R[1,1])]])
#             # #v = np.array([[gaussian_distribution_generator(R_sigma[0,0])],[gaussian_distribution_generator(R_sigma[1,1])]])

#             # 生成观测值Z_measure 取H为单位阵
#             X_measure=np.array([[data[2]],[data[3]]],dtype=np.float64)
#             Z_measure = np.dot(self.H, X_measure)
            
#             self.speed_measure.append(Z_measure[1,0])
#             #print(speed_measure)
#             self.position_measure.append(Z_measure[0,0])

#             # --------------------进行先验估计-----------------------------
#             # 开始时间更新
#             # 第1步:基于k-1时刻的后验估计值X_posterior建模预测k时刻的系统状态先验估计值X_prior
#             # 此时模型控制输入U=0
#             X_prior = np.dot(self.A, self.X_posterior)
            
#             # print(self.X_posterior)
            
#             # 把k时刻先验预测值赋给两个状态分量的先验预测值 speed_prior_est = X_prior[1,0];position_prior_est=X_prior[0,0]
#             # 再利用append函数把每次循环迭代后的分量值拼接成一个完整的数组
#             self.speed_prior_est.append(X_prior[1,0])
#             self.position_prior_est.append(X_prior[0,0])

#             # 第2步:基于k-1时刻的误差ek-1的协方差矩阵P_posterior和过程噪声w的协方差矩阵Q 预测k时刻的误差的协方差矩阵的先验估计值 P_prior
#             P_prior_1 = np.dot(self.A, self.P_posterior)
#             P_prior = np.dot(P_prior_1, self.A.T) + self.Q

#             # --------------------进行状态更新-----------------------------
#             # 第3步:计算k时刻的卡尔曼增益K
#             k1 = np.dot(P_prior, self.H.T)
#             k2 = np.dot(self.H, k1) + self.R
#             #k3 = np.dot(np.dot(H, P_prior), H.T) + R  k2和k3是两种写法，都可以
#             K = np.dot(k1, np.linalg.inv(k2))

#             # 第4步:利用卡尔曼增益K 进行校正更新状态，得到k时刻的后验状态估计值 X_posterior
#             X_posterior_1 = Z_measure -np.dot(self.H, X_prior)
#             self.X_posterior = X_prior + np.dot(K, X_posterior_1)
            
#             # 把k时刻后验预测值赋给两个状态分量的后验预测值 speed_posterior_est = X_posterior[1,0];position_posterior_est = X_posterior[0,0]
#             self.speed_posterior_est.append(self.X_posterior[1,0])
#             self.position_posterior_est.append(self.X_posterior[0,0])

#             # step5:更新k时刻的误差的协方差矩阵 为估计k+1时刻的最优值做准备
#             P_posterior_1 = np.eye(2) - np.dot(K, self.H)
#             self.P_posterior = np.dot(P_posterior_1, P_prior) 
#             self.X_true=self.X_posterior
            
#             #将处理后的数据写入队列
#             share_queue.shared_queue_back.put(self.X_posterior[0,0])
        
        
#     def show_result(self):
        
#     # ---------------------再从step5回到step1 其实全程只要搞清先验后验 k的自增是隐藏在循环的过程中的 然后用分量speed和position的append去记录每一次循环的结果-----------------------------
#         #print(self.X_posterior)
#         # 画出1行2列的多子图
#         fig, axs = plt.subplots(1,2)
#         #速度
#         axs[0].plot(self.speed_true,"-",color="blue",label="速度真实值",linewidth="1")
#         axs[0].plot(self.speed_measure,"-",color="grey",label="速度测量值",linewidth="1")
#         axs[0].plot(self.speed_prior_est,"-",color="green",label="速度先验估计值",linewidth="1")
#         axs[0].plot(self.speed_posterior_est,"-",color="red",label="速度后验估计值",linewidth="1")
#         axs[0].set_title("speed")
#         axs[0].set_xlabel('k')
#         axs[0].legend(loc = 'upper left')


#         #位置
#         axs[1].plot(self.position_true,"-",color="blue",label="位置真实值",linewidth="1")
#         axs[1].plot(self.position_measure,"-",color="grey",label="位置测量值",linewidth="1")
#         axs[1].plot(self.position_prior_est,"-",color="green",label="位置先验估计值",linewidth="1")
#         axs[1].plot(self.position_posterior_est,"-",color="red",label="位置后验估计值",linewidth="1")
#         axs[1].set_title("position")
#         axs[1].set_xlabel('k')
#         axs[1].legend(loc = 'upper left')

#         #     调整每个子图之间的距离
#         plt.tight_layout()
#         plt.figure(figsize=(60, 40))
#         plt.show()


# #进行数据平滑的滤波
# class KalmanFilter_low_z:
   
#     def __init__(self):

#         plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
#         plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
        
#         #定义状态过程噪声协方差矩阵Q和测量过程噪声协方差矩阵R的值，数据不同，值也不同
#         self.Q_value=0.0001
#         self.R_value=0.5
        
#         # 状态转移矩阵，上一时刻的状态转移到当前时刻
#         self.A = np.array([[1,1],[0,1]])
        
#         # 过程噪声w协方差矩阵Q，P(w)~N(0,Q)，噪声来自真实世界中的不确定性，Q越小越相信观测值，平滑效果越好，需要的时间越长
#         self.Q = np.array([[self.Q_value,0],[0,self.Q_value]])
        
#         #测量噪声协方差矩阵R，P(v)~N(0,R)，噪声来自测量过程的误差,R越大，更相信模型的值，平滑动效果越好，但需要的时间越长，＜0.1时(过小)，可能导致无法收敛
#         self.R = np.array([[self.R_value,0],[0,self.R_value]])
        
#         # 传输矩阵/状态观测矩阵H
#         self.H = np.array([[1,0],[0,1]])
        
#         # 控制输入矩阵B
#         self.B = None
        
#         # 初始位置和速度,x设置成0,v设置成1
#         X0 = np.array([[0],[1]])
        
#         # 状态估计协方差矩阵P初始化
#         P =np.array([[1,0],[0,1]])
        
           
#         #---------------------初始化-----------------------------
#         #真实值初始化 再写一遍np.array是为了保证它的类型是数组array
#         self.X_true = np.array(X0)
#         #后验估计值Xk的初始化
#         self.X_posterior = np.array(X0)
#         #第k次误差的协方差矩阵的初始化
#         self.P_posterior = np.array(P)
    
#         #创建状态变量的真实值的矩阵 状态变量1：速度 状态变量2：位置
#         self.speed_true = []
#         self.position_true = []
    
#         #创建测量值矩阵
#         self.speed_measure = []
#         self.position_measure = []
    
#         #创建状态变量的先验估计值
#         self.speed_prior_est = []
#         self.position_prior_est = []
    
#         #创建状态变量的后验估计值
#         self.speed_posterior_est = []
#         self.position_posterior_est = []
        
#         #滤波函数需要的中间变量,x1是需要滤波的数据，x2是滤波的速度值
#         self.x1=0
#         self.x2=0
    
    
#     def start(self):#启动卡尔曼计算线程
#         #start the thread to read data
#         #t = Thread(target=self.filter, name="filter", args=()) 
#         t=multiprocessing.Process(target=self.filter,name="kalmanfilter_z",args=())
#         t.daemon=True
#         t.start()
        
#         return self
        
#     def filter(self):
#         #print("进入卡尔曼计算线程")

#         #main loop
#         while(True):

#             #从共享队列中读取数据
#             data=share_queue.shared_queue_z.get()
#             print("接收数据",data)
            
#             # 过程噪声w协方差矩阵Q，P(w)~N(0,Q)，噪声来自真实世界中的不确定性，Q越小越相信观测值，平滑效果越好，需要的时间越长
#             self.Q = np.array([[data[0],0],[0,data[0]]])
            
#             #测量噪声协方差矩阵R，P(v)~N(0,R)，噪声来自测量过程的误差,R越大，更相信模型的值，平滑动效果越好，但需要的时间越长，＜0.1时(过小)，可能导致无法收敛
#             self.R = np.array([[data[1],0],[0,data[1]]])

#             # 真实值X_true 得到当前时刻的状态;之前我一直在想它怎么完成从Xk-1到Xk的更新，实际上在代码里面直接做迭代就行了，这里是不涉及数组下标的！！！
#             #dot函数用于矩阵乘法，对于二维数组，它计算的是矩阵乘积
#             self.X_true = np.dot(self.A, self.X_true)

#             # 速度的真实值是speed_true 使用append函数可以把每一次循环中产生的拼接在一起，形成一个新的数组speed_true

#             self.speed_true.append(self.X_true[1,0])
#             self.position_true.append(self.X_true[0,0])
#             #print(speed_true)


#             # # --------------------生成观测值-----------------------------
#             # # 生成过程噪声
#             # R_sigma = np.array([[math.sqrt(self.R[0,0]),self.R[0,1]],[self.R[1,0],math.sqrt(self.R[1,1])]])
#             # #v = np.array([[gaussian_distribution_generator(R_sigma[0,0])],[gaussian_distribution_generator(R_sigma[1,1])]])

#             # 生成观测值Z_measure 取H为单位阵
#             X_measure=np.array([[data[2]],[data[3]]],dtype=np.float64)
#             Z_measure = np.dot(self.H, X_measure)
            
#             self.speed_measure.append(Z_measure[1,0])
#             #print(speed_measure)
#             self.position_measure.append(Z_measure[0,0])

#             # --------------------进行先验估计-----------------------------
#             # 开始时间更新
#             # 第1步:基于k-1时刻的后验估计值X_posterior建模预测k时刻的系统状态先验估计值X_prior
#             # 此时模型控制输入U=0
#             X_prior = np.dot(self.A, self.X_posterior)
            
#             # print(self.X_posterior)
            
#             # 把k时刻先验预测值赋给两个状态分量的先验预测值 speed_prior_est = X_prior[1,0];position_prior_est=X_prior[0,0]
#             # 再利用append函数把每次循环迭代后的分量值拼接成一个完整的数组
#             self.speed_prior_est.append(X_prior[1,0])
#             self.position_prior_est.append(X_prior[0,0])

#             # 第2步:基于k-1时刻的误差ek-1的协方差矩阵P_posterior和过程噪声w的协方差矩阵Q 预测k时刻的误差的协方差矩阵的先验估计值 P_prior
#             P_prior_1 = np.dot(self.A, self.P_posterior)
#             P_prior = np.dot(P_prior_1, self.A.T) + self.Q

#             # --------------------进行状态更新-----------------------------
#             # 第3步:计算k时刻的卡尔曼增益K
#             k1 = np.dot(P_prior, self.H.T)
#             k2 = np.dot(self.H, k1) + self.R
#             #k3 = np.dot(np.dot(H, P_prior), H.T) + R  k2和k3是两种写法，都可以
#             K = np.dot(k1, np.linalg.inv(k2))

#             # 第4步:利用卡尔曼增益K 进行校正更新状态，得到k时刻的后验状态估计值 X_posterior
#             X_posterior_1 = Z_measure -np.dot(self.H, X_prior)
#             self.X_posterior = X_prior + np.dot(K, X_posterior_1)
            
#             # 把k时刻后验预测值赋给两个状态分量的后验预测值 speed_posterior_est = X_posterior[1,0];position_posterior_est = X_posterior[0,0]
#             self.speed_posterior_est.append(self.X_posterior[1,0])
#             self.position_posterior_est.append(self.X_posterior[0,0])

#             # step5:更新k时刻的误差的协方差矩阵 为估计k+1时刻的最优值做准备
#             P_posterior_1 = np.eye(2) - np.dot(K, self.H)
#             self.P_posterior = np.dot(P_posterior_1, P_prior) 
#             self.X_true=self.X_posterior
            
#             #将处理后的数据写入队列
#             share_queue.shared_queue_back.put(self.X_posterior[0,0])
        
        
#     def show_result(self):
        
#     # ---------------------再从step5回到step1 其实全程只要搞清先验后验 k的自增是隐藏在循环的过程中的 然后用分量speed和position的append去记录每一次循环的结果-----------------------------
#         #print(self.X_posterior)
#         # 画出1行2列的多子图
#         fig, axs = plt.subplots(1,2)
#         #速度
#         axs[0].plot(self.speed_true,"-",color="blue",label="速度真实值",linewidth="1")
#         axs[0].plot(self.speed_measure,"-",color="grey",label="速度测量值",linewidth="1")
#         axs[0].plot(self.speed_prior_est,"-",color="green",label="速度先验估计值",linewidth="1")
#         axs[0].plot(self.speed_posterior_est,"-",color="red",label="速度后验估计值",linewidth="1")
#         axs[0].set_title("speed")
#         axs[0].set_xlabel('k')
#         axs[0].legend(loc = 'upper left')


#         #位置
#         axs[1].plot(self.position_true,"-",color="blue",label="位置真实值",linewidth="1")
#         axs[1].plot(self.position_measure,"-",color="grey",label="位置测量值",linewidth="1")
#         axs[1].plot(self.position_prior_est,"-",color="green",label="位置先验估计值",linewidth="1")
#         axs[1].plot(self.position_posterior_est,"-",color="red",label="位置后验估计值",linewidth="1")
#         axs[1].set_title("position")
#         axs[1].set_xlabel('k')
#         axs[1].legend(loc = 'upper left')

#         #     调整每个子图之间的距离
#         plt.tight_layout()
#         plt.figure(figsize=(60, 40))
#         plt.show()


class MovingAverageFilter:
    def __init__(self,window_size):
        self.window_size=window_size
        self.data=[]
        
    def smooth(self,value):
        self.data.append(value)
        if len(self.data)>self.window_size:
            self.data=self.data[1:]
        
        # print("滤波数组",self.data)
        return sum(self.data)/len(self.data)
    def reset(self):
        self.data=[]
    
    
# class KalmanFilter:
#     #实例属性
#     kf = cv2.KalmanFilter(2, 1)                                                                              #其值为4，因为状态转移矩阵transitionMatrix有4个维度
#                                                                                                              #需要观测的维度为2
#     kf.measurementMatrix = np.array([[1, 0]], np.float32)                                #创建测量矩阵
#     kf.transitionMatrix = np.array([[1, 1], [0, 1]], np.float32)     #创建状态转移矩阵

#     def predict(self, coordX):                      #实例方法，自己实现一个predict
#         ''' This function estimates the position of the object'''
#         measured = np.array([[np.float32(coordX)]])   
#         self.kf.correct(measured)                           #结合观测值更新状态值，correct为卡尔曼滤波器自带函数
#         predicted = self.kf.predict()                       #调用卡尔曼滤波器自带的预测函数
#         x= int(predicted[0])                            #得到预测后的坐标值
#         return x


#https://pysource.com/2021/10/29/kalman-filter-predict-the-trajectory-of-an-object/
# import cv2
# import numpy as np

# class KalmanFilter:
#     #实例属性
#     kf = cv2.KalmanFilter(4, 2)                                                                              #其值为4，因为状态转移矩阵transitionMatrix有4个维度
#                                                                                                              #需要观测的维度为2
#     kf.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)                                #创建测量矩阵
#     kf.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)     #创建状态转移矩阵

#     def predict(self, coordX, coordY):                      #实例方法，自己实现一个predict
#         ''' This function estimates the position of the object'''
#         measured = np.array([[np.float32(coordX)], [np.float32(coordY)]])   
#         self.kf.correct(measured)                           #结合观测值更新状态值，correct为卡尔曼滤波器自带函数
#         predicted = self.kf.predict()                       #调用卡尔曼滤波器自带的预测函数
#         x, y = int(predicted[0]), int(predicted[1])         #得到预测后的坐标值
#         return x, y
# import cv2
# import numpy as np

# class KalmanFilter:
#     #实例属性
#     kf = cv2.KalmanFilter(4, 2)                                                                              #其值为4，因为状态转移矩阵transitionMatrix有4个维度
#                                                                                                              #需要观测的维度为2
#     kf.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)                                #创建测量矩阵
#     kf.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)     #创建状态转移矩阵
    
#     predicted=np.array([[0],[0]], np.float32)
#     def predict(self, coordX, coordY):                      #实例方法，自己实现一个predict，
#         ''' This function estimates the position of the object'''
#         measured = np.array([[np.float32(coordX)], [np.float32(coordY)]])   
#         self.kf.correct(measured)                           #结合观测值更新状态值，correct为卡尔曼滤波器自带函数
#         predicted = self.kf.predict() 
#         #print(type(predicted))
        
#         # for i in range (3):
#         #     #print("predic","次数",predicted,i)
#         #     measured = np.array([[predicted[0]], [predicted[1]]])   
#         #     self.kf.correct(measured)                           #结合观测值更新状态值，correct为卡尔曼滤波器自带函数
#         #     predicted = self.kf.predict() 
#         x, y = (predicted[0]), (predicted[1])         #得到预测后的坐标值
#         return x, y


