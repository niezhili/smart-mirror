import numpy as np
 
a=np.array([1,2,3])
b=np.array([[1,2,3],[3,9,10]])
print(np.linalg.norm(b,axis=1))
weight_map=np.array([[[1,11],[1,2],[3,26]],[[5,2],[1,89],[6,2]],[[1,2],[9,7],[1,2]]])
maxarray=np.array([weight_map[...,0].max(),weight_map[...,1].max()])
minarray=np.array([weight_map[...,0].min(),weight_map[...,1].min()])
center=(maxarray+minarray)/2.0
length=(maxarray-minarray)/2.0
print(maxarray)
print(np.subtract(weight_map,center)/length)