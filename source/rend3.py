import trimesh,sys
sys.path.insert(0,'.')
from render import render
O='../out/'
h=trimesh.load(O+'master_handle_v2.stl'); c=trimesh.load('../reference/euc_master_front_handle_p2.stl')
# STL frame -> wheel frame for the pictures: x=forward(-X), y=across(Z), z=up(Y)
import numpy as np
T=np.array([[-1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1.]])
def w(m): m=m.copy(); m.apply_transform(T); return m
V=((15,-150),(15,-110),(0,-90),(0,180),(60,-135),(-20,-160))
render([w(h),w(c),w(trimesh.load('v2_cup_open.stl'))],O+'preview_v2_open.png',views=V)
render([w(h),w(c),w(trimesh.load('v2_cup_fold.stl'))],O+'preview_v2_folded.png',views=V)
