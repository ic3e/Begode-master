# Scene + views for the lamp v5.1 stills (three.js renderer in anim/stills.html).
import numpy as np, trimesh, json, base64
exec(open('build18.py').read())
def T(x=0,y=0,z=0): M=np.eye(4); M[:3,3]=[x,y,z]; return M
def Rz(d): c,s=np.cos(np.radians(d)),np.sin(np.radians(d)); M=np.eye(4); M[:2,:2]=[[c,-s],[s,c]]; return M
def Rx(d): c,s=np.cos(np.radians(d)),np.sin(np.radians(d)); M=np.eye(4); M[1:3,1:3]=[[c,-s],[s,c]]; return M
def b64(a,dt): return base64.b64encode(np.ascontiguousarray(a,dtype=dt).tobytes()).decode()
meshes=[]; allW=[]
def add(name,m,color,group,rough=0.6,metal=0.0,emissive=None,opacity=1.0,smooth=True,kind='std'):
    t=m if isinstance(m,trimesh.Trimesh) else to_tm(m)
    if group=='body' and name not in ('ground',): allW.append(t.vertices)
    if smooth: t=trimesh.graph.smooth_shade(t,angle=np.radians(35))
    meshes.append(dict(name=name,group=group,color=color,rough=rough,metal=metal,emissive=emissive,opacity=opacity,kind=kind,
        pos=b64(t.vertices,np.float32),nrm=b64(t.vertex_normals,np.float32),idx=b64(t.faces,np.uint32)))
BLACK='#1c1e22'
for i,(m,c) in enumerate(model3()):
    col={'#2b2d31':'#222428','#232427':'#1d1f22'}.get(c,c)
    near=m.vertices[:,2].mean()-ZC>30                     # parts on the camera side of the side views
    add(f'wheel{"R" if near else ""}{i}',m,col,'body',0.8)
handle=to_mf(trimesh.load(U+'euc_master_front_handle.stl'))+handle_adds3()
add('handle',handle,BLACK,'body',0.7); add('cap',trimesh.load(U+'euc_master_front_handle_p2.stl'),BLACK,'body',0.7)
add('housing',housing5(),'#16181b','body',0.75); add('lid',lid3(),'#16181b','body',0.75)
add('servo',H3(servo3()),'#2f6fd6','body',0.4)
add('drl',diffuser5(1)+diffuser5(-1),'#ffffff','body',0.3,emissive='#eef4ff')
add('window',window(),'#dfe9f2','body',0.03,0.0,opacity=0.16,smooth=False,kind='glass')
add('head',head3(),'#2a2d32','head',0.6)
add('heatsink',box(HU1_3-HS3_D,HU1_3,-HS3_H/2,HS3_H/2,-HS3_W/2,HS3_W/2),'#b9bec6','head',0.35,0.8)
add('lens',mf.Manifold.batch_boolean([cu(TIR2_D/2-0.5,HU0_3-0.5,HU0_3+1.6,w=w) for w in OPTIC_W],mf.OpType.Add),'#aab4bf','head',0.05,0.4,emissive='#fff1b8')
L=2200.0
for k,(w,a) in enumerate(zip(OPTIC_W,(14,4.5,14))):
    beam=mf.Manifold.cylinder(L,7.5,7.5+L*np.tan(np.radians(a)),64).rotate([0,-90,0]).translate([HU0_3-0.5,0,w])
    add(f'beam{k}',beam,'#fff3c4','head',emissive='#fff3c4',opacity=0.075 if a>10 else 0.11,smooth=False,kind='beam')
add('ground',box(-3500,1500,-6,0,-1500,1500),'#c4c9d0','ground',0.95)
W=np.vstack(allW)
Lv=np.vstack([to_tm(m).vertices for m in (housing5(),window(),lid3())])
def head_mat(B,a): return B@T(PX3,PY3,0)@Rz(a)@T(-PX3,-PY3,0)@T(PX3,PY3,ZC)
def on_ground(B): # lift so the lowest point of the wheel touches y=0 (the ground)
    y=(np.c_[W,np.ones(len(W))]@B.T)[:,1].min(); return T(0,-y,0)@B
stand=on_ground(np.eye(4))
front=on_ground(Rz(90))            # fallen forward, face down
side=on_ground(Rx(90))             # fallen onto the right side
def view(cap,B,cam,tgt,night=False,a=2.0,beams=False,cut=False):
    return dict(cap=cap,cut=cut,m={'body':np.asarray(B).T.flatten().round(4).tolist(),'head':head_mat(B,a).T.flatten().round(4).tolist(),'ground':np.eye(4).flatten().tolist()},
                cam=list(cam),tgt=list(tgt),night=night,beams=beams,mark=cut)
P=lambda B,p: (B@np.r_[p,1])[:3]
lampS=P(stand,[-62,0,ZC])
whole=P(stand,[60,-280,ZC])
# a red marker from the ground up to the lamp's nearest point, for the fallen-forward view
Lf=(np.c_[Lv,np.ones(len(Lv))]@front.T)[:,:3]; lp=Lf[Lf[:,1].argmin()]
add('gapmark',mf.Manifold.cylinder(lp[1],1.6,1.6,16).rotate([-90,0,0]).translate([lp[0],0,lp[2]+0]),'#e8262d','ground',0.4,emissive='#e8262d',smooth=False,kind='mark')
print('lamp lowest point when fallen forward: %.1f mm above the ground'%lp[1])
views=[view('Lamp v5.1 on the Master',stand,whole+np.array([-1500,520,1050]),whole+np.array([-40,40,0])),
       view('Flush in the stock opening, behind a clear window',stand,lampS+np.array([-420,170,330]),lampS+np.array([0,-55,0])),
       view('Night: three LEDs, levelled; running lights dimmed',stand,lampS+np.array([-520,120,-300]),lampS+np.array([-60,-50,0]),night=True,beams=True),
       view('Face: three optics, angled running-light lines, chin vent and road sensor below',stand,lampS+np.array([-330,25,0]),lampS+np.array([0,-18,0])),
       view('Fallen forward (near shell cut away): handle and shells take the ground, the lamp stays 25 mm clear',front,np.array([lp[0]+40,70,lp[2]+520]),np.array([lp[0]+40,30,lp[2]]),cut=True),
       view('Fallen onto its side: shell and pedal take it, the lamp stays 90 mm clear',side,P(side,[-60,-120,ZC])+np.array([-900,350,200]),P(side,[-60,-120,ZC])+np.array([0,-30,0]))]
open('anim/stills_data.js','w').write('window.DATA='+json.dumps(dict(meshes=meshes,frames=views))+';')
print('views',len(views),'meshes',len(meshes))
