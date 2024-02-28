import easyocr
import cv2
import time as t
import pyttsx3
engine = pyttsx3.init()
reader = easyocr.Reader(['ch_sim','en'], gpu = True) # need to run only once to load model into memory

class resultype:
     value=0
     repeat=0

def count(num,numset):
    time=0
    for i in range(len(numset)):
         if(num==numset[i].value):
              time=time+1
    return time

def exist(num,numset):
    if(num==[]):
        return 2
    else:
        for i in range(len(numset)):
            if(num==numset[i].value):
                return 1
        return 0
    
def find(num,numset):
    for i in range(len(numset)):
        if(num==numset[i].value):
            return i
    return 0

def findmax(numset):
    max=0
    maxpos=0
    for i in range(len(numset)):
        if(numset[i].repeat>max):
            max=numset[i].repeat
            maxpos=i
    return maxpos,numset[maxpos].value

def analyzevideo():
    capture = cv2.VideoCapture(0)  
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    if capture.isOpened():
        time=1
        resultset=[]
        total=[]
        engine.say("识别开始")
        engine.runAndWait()
        t.sleep(1)
        while time:
            ret,img_src=capture.read()
            if not ret:break
            cv2.waitKey(1)
            result=resultype()
            #初始化中间变量类
            result.value = reader.readtext(img_src, allowlist ='0123456789',detail=0,min_size=100)
            print(result.value)
            #获取对一帧的处理结果
            if(not exist(result.value,total)):
                print("计入新结果")
                total.append(result)
                maxpos,max=findmax(total)
            #如果是第一次出现就将其计入总结果中
            elif(exist(result.value,total)==2):
                print("未获取到")
            else:
                total[find(result.value,total)].repeat=count(result.value,resultset)
                maxpos,max=findmax(total)
            #if(exist(result.value,total)):

            resultset.append(result)
            #无论是否已经出现过都加入到全部结果集合中
            
            #可能的处理
            cv2.imshow('Processing',img_src)
            time=time+1
            if(time==5):
                if(len(total)==0):
                    print("本次识别无结果")
                    time=1
                    resultset=[]
                    total=[]
                else:
                    print("PLEASE WAIT")
                    print("最可信结果：位于第",maxpos,"个的",max[0])
                    time=1
                    engine.say(max[0])
                    engine.runAndWait()
                    t.sleep(2)
                    resultset=[]
                    total=[]
    else:
        print('视频打开失败！')

#main
analyzevideo()