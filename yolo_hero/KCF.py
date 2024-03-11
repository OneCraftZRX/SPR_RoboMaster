import argparse
import cv2
import time


class KCF_follow():
    def __init__(self):
        #参数加载
        ap=argparse.ArgumentParser()

        ap.add_argument('-t', '--tracker', type=str,
                        default='kcf', help='Opencv object tracker type')

        self.args = vars(ap.parse_args())

        self.OPENCV_OBJECT_TRACKERS = {
            "csrt": cv2.TrackerCSRT_create,
            "kcf": cv2.TrackerKCF_create,
            "boosting": cv2.TrackerBoosting_create,
            "mil": cv2.TrackerMIL_create,
            "tld": cv2.TrackerTLD_create,
            "medianflow": cv2.TrackerMedianFlow_create,
            "mosse": cv2.TrackerMOSSE_create}

        # 第二步：实例化追踪器
        # 实例化Opencv's multi-object tracker
        self.trackers= cv2.MultiTracker_create()



    def run(self,src):
        #第三步,载入图片
        self.frame=src

        if self.frame is None:
            print("载入图片失败，请检查视频流是否正确")

        else:
        # 第四步：使用cv2.resize对图像进行长宽的放缩操作
            h, w = self.frame.shape[:2]
            width = 600
            r = width / float(w)
            dim = (width, int(r * h))
            self.frame = cv2.resize(self.frame, dim, cv2.INTER_AREA)


        # 第五步：使用trackers.apply获得矩形框,success是bool类型，boxes是tuple类型,空元组
        (success, boxes) = self.trackers.update(self.frame)

        # 第六步：循环多组矩形框，进行画图操作
        for box in boxes:
            (x, y, w, h) = [int(v) for v in box]
            cv2.rectangle(self.frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # 第九步：进行图像展示
            cv2.imshow('Frame', self.frame)

            # 第十步：判断按键，如果是s的话，进行画出新的box
            key = cv2.waitKey(10) & 0xff

            if key == ord('s'):
                # 第十一步：选择一个区域，按s键，并将tracker追踪器，frame和box传入到trackers中
                box = cv2.selectROI('Frame', self.frame, fromCenter=False,
                                    showCrosshair=True)
                tracker = self.OPENCV_OBJECT_TRACKERS[self.args['tracker']]()
                self.trackers.add(tracker, self.frame, box)

            elif key == 27:
                break

    def stop(self):
        cv2.destroyAllWindows()