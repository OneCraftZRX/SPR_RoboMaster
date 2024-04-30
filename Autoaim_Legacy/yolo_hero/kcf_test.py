import cv2
import torch
import time
from imutils.video import WebcamVideoStream#双线程读取视频类
from imutils.video import FPS#计算帧率类
from Predict.kalmanfilter import KalmanFilter#卡尔曼预测类
from KCF import KCF_follow

def draw(list_temp, image_temp):
        for temp in list_temp:
            name = temp[6]      # 取出标签名
            temp = temp[:4].astype('int')   # 转成int加快计算
            cv2.rectangle(image_temp, (temp[0], temp[1]), (temp[2], temp[3]), (0, 0, 255), 3)  # 框出识别物体
            cv2.putText(image_temp, name, (int(temp[0]-10), int(temp[1]-10)), cv2.FONT_ITALIC, 1, (0, 255, 0), 2)

# 检测识别, 加载模型
# 项目名, custom自定义 path权重路径
model = torch.hub.load('E:/yolov5-7.0', 'custom', path='E:/yolov5-7.0/weights/best.pt', source='local')
#model=torch.load("E:/yolov5-7.0/weights/yolov5s.pt",map_location=torch.device('cpu'))
#model = torch.hub.load('E:/yolov5-7.0', 'yolov5s', device='cpu')
# 置信度阈值
model.conf = 0.6
# 加载摄像头
#cap = WebcamVideoStream().start()
cap = cv2.VideoCapture('E:/yolov5-7.0/data/images/red5.mp4')

#实例化kcf对象
kf=KCF_follow()


fps = FPS().start()
while fps._numFrames<100:
    frame = cap.read()
    fps.update()
    # 翻转图像
    # 转换rgb
    img_cvt = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # 记录推理消耗时间   FPS
    start_time = time.time()
    # 推理
    results = model(img_cvt)
    pd = results.pandas().xyxy[0]
    print(pd)

    # 取出对应标签的list
    car_list = pd[pd['name'] == 'car'].to_numpy()
    five_list = pd[pd['name'] == '5'].to_numpy()
    # 框出物体
    draw(car_list, frame)
    draw(five_list, frame)

    end_time = time.time()
    fps_text = 1/(end_time-start_time)
    print("帧率",fps_text)
    if( fps_text<30):
        cv2.putText(frame, "FPS: " + str(round(fps_text, 2)), (30, 50),cv2.FONT_ITALIC, 1, (255, 255, 255), 2)
    cv2.imshow('test', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
# 做一些清理工作
cv2.destroyAllWindows()
# cap.stop()
