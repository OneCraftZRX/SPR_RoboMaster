# import time
# import matplotlib
# import matplotlib.pyplot as plt
# import argparse
# import numpy as np
# import cv2
# from openvino.runtime import Core, Model
# from typing import Tuple, Dict
# import random
# from ultralytics.yolo.utils import ops
# import torch
# from ultralytics import YOLO
# from ultralytics.yolo.utils.plotting import colors
# from ultralytics.yolo.utils import ROOT, yaml_load
# from ultralytics.yolo.utils.checks import check_yaml
# from WebcamVideoStream import WebcamVideoStream#双线程读取视频类
# from Predict.kalmanfilter import MovingAverageFilter,KalmanFilter_low,KalmanFilter#卡尔曼预测类
# from position_solver import PositionSolver
# import math
# from my_serial import SerialPort
# matplotlib.use('TkAgg')


# import cv2 as cv
# import cv2
# import serial
# import serial.tools.list_ports
# import numpy as np
# from threading import Thread
# import multiprocessing
# import struct

# class anti_top:

#     # 串口初始化函数,接收port参数，port是串口名
#     def __init__(self):
       
#         #针对1号，3号，4号，前哨站建立收集数据的队列，1，3，4一套逻辑，前哨站一套逻辑
#         self.armor1=[]
#         self.armor3=[]
#         self.armor4=[]
#         self.outpost=[]
        
#     #添加目标状态函数，接受目标的类别
#     def add_state(self,label):
#         if label=="armor_blue_1" or label=="armor_blue_1" :
#             self.armor1.append(1)
            
#         if label=="armor_blue_3" or label=="armor_blue_3" :
#             self.armor3.append(1)
            
#         if label=="armor_blue_4" or label=="armor_blue_4" :
#             self.armor4.append(1)
            
#         if label=="outpost_blue" or label=="outpost_red" :
#             self.outpost.append(1)
        
#     def 
        
#     def anti_detection(self,list):


import numpy as np
import matplotlib.pyplot as plt

# 初始化空的数据列表
yaw_data = []
iou_data = []

# 创建初始的Matplotlib图形
fig, ax = plt.subplots()
ax.set_xlabel('X轴')
ax.set_ylabel('Y轴')
line, = ax.plot(yaw_data, iou_data, marker='o', linestyle='-', markersize=5)

# 更新图形函数
def update_plot(yaw, iou):
    yaw_data.append(yaw)
    iou_data.append(iou)
    
    # 更新Matplotlib图形数据
    line.set_data(yaw_data, iou_data)
    
    # 重新设置图形的x轴范围，可以根据需要进行调整
    ax.relim()
    ax.autoscale_view()
    
    # 更新图形
    plt.draw()
    plt.pause(0.01)  # 稍微暂停以显示更新

# 示例函数接受两个参数并更新图形
def receive_and_plot(yaw, iou):
    update_plot(yaw, iou)

# 主程序示例，不断输入参数，调用示例函数
while True:
    try:
        yaw = float(input("输入X坐标: "))
        iou = float(input("输入Y坐标: "))
        receive_and_plot(yaw, iou)
    except ValueError:
        print("输入无效，请输入有效的数值。")
