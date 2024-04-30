import math
import cv2
import numpy as np
import math 

# class CameraCalibration:
#     def __init__(self):
#         self.object_points = None
#         self.camera_matrix = None
#         self.rotation_vector = None
#         self.translation_vector = None

#     def set_parameters(self, object_points, camera_matrix, rotation_vector, translation_vector):
#         self.object_points = object_points
#         self.camera_matrix = camera_matrix
#         self.rotation_vector = rotation_vector
#         self.translation_vector = translation_vector

#     def project_points(self):
        
#         self.image_points, _ = cv2.projectPoints(self.object_points, self.rotation_vector, self.translation_vector, self.camera_matrix, None)
#         return np.squeeze(self.image_points)

#     #计算实际检测的矩形和反投影矩形的差值
#     def calculate_intersection_over_union(self, real_points2d):
        
#         projected_image_points = self.project_points()

#         # Calculate the intersection area
#         intersection_area = 0

#         #计算两个矩形交集矩形的左上角和右下角坐标

#         x1_intersection = max(projected_image_points[0][0], real_points2d[0][0])
#         y1_intersection = max(projected_image_points[0][1], real_points2d[0][1])

#         x2_intersection = min(projected_image_points[2][0], real_points2d[2][0])
#         y2_intersection = min(projected_image_points[2][1], real_points2d[2][1])

#         # print("交集左上角坐标",x1_intersection,y1_intersection)
#         # print("交集右下角坐标",x2_intersection,y2_intersection)

#         #计算交集矩形的面积
#         intersection_area = (x2_intersection - x1_intersection) * (y2_intersection - y1_intersection)
#         # print("交集面积",intersection_area)

#         #计算两个矩形并集的面积
#         rect1_area = math.fabs(cv2.contourArea(np.array(projected_image_points, dtype=np.float32).astype(int)))
#         rect2_area = math.fabs(cv2.contourArea(np.array(real_points2d, dtype=np.float32).astype(int)))
#         union_area = rect1_area + rect2_area - intersection_area
#         # print("矩形1坐标",projected_image_points)
#         # print("矩形1面积",rect1_area)
#         # print("矩形2坐标",real_points2d)
#         # print("矩形2面积",rect2_area)
#         # print("并集面积",union_area)
#         # print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

#         # Calculate the intersection over union (IoU) ratio
#         iou_ratio = intersection_area / union_area if union_area > 0 else 0.0

#         return iou_ratio

# # Example usage:
# # Create a CameraCalibration object and set its parameters
# calibration = CameraCalibration()
# # Set object_points, camera_matrix, rotation_vector, and translation_vector here

# # Calculate the difference between known_image_points and projected_image_points
# known_image_points = np.array([[x1, y1], [x2, y2], [x3, y3], [x4, y4]])  # Replace with your known image points
# difference = calibration.calculate_difference(known_image_points)
# print("Difference:", difference)




import cv2
import math
import numpy as np

class CameraCalibration:
    def __init__(self):
        self.object_points = None
        self.camera_matrix = None
        self.rotation_vector = None
        self.translation_vector = None
        self.yaw_and_loss=[]

    def set_parameters(self, object_points, camera_matrix, rotation_vector, translation_vector):
        self.object_points = object_points
        self.camera_matrix = camera_matrix
        self.rotation_vector = rotation_vector
        self.translation_vector = translation_vector

    def project_points(self,yaw):#反投影函数，利用给定的yaw进行反投影

        # Apply the yaw rotation to the rotation vector
        rotated_rotation_vector = self.rotation_vector.copy()
        rotated_rotation_vector[1] = yaw  # Add the yaw angle to the original rotation vector

        # print("rotated_rotation_vector",rotated_rotation_vector)
        # print("self.translation_vector",self.translation_vector)

        # Project the object points
        image_points, _ = cv2.projectPoints(self.object_points, rotated_rotation_vector, self.translation_vector, self.camera_matrix, None)

        #print("库函数结果",image_points)
        
        return np.squeeze(image_points)

    def project_points_3d_to_2d(self,yaw):#反向投影的数学公式实现
        # 转换为NumPy数组
        points_3d = np.array(self.object_points)
       
        rotation_vector = self.rotation_vector.copy()
        rotation_vector[1] = yaw
        #print("旋转向量",rotation_vector)
        translation_vector=self.translation_vector

        # 将旋转向量转换为旋转矩阵
        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
        #print("旋转矩阵",rotation_matrix)
        
        #将3D点进行旋转和平移变换
        points_3d_transformed = np.dot(rotation_matrix, points_3d.T)+translation_vector
        
        #print(points_3d_transformed)
        # 使用相机矩阵将3D点投影到2D图像平面
        points_2d = np.dot(self.camera_matrix, points_3d_transformed).T

        # 转换为像素坐标系
        pixels_x = points_2d[:, 0] / points_2d[:, 2]
        pixels_y = points_2d[:, 1] / points_2d[:, 2]

        pixels_coordinates = np.column_stack((pixels_x, pixels_y))

        #print("数学运算结果",pixels_coordinates)
        
        return np.squeeze(pixels_coordinates)

  
    def calculate_iou(self, real_points2d,yaw):#计算iou的函数
        # Get projected image points for the given yaw
        projected_image_points = self.project_points(yaw)

        # Calculate coordinates of the intersection rectangle
        x0_intersection = max(projected_image_points[0][0], real_points2d[0][0])
        y0_intersection = max(projected_image_points[0][1], real_points2d[0][1])

        x1_intersection = min(projected_image_points[1][0], real_points2d[1][0])
        y1_intersection = max(projected_image_points[1][1], real_points2d[1][1])

        x2_intersection = min(projected_image_points[2][0], real_points2d[2][0])
        y2_intersection = min(projected_image_points[2][1], real_points2d[2][1])

        x3_intersection = max(projected_image_points[3][0], real_points2d[3][0])
        y3_intersection = min(projected_image_points[3][1], real_points2d[3][1])

        #将x1,x2,x3,x4四个点作为一个矩形，利用counterarea计算矩形的面积
        intersection_area = math.fabs(cv2.contourArea(np.array([[x0_intersection, y0_intersection],
                                                      [x1_intersection, y1_intersection],
                                                      [x2_intersection, y2_intersection],
                                                      [x3_intersection, y3_intersection]]).astype(int)))
        

        # Calculate areas of the two rectangles
        rect1_area = math.fabs(cv2.contourArea(np.array(projected_image_points, dtype=np.float32).astype(int)))
        rect2_area = math.fabs(cv2.contourArea(np.array(real_points2d, dtype=np.float32).astype(int)))

        # Calculate the union area
        union_area = rect1_area + rect2_area - intersection_area

        # Calculate the intersection over union (IoU) ratio
        iou_ratio = intersection_area / union_area if union_area > 0 else 0.0

        return iou_ratio
       

    def calculate_rake(self, real_points2d, yaw,angle_real_limit1,angle_real_limit2):  #计算装甲板倾斜度差异的函数，带有方向性,能够弥补iou的不足

        #参数计算,分别以两个极限角度进行反投影
        projected_image_points_limit1=self.project_points(angle_real_limit1)
        projected_image_points_limit2=self.project_points(angle_real_limit2)
        projected_image_points = self.project_points(yaw)
        
        #计算左右灯条的倾斜角度，选择较大的一个作为真实的倾斜角度
        angle_real_right=math.degrees(math.atan((real_points2d[1][0]-real_points2d[2][0])/(real_points2d[1][1]-real_points2d[2][1])))
        angle_real_left=math.degrees(math.atan((real_points2d[0][0]-real_points2d[3][0])/(real_points2d[0][1]-real_points2d[3][1])))

        #判断两个谁更大
        if(math.fabs(angle_real_right)>math.fabs(angle_real_left)):#右灯条更大
            
            #print("右灯条更大")
            #计算反投影的角度范围，用于归一化
            angle_projection_limit1=math.degrees(math.atan((projected_image_points_limit1[1][0]-projected_image_points_limit1[2][0])/(projected_image_points_limit1[1][1]-projected_image_points_limit1[2][1])))
            angle_projection_limit2=math.degrees(math.atan((projected_image_points_limit2[1][0]-projected_image_points_limit2[2][0])/(projected_image_points_limit2[1][1]-projected_image_points_limit2[2][1])))

            #损失计算
            angle_real=math.degrees(math.atan((real_points2d[1][0]-real_points2d[2][0])/(real_points2d[1][1]-real_points2d[2][1])))
            angle_projection=math.degrees(math.atan((projected_image_points[1][0]-projected_image_points[2][0])/(projected_image_points[1][1]-projected_image_points[2][1])))


        else:#左灯条更大
            #print("左灯条更大")

            #计算反投影的角度范围，用于归一化
            angle_projection_limit1=math.degrees(math.atan((projected_image_points_limit1[0][0]-projected_image_points_limit1[3][0])/(projected_image_points_limit1[0][1]-projected_image_points_limit1[3][1])))
            angle_projection_limit2=math.degrees(math.atan((projected_image_points_limit2[0][0]-projected_image_points_limit2[3][0])/(projected_image_points_limit2[0][1]-projected_image_points_limit2[3][1])))

            #损失计算
            angle_real=math.degrees(math.atan((real_points2d[0][0]-real_points2d[3][0])/(real_points2d[0][1]-real_points2d[3][1])))
            angle_projection=math.degrees(math.atan((projected_image_points[0][0]-projected_image_points[3][0])/(projected_image_points[0][1]-projected_image_points[3][1])))
            
        
        # angle_projection=math.degrees(3.14/2-math.atan((projected_image_points[0][1]-projected_image_points[1][1])/(projected_image_points[0][0]-projected_image_points[1][0])))
        #print("真实模型值",angle_real)
        #print("输入yaw", yaw)  
        # print("limit1",angle_projection_limit1)
        # print("limit2",angle_projection_limit2)
        #print(angle_projection)
        # print(angle_projection_limit1)
        # print(angle_projection_limit2)
        normal=max(math.fabs(angle_real-angle_projection_limit1),math.fabs(angle_real-angle_projection_limit2))
        rake_normalized=(angle_projection-angle_real)**2/(normal**2)
               
        
        return rake_normalized
    
    # def find_best_yaw(self, real_points2d):
    #     # Constants for Golden Section Search
    #     golden_ratio = (math.sqrt(5) - 1) / 2
    #     tolerance = 1e-5

    #     # Define the search range
    #     a = -math.pi/4
    #     b = math.pi/4

    #     # Initial points for Golden Section Search
    #     x1 = b - golden_ratio * (b - a)
    #     x2 = a + golden_ratio * (b - a)

    #     while abs(b - a) > tolerance:
    #         # Evaluate the function at the new points
    #         f1 = self.loss_function(real_points2d, x1)
    #         f2 = self.loss_function(real_points2d, x2)

    #         # Update the search range
    #         if f1 < f2:
    #             b = x2
    #         else:
    #             a = x1

    #         # Calculate new points
    #         x1 = b - golden_ratio * (b - a)
    #         x2 = a + golden_ratio * (b - a)

    #     best_yaw = (a + b) / 2

    #     return best_yaw

    # def loss_function(self, real_points2d, yaw):
    #     rake_ratio = self.calculate_rake(real_points2d, yaw)
    #     return 0.65 * 100 * (1 - rake_ratio) ** 2 + 0.35 * (1 - self.calculate_iou(real_points2d, yaw))

    def find_best_yaw(self, real_points2d, num_samples=100):
        best_yaw = 0
        best_iou = 0
        best_rake_ratio =1 

        # Iterate through yaw angles
        for i in range(num_samples):
            yaw = -math.pi/4 + i * ((math.pi/2) / num_samples)# Adjust yaw within the specified range
            #print("yaw",yaw)
            iou = self.calculate_iou(real_points2d, yaw)
            #points_abd=self.calculate_distance(real_points2d,yaw)
            rake_ratio=self.calculate_rake(real_points2d,yaw,(-math.pi/4),(math.pi/4))


            if(len(self.yaw_and_loss)<100):
                self.yaw_and_loss.append([yaw,1-iou])
            
            #print("yaw",yaw)
            #print("rake_ratio",rake_ratio)
            #print("1-iou",1-iou)
            #目前loss函数：0.5*100*(1-rake_ratio)**2+(1-iou)*0.5，iou和rake_ratio的权重是均为0.5
            if((0.6*(rake_ratio)+0.4*(1-iou))<(0.6*(best_rake_ratio)+0.4*(1-best_iou))):
                #print("开始更新最优值")
                best_iou=iou
                best_rake_ratio=rake_ratio
                best_yaw=yaw

        #print(self.yaw_and_loss)
        #print("best_yaw",best_yaw)

        return best_yaw
    

    # def ternary_search_minimize(self,loss_function, low, high, epsilon=1e-3):

    #     while (high - low) > epsilon:
    #         mid1 = low + (high - low) / 3
    #         mid2 = high - (high - low) / 3

    #         loss_mid1 = loss_function(mid1)
    #         loss_mid2 = loss_function(mid2)

    #         if loss_mid1 < loss_mid2:
    #             high = mid2
    #         else:
    #             low = mid1

    #     return (low + high) / 2

    # def phi_optimization(self, loss_function, low, high, epsilon=1e-3):  
    #     # 黄金分割比例  
    #     phi = (math.sqrt(5) - 1) / 2  
        
    #     # 计算分割点  
    #     a = low  
    #     b = high  
    #     c = b - phi * (b - a)  
    #     d = a + phi * (b - a)  
        
    #     while (b - a) > epsilon:  
    #         loss_c = loss_function(c)  
    #         loss_d = loss_function(d)  
            
    #         # 根据损失函数值更新搜索区间  
    #         if loss_c < loss_d:  
    #             b = d  
    #             d = c + phi * (b - c)  
    #         else:  
    #             a = c  
    #             c = d - phi * (d - c)  
    #             d = c + phi * (b - c)  
        
    #     # 返回最优解的近似值  
    #     return (a + b) / 2  

    # def find_best_yaw_phi_search(self, real_points2d, num_samples=100):
    #     # Define the loss function
    #     def loss_function(yaw):
    #         iou = self.calculate_iou(real_points2d, yaw)
    #         rake_ratio = self.calculate_rake(real_points2d, yaw)
    #         return 0.4*100 * (1 - rake_ratio)**2 + (1 - iou) * 0.6
    

        # Set the initial search range
        # initial_low = -math.pi / 2
        # initial_high = math.pi / 2

        # # Use ternary search to find the best yaw
        # best_yaw = self.phi_optimization(loss_function, initial_low, initial_high)

        # return best_yaw
    
    # def calculate_distance(self, real_points2d, yaw):  
    #     projected_image_points = self.project_points(yaw)

    #     armor_length=math.sqrt(((projected_image_points[0][0]- projected_image_points[1][0])**2+(projected_image_points[0][1]- projected_image_points[1][1])**2))/3#归一化变量
    #     #print(armor_length)
    #     points_distance0=math.sqrt((real_points2d[0][0]-projected_image_points[0][0])**2+(real_points2d[0][1]-projected_image_points[0][1])**2)
    #     points_distance1=math.sqrt((real_points2d[1][0]-projected_image_points[1][0])**2+(real_points2d[1][1]-projected_image_points[1][1])**2)
    #     points_distance2=math.sqrt((real_points2d[2][0]-projected_image_points[2][0])**2+(real_points2d[2][1]-projected_image_points[2][1])**2)
    #     points_distance3=math.sqrt((real_points2d[3][0]-projected_image_points[3][0])**2+(real_points2d[3][1]-projected_image_points[3][1])**2)
        
    #     points_abd=(points_distance0+points_distance1+points_distance2+points_distance3)/armor_length

    #     #print(points_abd)
    #     return points_abd