# # import the necessary packages
# #利用线程读取
# from threading import Thread
# import cv2
# class WebcamVideoStream:
# 	def __init__(self, src=0):
# 		# 初始化摄像机流并从流中读取第一帧
# 		self.stream = cv2.VideoCapture(src)
# 		(self.grabbed, self.frame) = self.stream.read()
# 		# 初始化用于指示线程是否应该停止的变量
# 		self.stopped = False
# 	def start(self):
# 		# 启动线程从视频流中读取帧
# 		Thread(target=self.update, args=()).start()
# 		return self
# 	def update(self):
# 		# 继续无限循环，直到线程停止
# 		while True:
# 			# 如果设置了线程指示器变量，则停止线程
# 			if self.stopped:
# 				return
# 			# 否则，从流中读取下一帧
# 			(self.grabbed, self.frame) = self.stream.read()
# 	def read(self):
# 		# 返回最近读取的帧
# 		return self.frame
# 	def stop(self):
# 		# 表示应该停止线程
# 		self.stopped = True





# import the necessary packages
from threading import Thread
import cv2
from Camera.Mindvision import Mindvision
import numpy
import time
class WebcamVideoStream:
	def __init__(self, name="WebcamVideoStream"):
		#initialize the video camera stream and read the first frame
		#from the stream
		# self.stream = cv2.VideoCapture(0)
		# (self.grabbed, self.frame) = self.stream.read()

		self.mind=Mindvision()
		self.mind.camera_init()
		self.src=numpy.zeros((640,640),dtype=numpy.uint8)
		self.frame=self.mind.getframe(self.src)   	

		# initialize the thread name          
		self.name = name

		# initialize the variable used to indicate if the thread should
		# be stopped
		self.stopped = False

	def start(self):
		# start the thread to read frames from the video stream,线程函数是updat()
		t = Thread(target=self.update, name=self.name, args=())
		#t=multiprocessing.Process(target=self.update, name=self.name, args=())
		t.daemon = True
		t.start()

		return self

	def update(self):
		# keep looping infinitely until the thread is stopped
		#print("进入相机采集线程")
  
		while True:
			time_start=time.time()
			# if the thread indicator variable is set, stop the thread
			if self.stopped:
				return

			# otherwise, read the next frame from the stream
			# (self.grabbed, self.frame) = self.stream.read()
			self.frame=self.mind.getframe(self.src)

			# #将采集到的图像放入队列
			#share_queue.shared_queue_image.put(self.frame)
			#print("读取到的数据",share_queue.shared_queue_image.get())
			#print("存放的数据",self.frame)
			
			time_end=time.time()
			#print("相机采集帧率",1/(time_end-time_start))

	def read(self):#用来信息交互的接口
		# return the frame most recently read
		return self.frame

	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True
		self.mind.colse()

