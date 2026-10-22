# The STLs in current/stl as they lie on a print bed, with the support a slicer would add drawn in (red), for
# the print preview (renderer: anim/printbed.html, PAGE=printbed.html OUTD=printbed node anim/stills_render.mjs).
import numpy as np, trimesh, json, base64, sys
sys.argv=[sys.argv[0]]
exec(open('print_check.py').read().split("if __name__=='__main__':")[0])
def b64(a,dt): return base64.b64encode(np.ascontiguousarray(a,dtype=dt).tobytes()).decode()
meshes=[]
def add(name,t,color,group,rough=0.6,metal=0.0,opacity=1.0,kind='std',smooth=True):
    if smooth: t=trimesh.graph.smooth_shade(t,angle=np.radians(30))
    meshes.append(dict(name=name,group=group,color=color,rough=rough,metal=metal,emissive=None,opacity=opacity,kind=kind,
        pos=b64(t.vertices,np.float32),nrm=b64(t.vertex_normals,np.float32),idx=b64(t.faces,np.uint32)))
def columns(t,P=0.4,LH=0.2):   # the support columns: from each unsupported cell down to the part or the bed
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
    cols=[]
    for k in range(1,len(zs)):
        sup=ndimage.binary_dilation(L[k-1],st,iterations=grow); un=L[k]&~sup
        if not un.any(): continue
        anch=L[k]&sup; ok=np.zeros_like(un)
        for ax in (0,1):
            A=un if ax==0 else un.T; N=anch if ax==0 else anch.T; O=np.zeros_like(A)
            for i in np.flatnonzero(A.any(1)):
                idx=np.flatnonzero(np.diff(np.r_[0,A[i].astype(int),0]))
                for s0,s1 in zip(idx[::2],idx[1::2]):
                    if s0>0 and s1<A.shape[1] and N[i][s0-1] and N[i][s1] and (s1-s0)*P<=25.0: O[i][s0:s1]=True
            ok|=O if ax==0 else O.T
        lab,n=ndimage.label(un&~ok,st)
        if n:
            edt=ndimage.distance_transform_edt(~anch)*P
            for c in range(1,n+1):
                comp=lab==c; ring=ndimage.binary_dilation(comp,st)&~comp
                if ring.sum() and (ring&anch).sum()/ring.sum()>=0.85 and edt[comp].max()<=12.5: ok|=comp
        need=un&~ok&~(ndimage.distance_transform_edt(~anch)*P<=2.0)
        for i,j in np.argwhere(need):
            below=np.flatnonzero(L[:k,i,j]); z0=zs[below[-1]]+LH/2 if len(below) else 0.0
            cols.append((xs[i],ys[j],z0,zs[k]-LH/2))
    if not cols: return None
    c=np.array(cols); n=len(c); h=P*0.42
    lo=np.c_[c[:,0]-h,c[:,1]-h,c[:,2]]; hi=np.c_[c[:,0]+h,c[:,1]+h,c[:,3]]
    corner=np.array([[0,0,0],[1,0,0],[1,1,0],[0,1,0],[0,0,1],[1,0,1],[1,1,1],[0,1,1]])
    V=(lo[:,None,:]+corner[None]*(hi-lo)[:,None,:]).reshape(-1,3)
    F0=np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]])
    F=(F0[None]+8*np.arange(n)[:,None,None]).reshape(-1,3)
    return trimesh.Trimesh(V,F,process=False)
PARTS=[('lamp62_housing','Housing: open top on the bed. Red = support (in the side bays and the LED window; none in the duct)','#2b2f35'),
       ('lamp62_top_plate','Top plate: top face on the bed, no support','#3a4048'),
       ('lamp62_lens_frame','Lens frame: front face on the bed, no support','#2b2f35'),
       ('lamp62_lid','Lid: flat, no support','#2b2f35'),
       ('master_handle_v17_usb_right','Handle: legs and grip flat, so every layer runs along them. Red = support from the bed, add a brim','#24272c'),
       ('master_handle_top_cap_p2','Top cap: flat side down','#24272c')]
TOZ=np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]],float)    # print frame (z up) -> renderer (y up)
frames=[]; Z=np.zeros(16).tolist()
for k,(f,cap,col) in enumerate(PARTS):
    t=trimesh.load('../current/stl/'+f+'.stl')
    add(f,t,col,f,0.7); add(f+'_ghost',t,'#9fb3c8',f+'_ghost',0.5,opacity=0.18,kind='glass',smooth=False)
    c=columns(t)
    if c is not None: add(f+'_sup',c,'#e8262d',f+'_sup',0.6,smooth=False)
    print(f,'support columns',0 if c is None else len(c.faces)//12)
bed=trimesh.creation.box([220,220,4]); bed.apply_translation([0,0,-2]); add('bed',bed,'#20242a','bed',0.9,smooth=False)
g=[]
for v in np.arange(-100,101,20):
    a=trimesh.creation.box([220,0.6,0.2]); a.apply_translation([0,v,0.1]); g.append(a)
    a=trimesh.creation.box([0.6,220,0.2]); a.apply_translation([v,0,0.1]); g.append(a)
add('grid',trimesh.util.concatenate(g),'#3d4450','bed',0.8,smooth=False)
def frame(cap,show,cam,tgt):
    m={'bed':TOZ.T.flatten().tolist()}
    for f,_,_ in PARTS:
        for suf in ('','_ghost','_sup'): m[f+suf]=TOZ.T.flatten().tolist() if (f+suf) in show else Z
    return dict(cap=cap,cut=False,m=m,cam=cam,tgt=tgt,night=False,beams=False,mark=False)
for f,cap,_ in PARTS:
    t=trimesh.load('../current/stl/'+f+'.stl'); e=t.extents; r=max(e)*1.0+40
    tgt=[0,e[2]*0.35,0]; cam=[-r*1.15,r*0.95,r*1.25]
    frames.append(frame(cap,{f},cam,tgt))
    if f in ('lamp62_housing','master_handle_v17_usb_right'):
        frames.append(frame(cap.split('.')[0]+': see-through, with the support a slicer adds',{f+'_ghost',f+'_sup'},cam,tgt))
frames.append(frame('Handle v17: a gusset under each lamp tab and a fillet over its root (tab shown from below as fitted)',
                    {'master_handle_v17_usb_right'},[-32.3,213.2,93.2],[62.0,53.5,52.1]))
open('anim/printbed_data.js','w').write('window.DATA='+json.dumps(dict(meshes=meshes,frames=frames))+';')
print('frames',len(frames))
