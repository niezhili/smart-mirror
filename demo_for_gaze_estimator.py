import time
from GazeEstimator.debugger import gaze_estimator_debug_api
import cv2

api = gaze_estimator_debug_api("without glasses.jpg")
api.start()

flag=True
while True:
    img = api.get_debug_image()
    print(str(api.get())+" "+str(api.get_weight()))
    if img is not None and flag:
        cv2.imshow("result", img)
    elif api.get_frame() is not None and not flag:
        cv2.imshow("result", api.get_frame())
    # 每隔30ms刷新一次窗口
    if cv2.waitKey(5) & 0xFF == ord("q"):
        break
    if cv2.waitKey(5) & 0xFF == ord("p"):
        flag= not flag

cv2.destroyAllWindows()
api.stop()


