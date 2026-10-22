exec(open('build14.py').read())
handle=to_mf(trimesh.load(U+'euc_master_front_handle.stl'))+holder8()
to_tm(handle).export(OUT+'master_handle_v9.stl'); to_tm(handle).export('handle9.stl')
def flat(m): b=m.bounding_box(); return m.translate([-(b[0]+b[3])/2,-(b[1]+b[4])/2,-b[2]])
to_tm(flat(arm(1,0).rotate([180,0,0]))).export(OUT+'cup2_slide_arm_right.stl')
to_tm(flat(arm(-1,0))).export(OUT+'cup2_slide_arm_left.stl')
for k,r in enumerate(basket(True)):
    to_tm(flat(r.rotate([90,0,0]))).export(OUT+f'cup2_ring{k+1}.stl')
to_tm(flat(gimbal_ring().rotate([90,0,0]))).export(OUT+'cup2_gimbal_ring.stl')   # flat side down
import glob
for f in sorted(glob.glob(OUT+'cup2_*.stl'))+[OUT+'master_handle_v9.stl']:
    t=trimesh.load(f); print(f.split('/')[-1],'watertight',t.is_watertight,'bodies',len(t.split(only_watertight=False)),'size',np.round(t.extents,1),'z0',round(t.bounds[0][2],2))
