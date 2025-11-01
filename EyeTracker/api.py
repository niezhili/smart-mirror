from .eye_tracker_api import EyeTrackerAPI
from .reference import Reference
import numpy as np
import time
import threading
class api(object):
    def __init__(self,img):
        self.api = EyeTrackerAPI()
        reference = Reference(img)
        self.api.add_reference(reference)
        self.reference=reference
        self.thread=None
        self.temp=[]
        self.center=(-0.1,0.5,0.1,0.4)
        self._collecting = False
    def start_get_point(self):
        """启动采集线程，循环采集gaze_direction，每0.1秒一次"""
        if self.thread is not None and self.thread.is_alive():
            return  # 已在采集
        self.temp = []
        self._collecting = True
        def collect():
            while self._collecting:
                self.get_point()
                time.sleep(0.1)
        self.thread = threading.Thread(target=collect)
        self.thread.daemon = True
        self.thread.start()

    def end_get_point(self):
        """停止采集线程，并计算所有采集点的均值"""
        self._collecting = False
        if self.thread is not None:
            self.thread.join()
        if self.temp:
            arr = np.array(self.temp)
            return tuple(np.mean(arr, axis=0))
        else:
            return (0.0, 0.0)
    def calibrate(self,up,down,left,right,center):
        self.center=((left[0]+center[0]*3)/4,center[1],(right[0]+center[0]*3)/4,(down[1]*4+center[1])/5)
    def get_point(self):
        """采集当前gaze_direction二维点并存入temp"""
        gaze = self.reference.gaze_direction
        if gaze is not None and len(gaze) == 2:
            self.temp.append([gaze[0], gaze[1]])
    def start(self):
        self.api.start()
    def stop(self):
        self.api.stop()
    def get_gaze_dir(self):
        if self.reference.gaze_direction[0]<self.center[0] and self.reference.gaze_direction[1]<self.center[3]:
            return 2;
        elif self.reference.gaze_direction[0]<self.center[0] and self.reference.gaze_direction[1]>self.center[1]:
            return 1;
        elif self.reference.gaze_direction[0]>self.center[2] and self.reference.gaze_direction[1]<self.center[3]:
            return 3;
        elif self.reference.gaze_direction[0]>self.center[2] and self.reference.gaze_direction[1]>self.center[1]:
            return 4;
        else:
            return 0;




