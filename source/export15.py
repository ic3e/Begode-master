exec(open('build15.py').read())
import glob
handle=to_mf(trimesh.load(U+'euc_master_front_handle.stl'))+holder10()
to_tm(handle).export(OUT+'master_handle_v10.stl'); to_tm(handle).export('handle10.stl')
def flat(m): b=m.bounding_box(); return m.translate([-(b[0]+b[3])/2,-(b[1]+b[4])/2,-b[2]])
up=lambda m: m.rotate([90,0,0])          # basket coords have y up -> print with that axis up
to_tm(flat(up(gimbal_ring()))).export(OUT+'cup3_gimbal_ring.stl')
to_tm(flat(up(cup_ring()))).export(OUT+'cup3_ring.stl')
to_tm(flat(up(floor_disc()))).export(OUT+'cup3_floor.stl')
to_tm(flat(arm_local(1).rotate([180,0,0]))).export(OUT+'cup3_swing_arm_right.stl')
to_tm(flat(arm_local(-1))).export(OUT+'cup3_swing_arm_left.stl')
for f in sorted(glob.glob(OUT+'cup3_*.stl'))+[OUT+'master_handle_v10.stl']:
    t=trimesh.load(f); print(f.split('/')[-1],'watertight',t.is_watertight,'bodies',len(t.split(only_watertight=False)),'size',np.round(t.extents,1))
