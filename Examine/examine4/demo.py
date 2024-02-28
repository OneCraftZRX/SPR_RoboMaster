from __future__ import division
import numpy as np
import math
import cv2
from config import *

def nothing(*arg):
    pass

half_Weight = int(Object["width"] / 2)
half_Height = int(Object["height"] / 2)


# 滑动条用以调节HSV的参数
cv2.namedWindow('colorTest')  # 为滑动条创建窗口
Icol = icol["icol_black"] # 初始化滑动条内的起始数据
cv2.createTrackbar('lowHue', 'colorTest', Icol[0], 255, nothing)
cv2.createTrackbar('highHue', 'colorTest', Icol[1], 255, nothing)

cv2.createTrackbar('lowSat', 'colorTest', Icol[2], 255, nothing)
cv2.createTrackbar('highSat', 'colorTest', Icol[3], 255, nothing)

cv2.createTrackbar('lowVal', 'colorTest', Icol[4], 255, nothing)
cv2.createTrackbar('highVal', 'colorTest', Icol[5], 255, nothing)

camera = cv2.VideoCapture(3)

while True:
    (grabbed, frame) = camera.read()
    # Get HSV values from the GUI sliders.
    lowHue = cv2.getTrackbarPos('lowHue', 'colorTest')
    lowSat = cv2.getTrackbarPos('lowSat', 'colorTest')
    lowVal = cv2.getTrackbarPos('lowVal', 'colorTest')
    highHue = cv2.getTrackbarPos('highHue', 'colorTest')
    highSat = cv2.getTrackbarPos('highSat', 'colorTest')
    highVal = cv2.getTrackbarPos('highVal', 'colorTest')

    frameBGR = cv2.GaussianBlur(frame.copy(), (7, 7), 0)  # 高斯模糊
    hsv = cv2.cvtColor(frameBGR, cv2.COLOR_BGR2HSV)  # 颜色转换
    colorLow = np.array([lowHue, lowSat, lowVal]) # 获取low HSV 的值
    colorHigh = np.array([highHue, highSat, highVal]) # 获取high HSV 的值
    mask = cv2.inRange(hsv, colorLow, colorHigh)
    edged = cv2.Canny(mask, 35, 100) # canny算子找轮廓
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    dst = cv2.dilate(edged.copy(), kernel)  # 扩张，使轮廓闭合。
    (cnts, _) = cv2.findContours(dst.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)  # 找轮廓
    area = []

    # 求最大面积
    try:
        for k in range(len(cnts)):
            area.append(cv2.contourArea(cnts[k]))
        max_idx = np.argmax(np.array(area))
        cv2.drawContours(mask, cnts, max_idx, (255, 255, 255), cv2.FILLED)
        (cnts, _) = cv2.findContours(mask.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        c = max(cnts, key=cv2.contourArea)

        marker = cv2.minAreaRect(c)
        box = np.int0(cv2.boxPoints(marker))

        cv2.drawContours(frame, [box], -1, (255, 255, 255), 2)

        obj = np.array([[-half_Weight, -half_Height, 0], [half_Weight, -half_Height, 0], [half_Weight, half_Height, 0],
                        [-half_Weight, half_Height, 0]], dtype=np.float64)  # 世界坐标
        pnts = np.array(box, dtype=np.float64) # 像素坐标

        # rotation_vector 旋转向量 translation_vector 平移向量
        (success, rvec, tvec) = cv2.solvePnP(obj, pnts, Camera_intrinsic["mtx"], Camera_intrinsic["dist"])

        distance=math.sqrt(tvec[0]**2+tvec[1]**2+tvec[2]**2)/10  # 测算距离

        rvec_matrix = cv2.Rodrigues(rvec)[0]
        proj_matrix = np.hstack((rvec_matrix, rvec))
        eulerAngles = -cv2.decomposeProjectionMatrix(proj_matrix)[6]  # 欧拉角
        pitch, yaw, roll = eulerAngles[0], eulerAngles[1], eulerAngles[2]
        rot_params = np.array([yaw, pitch, roll])  # 欧拉角 数组
        # # 这里pitch要变为其相反数(不知道为啥)
        cv2.putText(frame, "Distance %.2f cm" % (distance),
                    (frame.shape[1] - 500, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
        # cv2.putText(frame, "%.2fcm,%.2f,%.2f,%.2f" % (distance, yaw, -pitch, roll),
        #             (frame.shape[1] - 500, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)

    except Exception:
        pass
    cv2.imshow('frame', frame)
    cv2.imshow('mask-plain', mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()