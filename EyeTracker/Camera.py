import cv2
import threading
import time


def create_camera_source(camera_index):
    if camera_index not in camera.camera_resource.keys():
        with camera.lock:
            camera.camera_resource[camera_index]=[cv2.VideoCapture(camera_index),1,threading.Lock(),None]
def add_reader(camera_index):
    if camera_index not in camera.camera_resource.keys():
        create_camera_source(camera_index)
    else:
        with camera.camera_resource[camera_index][2]:
            camera.camera_resource[camera_index][1]+=1
def read():
    while True:
        delete=[]
        for camera_index in camera.camera_resource.keys():
            if camera.camera_resource[camera_index][1]==0:
                camera.camera_resource[camera_index][0].release()
                delete.append(camera_index)
                continue
            ret, frame = camera.camera_resource[camera_index][0].read()
            if ret:
                with camera.camera_resource[camera_index][2]:
                    camera.camera_resource[camera_index][3] = cv2.flip(frame,1)
        for camera_index in delete:
            del camera.camera_resource[camera_index]
        time.sleep(1.0 / 30)

class camera(object):
    lock=threading.Lock()
    camera_resource={}
    camera_threadings=threading.Thread(target=read,daemon=True)
    def __init__(self,camera_index):  
        self.camera_index=camera_index
        add_reader(self.camera_index)
    def get_frame(self):
        if camera.camera_resource[self.camera_index][3] is None:
            return None
        return camera.camera_resource[self.camera_index][3].copy()
    def release(self):
        with camera.camera_resource[self.camera_index][2]:
            camera.camera_resource[self.camera_index][1]-=1
                
                    




