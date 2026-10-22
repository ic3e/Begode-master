# Lamp v6.2 STLs, each lying on the bed the way it should print, centred, lowest point at z = 0.
exec(open('build24.py').read())
import glob, os
OUTD='../build_output/'                # superseded by export25.py, which writes current/stl/
os.makedirs(OUTD,exist_ok=True)
def put(m,name):   # centre on x/y, lowest point on the bed; no zero-area triangles for the slicer to "repair"
    t=m if isinstance(m,trimesh.Trimesh) else clean_tm(to_tm(m.simplify(0.001)))
    lo,hi=t.bounds; t.apply_translation([-(lo[0]+hi[0])/2,-(lo[1]+hi[1])/2,-lo[2]]); t.export(OUTD+name)
put(housing11().rotate([-90,0,0]),'lamp62_housing.stl')          # open top on the bed: the plate's seat and the face come out true
put(top_plate11().rotate([-90,0,0]),'lamp62_top_plate.stl')      # top face on the bed, tongues and fingers up
put(lens_frame7().rotate([0,-90,0]),'lamp62_lens_frame.stl')     # front face on the bed: the lens lips are the first layers
put(lid10().rotate([90,0,0]),'lamp62_lid.stl')
# the handle lies with its U flat (the plane of its legs and grip on the bed): every layer runs along the legs
# and the grip, so a fall onto the grip pulls along the filament, not between layers
for side,nm in ((1,'right'),(-1,'left')):
    t=clean_tm(to_tm(handle14(side))); n=np.array([0.71,0.70,0.0]); n/=np.linalg.norm(n)   # the U's normal (its thinnest axis)
    t.apply_transform(trimesh.geometry.align_vectors(-n,[0,0,1])); put(t,f'master_handle_v14_usb_{nm}.stl')
put(trimesh.load(U+'euc_master_front_handle_p2.stl'),'master_handle_top_cap_p2.stl')   # your stock cap, flat side down
pts=window_outline(); W_=2*WIN_W; H_=WIN_Y1-WIN_Y0
path=' '.join(('M' if i==0 else 'L')+f'{w+WIN_W:.2f},{WIN_Y1-y:.2f}' for i,(w,y) in enumerate(pts))+' Z'
open(OUTD+'lamp62_window_1.5mm_polycarbonate.svg','w').write(
 f'<svg xmlns="http://www.w3.org/2000/svg" width="{W_:.1f}mm" height="{H_:.1f}mm" viewBox="0 0 {W_:.2f} {H_:.2f}">'
 f'<path d="{path}" fill="none" stroke="black" stroke-width="0.2"/></svg>')
for f in sorted(glob.glob(OUTD+'*.stl')):
    t=trimesh.load(f); print(os.path.basename(f),'watertight',t.is_watertight,'bodies',len(t.split(only_watertight=False)),'size',np.round(t.extents,1))
