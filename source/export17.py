exec(open('build17.py').read())
import glob, os
os.makedirs(OUT,exist_ok=True)
handle=to_mf(trimesh.load(U+'euc_master_front_handle.stl'))+handle_adds3()
to_tm(handle).export(OUT+'master_handle_v12.stl'); to_tm(handle).export('handle12.stl')
def flat(m): b=m.bounding_box(); return m.translate([-(b[0]+b[3])/2,-(b[1]+b[4])/2,-b[2]])
to_tm(flat(housing3().rotate([180,0,0]))).export(OUT+'lamp5_housing.stl')          # top on the bed
to_tm(flat(head3().rotate([0,90,0]))).export(OUT+'lamp5_head.stl')                 # open back on the bed
to_tm(flat(lid3())).export(OUT+'lamp5_lid.stl')                                    # outside face on the bed
to_tm(flat(diffuser3(1).rotate([0,90,0]))).export(OUT+'lamp5_drl_diffuser_x2.stl')
for f in sorted(glob.glob(OUT+'lamp5_*.stl'))+[OUT+'master_handle_v12.stl']:
    t=trimesh.load(f); print(f.split('/')[-1],'watertight',t.is_watertight,'bodies',len(t.split(only_watertight=False)),'size',np.round(t.extents,1))
