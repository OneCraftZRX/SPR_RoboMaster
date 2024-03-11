import cv2
import numpy as np
from cv2 import solvePnP
import math
from scipy.optimize import fsolve
from my_serial import SerialPort

###########################跟随相机结算思路###############################
#pnp结算相机坐标系下的装甲板位置,由于pitch角度不可忽略,所以需要考虑云台抬升带来的结算变化
#相机系和云台系之间的转换，把三维点放到云台坐标系下
#云台系下结算角度，得出的即为需要偏转的角度



class PositionSolver :

    # yaw和pitch是现在云台系相对惯性系的角度
    # yaw_now=0.0#当前摆头角
    # pitch_now=0.0#当前俯仰角

    def my_pnp(self,points_3D, points_2D, cameraMatrix,distCoeffs):#pnp函数，结算装甲板中心和相机中心之间的旋转，平移矩阵，此处的2维点应该是卡尔曼预测后的点

        #assert points_3D.shape[0] == points_2D.shape[0], '点 3D 和点 2D 必须具有相同数量的顶点,shape()函数得到矩阵的尺寸【0】是矩阵行数'

        self.R=np.array([[0, 0, 0],
                            [ 0, 0, 0],
                            [0, 0, 0]], dtype=np.float64)

        self.t=np.array([[0], [0] ,[0]], dtype=np.float64)
    #    = cv2.solvePnP(points_3D, points_2D, cameraMatrix, distCoeffs)
    
        # 将旋转向量转换为旋转矩阵
        self.R, _ = cv2.Rodrigues(self.R)
    
        # return self.R, self.t
        retval, self.R, self.t =cv2.solvePnP(points_3D, points_2D,
                                #np.ascontiguousarray(points_2D[:,:2]).reshape((-1,1,2)),
                                cameraMatrix,
                                distCoeffs,self.R,self.t,False,
                                 cv2.SOLVEPNP_IPPE)

        self.R, _ = cv2.Rodrigues(self.R)

        return self.R, self.t 
    
        #points_3D:特征点的世界坐标，坐标值需为float型，不能为double型，可以为mat类型，也可以直接输入vector
        ###########以特征点所在平面为世界坐标XY平面，并在该平面中确定世界坐标的原点，并按照顺时针方向逐个输入四个角点的世界坐标
        #points_2D:特征点在图像中的像素坐标，可以为mat类型，也可以直接输入vector，顺序要与前面的世界坐标特征点一一对应
        #cameraMatrix:相机内参矩阵
        #distcoeffs：相机畸变参数
        #R_exp：旋转向量   R:旋转矩阵   t：平移矩阵


    def position2cam(self):#结算坐标，只考虑平移矩阵，偏移单位mm

        cam_x=self.t[0]
        cam_y=self.t[1]
        cam_z=self.t[2]

        #定义坐标矩阵，方便后面进行变换
        self.cam_position_matrix=np.array([[cam_x],
                                            [cam_y],
                                            [cam_z]],dtype=np.float64)
        self.cam_position_matrix_reshape=self.cam_position_matrix.reshape(3,1)#相机坐标系下的物体坐标
        
        #print("相机坐标系下的坐标",self.cam_position_matrix)
        

    def cam2imu(self):#先进行相机系到惯性系的转换

        #初始化旋转矩阵，相机的相机系到惯性系的旋转化是固定的,即是单位阵
        b2axx_1,b2ayx_1,b2azx_1= 1.0, 0.0, 0.0
        b2axy_1,b2ayy_1,b2azy_1= 0.0, 1.0, 0.0
        b2axz_1,b2ayz_1,b2azz_1= 0.0, 0.0, 1.0

        #初始化平移矩阵，相机固定时，平移矩阵也是固定的（数据从机械获得）,单位mm，影响坐标结算的准确度
        self.tx,self.ty,self.tz=0.0, 0.0, 199.6
        
        #相机到惯性系的旋转矩阵
        cam_to_imu_R=np.array([[b2axx_1,b2ayx_1,b2azx_1],
                                    [b2axy_1,b2ayy_1,b2azy_1],
                                    [b2axz_1,b2ayz_1,b2azz_1]],dtype=np.float64)

        #相机系到惯性系的平移矩阵
        cam_to_imu_T =[[self.tx],
                        [self.ty],
                        [self.tz]]

        #print(cam_to_imu_T)


        #进行旋转变换
        self.imu_position_matrix=cam_to_imu_R.dot((self.cam_position_matrix_reshape))
        # self.imu_position_matrix=cam_to_imu_R_2.dot((self.cam_position_matrix_reshape))
        #进行平移变换
        self.imu_position_matrix[0]+=cam_to_imu_T[0]
        self.imu_position_matrix[1]+=cam_to_imu_T[1]
        self.imu_position_matrix[2]+=cam_to_imu_T[2]
        
        #返回云台系下的物体坐标
        return self.imu_position_matrix


    def imu2inetia(self,angle_pitch):
        #print(angle_pitch)
        #定义云台系到惯性坐标系的旋转矩阵,接受pitch角度,yaw角度不需要
        b2axx_2,b2ayx_2,b2azx_2= 1.0,             0.0,             0.0
        b2axy_2,b2ayy_2,b2azy_2= 0.0,   math.cos(angle_pitch), -math.sin(angle_pitch)
        b2axz_2,b2ayz_2,b2azz_2= 0.0,   math.sin(angle_pitch),  math.cos(angle_pitch)


        imu_to_inetia_R=np.array([[b2axx_2,b2ayx_2,b2azx_2],
                            [b2axy_2,b2ayy_2,b2azy_2],
                            [b2axz_2,b2ayz_2,b2azz_2]],dtype=np.float64)
        
        #进行云台到世界坐标系的转化
        self.inetia_position_matrix= imu_to_inetia_R.dot((self.imu_position_matrix))
        
        return self.inetia_position_matrix

    def inetia2world(self,angle_yaw):
        #定义云台系到世界坐标系的旋转矩阵,接受pitch角度,yaw角度不需要,最终转换到的世界坐标系可以理解为是云台上电时候建立的坐标系，此坐标系不变

        b2axx_2,b2ayx_2,b2azx_2= math.cos(angle_yaw),0.0,-math.sin(angle_yaw)
        b2axy_2,b2ayy_2,b2azy_2= 0.0, 1.0, 0.0
        b2axz_2,b2ayz_2,b2azz_2= math.sin(angle_yaw),0.0,math.cos(angle_yaw)


        inetia_to_world_R=np.array([[b2axx_2,b2ayx_2,b2azx_2],
                            [b2axy_2,b2ayy_2,b2azy_2],
                            [b2axz_2,b2ayz_2,b2azz_2]],dtype=np.float64)
        
        #进行云台到世界坐标系的转化
        self.world_position_matrix= inetia_to_world_R.dot((self.inetia_position_matrix))
        

        return self.world_position_matrix


    #计算惯性系下云台需要转过的相对角度，结算后和云台当前角度做差

    def equation(self,theta,h,distance):#斜抛运动方程，注意单位换算，单位为m
        cos_theta=math.cos(theta)
        eq=math.tan(theta)*distance-h+9.8*distance**2/(2*27*27*cos_theta**2)#30为合理射速
        
        return eq
    
    def solve_pitch(self,h,distance):
        
        #使用fslove函数求解
        theta_fsolve=fsolve(self.equation,0.1,args=(h,distance))
        
        #print("result",theta_fsolve)
        
        return theta_fsolve
    
    
    