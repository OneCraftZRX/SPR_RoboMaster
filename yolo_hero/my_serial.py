import cv2 as cv
import cv2
import serial
import serial.tools.list_ports
import numpy as np
from threading import Thread
import time
import struct

class SerialPort:

    # 串口初始化函数,接收port参数，port是串口名
    def __init__(self):
        port='/dev/ttyUSB0'
        baudrate = 115200  # 波特率
        self.gimbal_yaw_angle=0#电控发来的云台yaw数据
        self.gimbal_pitch_angle=0#电控发来的云台pitch数据
        try:
            self.ser = serial.Serial(port, baudrate, timeout=2)
            if (self.ser.isOpen () == True):
                print("串口打开成功")
        except Exception as exc:
            print("串口打开异常", exc)
       
    #清理缓冲区数据
    def port_clean(self):
        self.ser.flushInput()

    # 关闭串口
    def close_port(self):
    
        try:
            self.ser_1.close()
            if self.ser.isOpen():
                print("串口1未关闭")
            else:
                print("串口1已关闭")
        except Exception as exc:
            print("串口1关闭异常", exc)
       
##################################################################发送给电控的数据##################################################################
    #发送装甲板数据的函数，包含两个角度
    def sendAngle(self,angle,fire):#目前采用的弧度制
        
        if(angle[0]==0 and angle[1]==0 and fire==0):
            
            try:
                self.ser.write([0,0,0,0,0,0,0,0,0])
                print('-' * 80)
                print("串口1已发送数据:")
                print([0,0,0,0,0,0,0,0,0])
                print('-' * 80)

            except Exception as exc:
                print("串口1发送异常", exc)
           
            
        else:
            angle_1=angle[0]
            angle_2=angle[1]
            
            #保证和电控的控制策略一致
            angle_1=-angle_1

            #print("yaw",angle_1)
            #print("pitch",angle_2)
            
            angle_1=int((angle_1+3.1415925)*1000)#yaw角度放大后的数据，保留4位小数,再精细的就没必要了
            angle_2=int((angle_2+3.1415926)*1000)#pitch角度放大

            #存放高八位和低八位数据的字符数组
            data_unsigned =[0XFF,0,0,0,0,0,0,0,0XFE]
            #data_unsigned1=[0,0,0,0,0,0,0]
            #第一组数据的高八位和低八位
            
            data_unsigned[2]=(angle_1>>8)#取高八位,将高八位的数据对应的字符发出去
            data_unsigned[3]=(angle_1 & 0x00ff)#取低八位
            
            
            # #第二组数据的高八位和低八位
            data_unsigned[4]=(angle_2>>8)
            data_unsigned[5]=(angle_2 & 0x00ff)
            
            #开火指令
            data_unsigned[6]=fire
            #data_unsigned[5]=0
            #create a byte to correct
            data_unsigned[7]=(data_unsigned[2]+data_unsigned[3]+data_unsigned[4]+data_unsigned[5]+data_unsigned[6]) & 0x00ff


            try:
                send_datas = data_unsigned#需要发送的数据，此处直接发送列表数据，不需要设置编码格式，如果发送字符串需要制定编码格式
                #ser.write(str(send_datas+'\r\n').encode("utf-8"))
                self.ser.write(send_datas)
                
                print('-' * 80)
                print("已发送数据:")
                print(send_datas)
                print('-' * 80)

            except Exception as exc:
                print("串口发送异常", exc)

  
##################################################################接收电控的数据################################################################         
                  
    def start(self): #哨兵接收装甲板数据的线程
        #start the thread to read data 
        #t=multiprocessing.Process(target=self.readAngle,name="ReadAngle",args=())
        t=Thread(target=self.readAngle,name="ReadAngle",args=())
        t.daemon=True
        t.start()
      
        return self


    def readAngle(self):
        print("接收云台数据线程")
        #main loop
        while(1):    
            try:
                #time1=time.time()
                gimbal_yaw_data=[]
                gimbal_pitch_data=[]
                self.ser.timeout=5#设置超时时间
                read_datas =self.ser.read(11)#需要接受的数据，此处直接接收列表数据，不需要设置编码格式，如果发送字符串需要制定编码格式   
                #print(read_datas)
                if(read_datas[0]==0XFF and read_datas[10]==0XFE):
                    gimbal_yaw_data=read_datas[1:5]
                    self.gimbal_yaw_angle=struct.unpack('f',gimbal_yaw_data)[0]
                    
                    gimbal_pitch_data=gimbal_yaw_data=read_datas[5:9]
                    self.gimbal_pitch_angle=struct.unpack('f',gimbal_pitch_data)[0]
                    self.enemy_color=read_datas[9]#1对面是蓝色，0是红色
                    #print("接收颜色",read_datas[9])
                    
                #time2=time.time()
                #print("接收数据帧率",1/(time2-time1))
                #print("云台yaw角度",self.gimbal_yaw_angle) 
                #print("云台pitch角度",self.gimbal_pitch_angle) 

            except Exception as exc:
                pass
                #print("云台角度接收异常", exc)
                
    