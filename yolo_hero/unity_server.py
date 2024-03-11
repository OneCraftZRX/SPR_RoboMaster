import socket  
from threading import Thread
import time  
import random  
from loguru import logger  
import numpy as np

flag_yaw=1#是否对yaw进行可视化的标志位

class  Armro_Unity_Server:
    def __init__(self):
        self.s = socket.socket()
        self.host = "127.0.0.1" 
        logger.info('host name=' + str(self.host))  
        self.port = 7788
        self.s.bind((self.host, self.port))
        self.s.listen(5)
        logger.info("server start...")  
        self.c, self.addr = self.s.accept()
        logger.info('连接地址：' + str(self.addr))

        # Initialize parameters with default values
        self.center_x = 0.0
        self.center_y = 0.0
        self.center_z = 0.0
        self.best_yaw = 0.0

    def start(self):
        if(flag_yaw==1):
            t = Thread(target=self.send_message_yaw, name="Unity_server", args=(self.c,))
            t.daemon = True
            t.start()
        
        else:
            t = Thread(target=self.send_message, name="Unity_server", args=(self.c,))
            t.daemon = True
            t.start()

        return self
    
    def set_parameters(self, center_x, center_y, center_z, best_yaw):
        # Update parameters with new values
        self.center_x = center_x
        self.center_y = center_y
        self.center_z = center_z
        self.best_yaw = best_yaw
        
    def regenerate(self):
        car_radius = 0.3*10#为了和unity的坐标系对应，需要乘以10，单位dm

        # Calculate car center
        car_center_x = self.center_x + car_radius * np.sin(self.best_yaw)
        car_center_z = self.center_z + car_radius * np.cos(self.best_yaw)
        car_center_y = self.center_y

        # Calculate armor centers
        armor1_center_x = car_center_x + car_radius * np.cos(self.best_yaw)
        armor1_center_z = car_center_z - car_radius * np.sin(self.best_yaw)
        armor1_center_y = car_center_y

        armor2_center_x = self.center_x + 2 * car_radius * np.sin(self.best_yaw)
        armor2_center_z = self.center_z + 2 * car_radius * np.cos(self.best_yaw)
        armor2_center_y = self.center_y

        armor3_center_x = car_center_x - car_radius * np.cos(self.best_yaw)
        armor3_center_z = car_center_z + car_radius * np.sin(self.best_yaw)
        armor3_center_y = car_center_y

        points = [
            (self.center_x, self.center_y, self.center_z),
            (armor1_center_x, armor1_center_y, armor1_center_z),
            (armor2_center_x, armor2_center_y, armor2_center_z),
            (armor3_center_x, armor3_center_y, armor3_center_z),
            (car_center_x, car_center_y, car_center_z)
        ]

        #print("Points:", points)
        result_string = ""
        for point in points:
            for coord in point:
                if coord > 0:
                    result_string += "+{:.2f}N".format(coord)
                else:
                    result_string += "{:.2f}N".format(coord)
        result_string = result_string.rstrip("N")  # Remove trailing N


        return result_string
    
    def regenerate_yaw(self):
        
        points = [
            (time.time(),self.best_yaw)
        ]

        #print("Points:", points)
        result_string = ""
        for point in points:
            for coord in point:
                if coord > 0:
                    result_string += "+{:.2f}N".format(coord)
                else:
                    result_string += "{:.2f}N".format(coord)
        result_string = result_string.rstrip("N")  # Remove trailing N


        return result_string

    def send_message(self,c: socket):  #对敌方车辆进行可视化
        while True:  
            testarr=self.regenerate() 
            time.sleep(0.01)  
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  
            # 发送数据包
            c.send((testarr).encode("utf-8"))  
            #c.send(('server test, time=' + timestamp).encode("utf-8"))  
            #logger.debug(testarr+"\n"+"server send finish time=" + timestamp) 

    
    def send_message_yaw(self,c: socket):  #只对yaw数据进行可视化
        while True:  
            testarr=self.regenerate_yaw() 
            time.sleep(0.01)  
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  
            # 发送数据包
            c.send((testarr).encode("utf-8"))  
            #c.send(('server test, time=' + timestamp).encode("utf-8"))  
            #logger.debug(testarr+"\n"+"server send finish time=" + timestamp) 

    
            