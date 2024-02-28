import cv2
import numpy as np

videoinpath = './RC2.mp4'
videooutpath = './RC_out.mp4'
capture = cv2.VideoCapture(videoinpath)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
writer = cv2.VideoWriter(videooutpath ,fourcc, 24.0, (640,480), True)

def distance(x1,y1,x2,y2):
    return ((x1-x2)**2+(y1-y2)**2)**0.5

# 找线
def Find_Line(frame, binary):
    global x, y, img
    # 1 找出所有轮廓
    bin2, contours, hierarchy = cv2.findContours(binary,1,cv2.CHAIN_APPROX_NONE)
    
    # 2 找出最大轮廓
    if len(contours) > 0:
        # 最大轮廓
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)
 
        # 中心点坐标
        x = int(M['m10'] / M['m00'])
        y = int(M['m01'] / M['m00'])
        #print(x, y)
 
        # 显示
        img = frame.copy()
        # 标出中心位置
        cv2.line(img, (x, 0), (x, 720), (0, 0, 255), 1)
        cv2.line(img, (0, y), (1280, y), (0, 0, 255), 1)
        # 画出轮廓
        cv2.drawContours(img, contours, -1, (128, 0, 128), 2)
        cv2.imshow("image", img)
 
    else:
        print("not found the line")
 
        (x,y) = (0, 0)

def process(img):
    width=img.shape[0]
    length=img.shape[1]
    print("width:",width,"length:",length)
    knlval=6
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_gray_and_white = np.array([0,0,46])
    upper_gray_and_white = np.array([180,60,255])
    mask = cv2.inRange(hsv, lower_gray_and_white, upper_gray_and_white)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(knlval,knlval))
    dilate = cv2.dilate(mask, kernel, 10)
    # thresh1 = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    cv2.imshow("hsv",dilate)

    contours, hierarchy = cv2.findContours(dilate,1,cv2.CHAIN_APPROX_NONE)
    #找出最大轮廓
    if len(contours) > 0:
        # 最大轮廓
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)

        # 中心点坐标
        x = int(M['m10'] / M['m00'])
        y = int(M['m01'] / M['m00'])

        #最小外包矩形
        rect = cv2.minAreaRect(c)
        box = cv2.boxPoints(rect)

        #求矩形四个顶点
        pbox= cv2.boxPoints(rect)
        pbox = np.intp(pbox)

        allxy=[(pbox[0][0],pbox[0][1]),(pbox[1][0],pbox[1][1]),(pbox[2][0],pbox[2][1]),(pbox[3][0],pbox[3][1])]
        allxy.sort(key=lambda x:x[0])
        allxy.sort(key=lambda x:x[1])
        print(allxy)

        #上中点
        x1=int((allxy[0][0]+allxy[1][0])/2)
        y1=int((allxy[0][1]+allxy[1][1])/2)
        #下中点
        x2=int((allxy[2][0]+allxy[3][0])/2)
        y2=int((allxy[2][1]+allxy[3][1])/2)
        #对角点
        x3=int(allxy[0][0])
        y3=int(allxy[0][1])
        x4=int(allxy[3][0])
        y4=int(allxy[3][1])

        w=distance(allxy[0][0],allxy[0][1],allxy[1][0],allxy[1][1])
        h=distance(allxy[0][0],allxy[0][1],allxy[3][0],allxy[3][1])

        #计算长宽比
        if w>h:
            ratio=w/h
        else:
            ratio=h/w
        print("ratio:",ratio)

        if(ratio>=5):
            #画出中轴线
            cv2.line(img, (x1,y1), (x2,y2), (255,0,0), 2)
            #计算中轴线与竖直线夹角
            if(x1==x2):
                k=90
            else:
                k=(y2-y1)/(x2-x1)
            angle=90-(np.arctan(abs(k))*180/np.pi)
            #显示角度
            cv2.putText(img, "Angle: "+str('%.2f'%angle), (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 0, 0), 2)
            #显示白线中轴线与图片中心点的横向距离（取轴线上与中心点Y方向相同的点）
            b=y1-k*x1
            xn=(120-b)/k
            cv2.circle(img,(int(xn),120), 5, (0,0,255), -1)
            cv2.circle(img,(160,120), 5, (0,255,0), -1)
            cv2.putText(img, "Distance: "+str('%.2f'%abs(xn-160)), (10, 60), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 0, 0), 2)
            # 画出轮廓
            cv2.drawContours(img, [np.intp(box)], 0, (0, 0, 255), 2)

        else:
            img_split1=dilate[0:width,0:int(length/2)]
            img_split2=dilate[0:width,int(length/2):length]
            white_area1 = cv2.countNonZero(img_split1)
            white_area2 = cv2.countNonZero(img_split2)
            whiteabs=abs(white_area1-white_area2)

            if(whiteabs>5500):
                print("转弯")   
                #画出对角线
                cv2.line(img, (x3,y3), (x4,y4), (255,0,0), 2)
                #计算中轴线与竖直线夹角
                if(x3==x4):
                    k=0
                else:
                    k=(y4-y3)/(x4-x3)
                angle=(np.arctan(k)*180/np.pi)
                #显示角度
                cv2.putText(img, "Turn: "+str('%.2f'%angle), (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 0, 0), 2)
                # 画出轮廓
                cv2.drawContours(img, [np.intp(box)], 0, (0, 0, 255), 2)

            else:
                cv2.putText(img, "Cross found", (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 0, 0), 2)
            print("whiteabs",whiteabs)
            
        # 标出中心位置
        cv2.line(img, (x, 0), (x, 480), (0, 0, 255), 1)
        cv2.line(img, (0, y), (640, y), (0, 0, 255), 1)

        # cv2.putText(img, "Area:"+str(area), (10, 60), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
        # cv2.putText(img, "Perimeter:"+str('%.1f'%perimeter), (10, 90), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
        # cv2.putText(img, "Zhang Rongxi", (10, 120), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
        cv2.imshow("image", img)

if capture.isOpened():
    while True:
        ret,img=capture.read()
        if not ret:break
        # img=cv2.imread(r"C:\Users\25176\OneDrive\Codes\SPR2024\TestGit\examine\examine3\7m.png")
        img = cv2.resize(img, (0,0), fx=0.5, fy=0.5)
        
        process(img)

        cv2.waitKey(0)
        #print("processed1img")
        # writer.write(img_out)
else:
    print('视频打开失败！')
writer.release()
print("over")