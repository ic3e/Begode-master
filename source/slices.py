import trimesh, numpy as np, sys
m = trimesh.load(sys.argv[1])
axis = int(sys.argv[2]); levels=[float(x) for x in sys.argv[3:]]
n = np.zeros(3); n[axis]=1
for z in levels:
    o = np.zeros(3); o[axis]=z
    s = m.section(plane_origin=o, plane_normal=n)
    if s is None: print(z,'none'); continue
    p,_ = s.to_2D(to_3D=None) if False else (None,None)
    # get polygons in world coords
    for i,ent in enumerate(s.discrete):
        lo,hi = ent.min(0), ent.max(0)
        c = ent.mean(0); ext=hi-lo
        print(f'{"XYZ"[axis]}={z}: loop{i} n={len(ent)} center={c.round(2)} ext={ext.round(2)}')
