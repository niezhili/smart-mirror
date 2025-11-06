from GazeEstimator.gaze_estimator_api import gaze_estimator_api
api=gaze_estimator_api("with glasses.jpg")
api.start()
result=api.get()
print(result)
api.stop()

