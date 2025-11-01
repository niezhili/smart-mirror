import keyboard
from EyeTracker.api import api
import cv2
reference_image = cv2.imread("without glasses.jpg")
api=api(reference_image);
api.start();
print("请按W键开始校准...")
keyboard.wait('w')
api.start_get_point();
print("请注视上点，按空格键完成校准...")
keyboard.wait('space')
up=api.end_get_point()
print("请按A键开始校准...")
keyboard.wait('a')
api.start_get_point();
print("请注视左点，按空格键完成校准...")
keyboard.wait('space')
left=api.end_get_point()
print("请按S键开始校准...")
keyboard.wait('s')
api.start_get_point();
print("请注视下点，按空格键完成校准...")
keyboard.wait('space')
down=api.end_get_point()
print("请按D键开始校准...")
keyboard.wait('d')
api.start_get_point();
print("请注视右点，按空格键完成校准...")
keyboard.wait('space')
right=api.end_get_point()
print("请按空格键开始校准...")
keyboard.wait('space')
api.start_get_point();
print("请注视右点，按空格键完成校准...")
keyboard.wait('space')
center=api.end_get_point()
api.calibrate(up,down,left,right,center);
while(True):
    print(api.get_gaze_dir());
    if keyboard.is_pressed('p'):
        print("检测到空格键，退出程序...")
        break
api.stop();