import ncsyproclib as mylib
import cv2
import os

def sortcnt(cnts):
    length=len(cnts)
    cnts_sorted=[]
    for i in range(length-1):
        if cv2.contourArea(cnts[i])>=1000 and cv2.contourArea(cnts[i])<=1500:
            cnts_sorted.append(cnts[i])
    return cnts_sorted

def process(path,thresholdval,knlval):
    # print(os.getcwd())
    # img=cv2.imread(r"C:\Users\25176\OneDrive\Codes\SPR2024\TestGit\examine\examine1\1.bmp")
    img=cv2.imread(path)
    binary=mylib.ncsyprocs.open_with_threshold(img,1,thresholdval,knlval)
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
    # binary=cv2.erode(binary,kernel,iterations=1)
    cv2.imshow("1",binary)
    # binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    contours=sortcnt(contours)

    for i in range(len(contours)-1):
        M = cv2.moments(contours[i])#计算第一条轮廓的各阶矩,字典形式
        #这两行是计算中心点坐标
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        #计算轮廓所包含的面积
        area = cv2.contourArea(contours[i])
        #计算轮廓的周长
        # 第二参数可以用来指定对象的形状是闭合的(True),还是打开的(一条曲线)。
        perimeter = cv2.arcLength(contours[i],False)
        cv2.putText(img, "Center:("+str(cx)+","+str(cy)+")", (30, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(img, "Area:"+str(area), (30, 200), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(img, "Perimeter:"+str('%.1f'%perimeter), (30, 150), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(img, "Zhang Rongxi", (30, 250), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
        cv2.circle(img, (cx, cy), 2, (255, 0, 0), 2)
    cv2.drawContours(img, contours, 0, (255, 0, 0), 2)  # 改变的是img这张图
    cv2.imshow('findedge', img)
    cv2.imwrite(r"C:\Users\25176\OneDrive\Codes\SPR2024\TestGit\examine\examine1\9-.bmp",img)
    cv2.waitKey(0)

#1.bmp:175,10
#2.bmp:163,26
#9.bmp:206,8

process(r"C:\Users\25176\OneDrive\Codes\SPR2024\TestGit\examine\examine1\9.bmp",206,8)
cv2.waitKey(0)


# def trackChaned(x):
#   pass
# cv2.namedWindow('Color Track Bar')
# hh='Max'
# hl='Min'
# wnd = 'Colorbars'
# cv2.createTrackbar("Max", "Color Track Bar",1,255,trackChaned)
# cv2.createTrackbar("Min", "Color Track Bar",1,255,trackChaned)
# img = cv2.imread(r"C:\Users\25176\OneDrive\Codes\SPR2024\TestGit\examine\examine1\2.bmp")
# img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# img = cv2.resize(img, (0,0), fx=0.5, fy=0.5)
 
# while(True):
#     the=cv2.getTrackbarPos("Max", "Color Track Bar")
#     knl=cv2.getTrackbarPos("Min", "Color Track Bar")
#     process(r"C:\Users\25176\OneDrive\Codes\SPR2024\TestGit\examine\examine1\2.bmp",the,knl)