import trimesh,sys
sys.path.insert(0,sys.argv[1])
from render import render
O='../build_output/'
h=trimesh.load(O+'master_handle_cupside_A.stl'); c=trimesh.load(O+'master_handle_top_cap_p2.stl')
render([h,c,trimesh.load('cup_open_A.stl')],'open_A.png',views=((20,-60),(20,30),(90,-90),(0,-45),(0,45),(-25,150)))
render([h,c,trimesh.load('cup_fold_A.stl')],'fold_A.png',views=((20,-60),(20,30),(90,-90),(0,-45),(0,45),(-25,150)))
