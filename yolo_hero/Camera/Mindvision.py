import cv2
import numpy as np
import Camera.mvsdk 
import platform


class Mindvision:

    def camera_init(self):
        self.DevList = Camera.mvsdk.CameraEnumerateDevice()
        for i, DevInfo in enumerate(self.DevList):
            print("{}: {} {}".format(i, DevInfo.GetFriendlyName(), DevInfo.GetPortType()))
        # i = 0 if self.nDev == 1 else int(input("Select camera: "))
        i = 0
        DevInfo = self.DevList[i]
        print(DevInfo)

        # 打开相机
        self.hCamera = 0
        #查看相机是否正常初始化
        try:
            self.hCamera = Camera.mvsdk.CameraInit(DevInfo, -1, -1)
        #返回报错信息
        except Camera.mvsdk.CameraException as e:
            print("CameraInit Failed({}): {}".format(e.error_code, e.message) )
            #return
            return Mindvision

        # 获取相机特性描述
        cap = Camera.mvsdk.CameraGetCapability(self.hCamera)

        #加载相机参数文件,加载成功返回0
        parameter=1
        parameter=Camera.mvsdk.CameraReadParameterFromFile(self.hCamera,"D:\\source\\YOLO\\yolo_hero\\Camera\\camera_windows_night_camera2.Config")
        print("相机参数加载",parameter)

        #print("xiangjicanshu ",parameter)
        # 相机模式切换成连续采集
        Camera.mvsdk.CameraSetTriggerMode( self.hCamera, 0)

        # 让SDK内部取图线程开始工作
        Camera.mvsdk.CameraPlay(self.hCamera)

        # 计算RGB buffer所需的大小，这里直接按照相机的最大分辨率来分配
        FrameBufferSize = cap.sResolutionRange.iWidthMax * cap.sResolutionRange.iHeightMax * (3)

        # 分配RGB buffer，用来存放ISP输出的图像
	    # 备注：从相机传输到PC端的是RAW数据，在PC端通过软件ISP转为RGB数据（如果是黑白相机就不需要转换格式，但是ISP还有其它处理，所以也需要分配这个buffer）
        self.pFrameBuffer = Camera.mvsdk.CameraAlignMalloc(FrameBufferSize, 16)

    def getframe(self,src):
        try:
            pRawData, FrameHead = Camera.mvsdk.CameraGetImageBuffer(self.hCamera, 200)
            Camera.mvsdk.CameraImageProcess(self.hCamera, pRawData, self.pFrameBuffer, FrameHead)
            Camera.mvsdk.CameraReleaseImageBuffer(self.hCamera, pRawData)

            # windows下取到的图像数据是上下颠倒的，以BMP格式存放。转换成opencv则需要上下翻转成正的
            # linux下直接输出正的，不需要上下翻转
            if platform.system() == "Windows":
                Camera.mvsdk.CameraFlipFrameBuffer(self.pFrameBuffer, FrameHead, 1)

            # 此时图片已经存储在pFrameBuffer中，对于彩色相机pFrameBuffer=RGB数据，黑白相机pFrameBuffer=8位灰度数据
            # 把pFrameBuffer转换成opencv的图像格式以进行后续算法处理
            frame_data = (Camera.mvsdk.c_ubyte * FrameHead.uBytes).from_address(self.pFrameBuffer)
            frame = np.frombuffer(frame_data, dtype=np.uint8)
            frame = frame.reshape((FrameHead.iHeight, FrameHead.iWidth, 1 if FrameHead.uiMediaType == Camera.mvsdk.CAMERA_MEDIA_TYPE_MONO8 else 3) )
            #print(frame.size)
            #print(frame.height)
            
            frame = cv2.resize(frame, (416,416), interpolation = cv2.INTER_LINEAR)
            src=frame

        
        except Camera.mvsdk.CameraException as e:
            if e.error_code != Camera.mvsdk.CAMERA_STATUS_TIME_OUT:
                print("CameraGetImageBuffer failed({}): {}".format(e.error_code, e.message) )

        return src

    def colse(self):
	    # 关闭相机
        Camera.mvsdk.CameraUnInit(self.hCamera)

        #释放帧缓存
        Camera.mvsdk.CameraAlignFree(self.pFrameBuffer)



