# What a slicer would trip over, checked on the STLs in current/stl before anyone prints them, in the
# orientation they are exported in (lying on the bed as they should print):
# - a mesh that isn't one closed solid, or a part not lying flat and centred on the bed;
# - walls thinner than a 0.4 mm nozzle can draw (the slicer drops them or leaves holes), and floors thinner
#   than one 0.2 mm layer; knife edges are listed but harmless;
# - slits under 0.3 mm between parallel faces (the slicer fuses them, or leaves a hairline void);
# - overhangs, layer by layer like a slicer: what bridges, what needs support, and whether that support
#   stands on the bed or on the part itself;
# - curves cut into facets coarse enough to see.
# python3 print_check.py [folder]      (default ../current/stl/)
import numpy as np, trimesh, glob, sys, os
from matplotlib.path import Path
from scipy import ndimage
D=sys.argv[1] if len(sys.argv)>1 else '../current/stl/'
BED=(220,220,220)            # the smallest common bed (Ender 3 / Prusa Mini class)
NOZ,LAYER=0.4,0.2
def rays(t,o,d):
    loc,ir,it=t.ray.intersects_location(o,d,multiple_hits=False); r=np.full(len(o),np.inf); f=np.full(len(o),-1)
    if len(ir): r[ir]=np.linalg.norm(loc-o[ir],axis=1); f[ir]=it
    return r,f
def supports(t,P=0.4,LH=LAYER,SPAN=25.0,LEDGE=2.0):
    b=t.bounds; xs=np.arange(b[0][0]-1,b[1][0]+1,P); ys=np.arange(b[0][1]-1,b[1][1]+1,P); zs=np.arange(LH/2,b[1][2],LH)
    X,Y=np.meshgrid(xs,ys,indexing='ij'); pts=np.c_[X.ravel(),Y.ravel()]
    L=np.zeros((len(zs),len(xs),len(ys)),bool)
    for k,z in enumerate(zs):
        s=t.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
        if s is None: continue
        occ=np.zeros(len(pts),int)
        for e in s.discrete: occ^=Path(e[:,:2]).contains_points(pts)
        L[k]=occ.reshape(len(xs),len(ys)).astype(bool)
    st=ndimage.generate_binary_structure(2,1); grow=max(1,int(round(LH*np.tan(np.radians(50))/P)))
    need=np.zeros_like(L); bridged=0.0
    for k in range(1,len(zs)):
        sup=ndimage.binary_dilation(L[k-1],st,iterations=grow); un=L[k]&~sup
        if not un.any(): continue
        anch=L[k]&sup; ok=np.zeros_like(un)
        for ax in (0,1):   # straight bridges between two anchored ends, no longer than SPAN
            A=un if ax==0 else un.T; N=anch if ax==0 else anch.T; O=np.zeros_like(A)
            for i in np.flatnonzero(A.any(1)):
                idx=np.flatnonzero(np.diff(np.r_[0,A[i].astype(int),0]))
                for s0,s1 in zip(idx[::2],idx[1::2]):
                    if s0>0 and s1<A.shape[1] and N[i][s0-1] and N[i][s1] and (s1-s0)*P<=SPAN: O[i][s0:s1]=True
            ok|=O if ax==0 else O.T
        lab,n=ndimage.label(un&~ok,st)
        if n:            # anchored on most of its outline (angled slots, round holes) and narrow enough
            edt=ndimage.distance_transform_edt(~anch)*P
            for c in range(1,n+1):
                comp=lab==c; ring=ndimage.binary_dilation(comp,st)&~comp
                if ring.sum() and (ring&anch).sum()/ring.sum()>=0.85 and edt[comp].max()<=SPAN/2: ok|=comp
        short=ndimage.distance_transform_edt(~anch)*P<=LEDGE
        bridged+=ok.sum()*P*P; need[k]=un&~ok&~short
    onpart=sum(L[:k,i,j].any() for k,i,j in np.argwhere(need))*P*P
    return bridged,need.sum()*P*P,onpart
def check(f,support=True):
    t=trimesh.load(f); name=os.path.basename(f); out=[]
    ok=lambda c,msg: out.append(('  ok  ' if c else '  !!  ')+msg)
    ok(t.is_watertight,'closed (watertight)'); ok(t.is_winding_consistent,'normals consistent')
    ok(t.is_volume and t.volume>0,'a solid with outward normals, %.1f cm3'%(t.volume/1000))
    nb=len(t.split(only_watertight=False)); ok(nb==1,'one body (%d)'%nb)
    deg=(t.area_faces<1e-6).sum(); ok(deg==0,'no zero-area triangles (%d)'%deg)
    lo,hi=t.bounds; ext=hi-lo
    ok(abs(lo[2])<1e-3,'on the bed (lowest point z = %.3f)'%lo[2])
    ok(np.all(np.abs((lo[:2]+hi[:2])/2)<1),'centred (%.1f, %.1f)'%tuple((lo[:2]+hi[:2])/2))
    ok(np.all(ext<=np.array(BED)),'fits a %dx%dx%d bed: %.1f x %.1f x %.1f mm'%(BED+tuple(ext)))
    bed=t.area_faces[(t.face_normals[:,2]<-0.999)&(t.triangles_center[:,2]<1e-3)].sum()
    out.append(('  ok  ' if bed>100 else '  ..  ')+'flat on the bed: %.0f mm2%s'%(bed,'' if bed>100 else ' (rests on supports: use a brim)'))
    # thickness, by rays from area-weighted points straight through the part
    rng=np.random.default_rng(1); n=8000
    fi=rng.choice(len(t.faces),size=n,p=t.area_faces/t.area); nr=t.face_normals[fi]
    p=(t.triangles[fi]*rng.dirichlet([1,1,1],n)[:,:,None]).sum(1)
    th,hf=rays(t,p-nr*1e-4,-nr); gp,gf=rays(t,p+nr*1e-4,nr)
    par=np.where(hf>=0,(t.face_normals[np.maximum(hf,0)]*nr).sum(1)<-0.95,False)      # the far face is parallel: a wall
    wall=np.abs(nr[:,2])<0.7                                                         # vertical in print: drawn by the nozzle
    tw=par&wall&(th<NOZ); tf=par&~wall&(th<LAYER*1.25)
    ok(tw.sum()==0,'no wall thinner than the nozzle, %.1f mm (%d of %d samples)'%(NOZ,tw.sum(),n))
    ok(tf.sum()==0,'no floor thinner than one layer, %.2f mm (%d)'%(LAYER,tf.sum()))
    thin=par&wall&(th<2*NOZ)&~tw
    if thin.sum(): out.append('  ..  %d samples of walls one line wide (%.1f-%.1f mm): prints, but as a single line'%(thin.sum(),NOZ,2*NOZ))
    edge=~par&(th<NOZ)
    if edge.sum(): out.append('  ..  %d samples on edges or tips thinner than %.1f mm (corners of slanted faces; harmless)'%(edge.sum(),NOZ))
    gpar=np.where(gf>=0,(t.face_normals[np.maximum(gf,0)]*nr).sum(1)<-0.95,False)
    sl=gpar&(gp<0.3); ok(sl.sum()==0,'no slit under 0.3 mm between parallel faces (%d)'%sl.sum())
    if support:
        br,need,onpart=supports(t)
        out.append('  ..  overhangs: %.0f mm2 bridge, %.0f mm2 need support (%.0f from the bed, %.0f on the part)'%(br,need,need-onpart,onpart))
    ang=np.degrees(t.face_adjacency_angles); curve=(ang>1)&(ang<15)
    if curve.any(): out.append('  ..  curves: facet step median %.1f deg, %.0f%% over 6 deg; %d triangles'%(np.median(ang[curve]),100*np.mean(ang[curve]>6),len(t.faces)))
    print(name); print('\n'.join(out)); return not any(l.startswith('  !!') for l in out)
if __name__=='__main__':
    res=[check(f) for f in sorted(glob.glob(D+'*.stl'))]
    print('ALL CLEAN' if all(res) else 'PROBLEMS ABOVE (!!)')
