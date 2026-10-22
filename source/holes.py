import trimesh, numpy as np, sys
m = trimesh.load(sys.argv[1])
z0,z1,st=[float(x) for x in sys.argv[2:5]]
for z in np.arange(z0,z1+1e-6,st):
    s = m.section(plane_origin=[0,0,z], plane_normal=[0,0,1])
    if s is None: print(round(z,2),'none'); continue
    out=[]
    for ent in s.discrete:
        c=ent.mean(0); e=ent.max(0)-ent.min(0)
        if c[0]>-25 and c[1]<30:
            out.append(f'({c[0]:.1f},{c[1]:.1f}) {e[0]:.1f}x{e[1]:.1f}')
    print(round(z,2),' | '.join(out))
